from enum import Enum
from datetime import datetime
from kivy.uix.gridlayout import GridLayout
from database import (
    getAllSnacks,
    SnackData,
    getSnack,
    removeSnack,
    subtractSnackQuantity,
    subtractPatronCredits,
    addPurchaseTransaction,
)
from widgets.customScreenManager import CustomScreenManager
from widgets.headerBodyLayout import HeaderBodyScreen
from widgets.popups.purchaseCompletedPopup import PurchaseCompletedPopup
from widgets.popups.errorMessagePopup import ErrorMessagePopup
from widgets.clickableTable import ClickableTable
from widgets.settingsManager import SettingName


class ItemLocation(Enum):
    INVENTORY = 0
    SHOPPINGCART = 1


class BuyScreenContent(GridLayout):
    def __init__(self, screenManager: CustomScreenManager, **kwargs):
        super().__init__(**kwargs)
        self.screenManager = screenManager
        self.snackDict = {}
        for snack in getAllSnacks():
            self.snackDict[snack.snackId] = {
                ItemLocation.INVENTORY: snack.quantity,
                ItemLocation.SHOPPINGCART: 0,
            }

        self.snackListInventory = ClickableTable(
            columns=["Snack name", "Quantity", "Price"],
            columnExamples=["Long snack name", "Quantity", "Price"],
            onEntryPressedCallback=self.itemClickedInInventory,
        )
        self.snackListShoppingCart = ClickableTable(
            columns=["Snack name", "Quantity", "Price"],
            columnExamples=["Long snack name", "Quantity", "Price"],
            onEntryPressedCallback=self.itemClickedInShoppingCart,
        )

        self.ids["inventoryItemSelection"].add_widget(self.snackListInventory)
        self.ids["shoppingCartItemSelection"].add_widget(self.snackListShoppingCart)

        self.updateSnackLists()

    def itemClickedInInventory(self, snackId: int):
        self.snackDict[snackId][ItemLocation.INVENTORY] -= 1
        self.snackDict[snackId][ItemLocation.SHOPPINGCART] += 1
        self.updateSnackLists()
        self.updateTotalPrice()

    def itemClickedInShoppingCart(self, snackId: int):
        self.snackDict[snackId][ItemLocation.SHOPPINGCART] -= 1
        self.snackDict[snackId][ItemLocation.INVENTORY] += 1
        self.updateSnackLists()
        self.updateTotalPrice()

    def updateSnackLists(self):
        self.snackListInventory.clearEntries()
        self.snackListShoppingCart.clearEntries()

        for snackDictEntry in self.snackDict.items():
            snackId = snackDictEntry[0]
            snack = getSnack(snackId)
            snackInInventory = snackDictEntry[1][ItemLocation.INVENTORY]
            snackInShoppingCart = snackDictEntry[1][ItemLocation.SHOPPINGCART]

            if snackInInventory:
                self.snackListInventory.addEntry(
                    entryContents=[
                        snack.snackName,
                        str(snackInInventory),
                        f"{snack.pricePerItem:.2f}",
                    ],
                    entryIdentifier=snackId,
                )
            if snackInShoppingCart:
                self.snackListShoppingCart.addEntry(
                    entryContents=[
                        snack.snackName,
                        str(snackInShoppingCart),
                        f"{snack.pricePerItem:.2f}",
                    ],
                    entryIdentifier=snackId,
                )

    def updateTotalPrice(self):
        totalPrice = 0.0
        for snackDictEntry in self.snackDict.items():
            snackId = snackDictEntry[0]
            snack = getSnack(snackId)
            snackPrice = snack.pricePerItem
            snackInShoppingCart = snackDictEntry[1][ItemLocation.SHOPPINGCART]
            totalPrice += snackPrice * snackInShoppingCart
        self.ids["totalPriceLabel"].text = f"Total price: {totalPrice:.2f} credits"

    def isShoppingCartEmpty(self):
        for snackDictEntry in self.snackDict.items():
            snackInShoppingCart = snackDictEntry[1][ItemLocation.SHOPPINGCART]
            if snackInShoppingCart > 0:
                return False
        return True

    def getSnacksInShoppingCart(self) -> list[SnackData]:
        snacksInShoppingCart = []
        for snackDictEntry in self.snackDict.items():
            snackInShoppingCart = snackDictEntry[1][ItemLocation.SHOPPINGCART]
            if snackInShoppingCart > 0:
                snackId = snackDictEntry[0]
                snack = getSnack(snackId)
                snackBought = SnackData(
                    snackId=snackId,
                    snackName=snack.snackName,
                    quantity=snackInShoppingCart,
                    imageID=snack.imageID,
                    pricePerItem=snack.pricePerItem,
                )
                snacksInShoppingCart.append(snackBought)
        return snacksInShoppingCart

    def getTotalPriceOfSnacks(self, snacks: list[SnackData]) -> float:
        totalPrice = 0.0
        for snack in snacks:
            totalPrice += snack.pricePerItem * snack.quantity
        return totalPrice

    def onBuy(self):
        if self.isShoppingCartEmpty():
            popup = ErrorMessagePopup(errorMessage="Shopping cart is empty")
            popup.open()
            return

        snacksInShoppingCart = self.getSnacksInShoppingCart()
        totalPrice = self.getTotalPriceOfSnacks(snacksInShoppingCart)

        currentPatron = self.screenManager.getCurrentPatron()

        if totalPrice > currentPatron.totalCredits:
            popup = ErrorMessagePopup(errorMessage="Not enough credits")
            popup.open()
            return

        #
        # Purchase validation passed
        #

        creditsBeforePurchase = currentPatron.totalCredits
        creditsAfterPurchase = creditsBeforePurchase - totalPrice

        # Update snack database
        for snack in snacksInShoppingCart:
            if snack.quantity == getSnack(snack.snackId).quantity:
                removeSnack(snackId=snack.snackId)
            else:
                subtractSnackQuantity(snackId=snack.snackId, quantity=snack.quantity)

        # Update transaction database
        addPurchaseTransaction(
            patronID=currentPatron.patronId,
            amountBeforeTransaction=creditsBeforePurchase,
            amountAfterTransaction=creditsAfterPurchase,
            transactionDate=datetime.now(),
            transactionItems=snacksInShoppingCart,
        )

        # Update patron credits
        subtractPatronCredits(
            patronID=currentPatron.patronId, creditsToSubtract=totalPrice
        )

        # Update current patron with new data
        self.screenManager.refreshCurrentPatron()

        PurchaseCompletedPopup(
            creditsBeforePurchase=creditsBeforePurchase,
            creditsAfterPurchase=creditsAfterPurchase,
        ).open()

        if self.screenManager.settingsManager.get_setting_value(
            settingName=SettingName.AUTO_LOGOUT_AFTER_PURCHASE
        ):
            self.screenManager.logout()
            self.screenManager.transitionToScreen(
                "splashScreen", transitionDirection="right"
            )
        else:
            self.screenManager.transitionToScreen(
                "mainUserPage", transitionDirection="right"
            )

    def onCancel(self):
        self.screenManager.transitionToScreen(
            "mainUserPage", transitionDirection="right"
        )


class BuyScreen(HeaderBodyScreen):
    def __init__(self, **kwargs):
        super().__init__(previousScreen="mainUserPage", **kwargs)
        self.headerSuffix = "Buy snacks screen"

    def on_pre_enter(self, *args):
        super().on_pre_enter(*args)
        self.body.add_widget(BuyScreenContent(screenManager=self.manager))
