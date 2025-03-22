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
    getMostPurchasedSnacksByPatron,
)
from widgets.customScreenManager import CustomScreenManager
from widgets.headerBodyLayout import HeaderBodyScreen
from widgets.popups.creditsAnimationPopup import CreditsAnimationPopup
from widgets.popups.errorMessagePopup import ErrorMessagePopup
from widgets.popups.insufficientFundsPopup import InsufficientFundsPopup
from widgets.clickableTable import ClickableTable
from widgets.settingsManager import SettingName
from snackReorderer import SnackReorderer


class ItemLocation(Enum):
    INVENTORY = 0
    SHOPPINGCART = 1


class BuyScreenContent(GridLayout):
    def __init__(self, screenManager: CustomScreenManager, **kwargs):
        super().__init__(**kwargs)
        self.screenManager = screenManager
        self.snackDict = {}

        self.snackListInventory = ClickableTable(
            columns=["Snack name", "Quantity", "Price"],
            columnExamples=["Long snack name", "30", "15.00"],
            onEntryPressedCallback=self.itemClickedInInventory,
        )
        self.snackListShoppingCart = ClickableTable(
            columns=["Snack name", "Quantity", "Price"],
            columnExamples=["Long snack name", "30", "15.00"],
            onEntryPressedCallback=self.itemClickedInShoppingCart,
        )

        self.ids["inventoryItemSelection"].add_widget(self.snackListInventory)
        self.ids["shoppingCartItemSelection"].add_widget(self.snackListShoppingCart)

        self.initInventory()

    def itemClickedInInventory(self, snackId: int):
        self.snackDict[snackId][ItemLocation.INVENTORY] -= 1
        self.snackDict[snackId][ItemLocation.SHOPPINGCART] += 1
        self.updateSnackInLists(snackId=snackId)
        self.updateTotalPrice()

    def itemClickedInShoppingCart(self, snackId: int):
        self.snackDict[snackId][ItemLocation.SHOPPINGCART] -= 1
        self.snackDict[snackId][ItemLocation.INVENTORY] += 1
        self.updateSnackInLists(snackId=snackId)
        self.updateTotalPrice()

    def updateSnackInLists(self, snackId: int):
        snackData = getSnack(snackId)

        if self.snackDict[snackId][ItemLocation.INVENTORY] == 0:
            self.snackListInventory.removeEntry(entryIdentifier=snackId)
        elif self.snackListInventory.hasEntry(entryIdentifier=snackId):
            self.snackListInventory.updateEntry(
                entryIdentifier=snackId,
                newEntryContents=[
                    snackData.snackName,
                    str(self.snackDict[snackId][ItemLocation.INVENTORY]),
                    f"{snackData.pricePerItem:.2f}",
                ],
            )
        else:
            self.snackListInventory.addEntry(
                entryContents=[
                    snackData.snackName,
                    str(self.snackDict[snackId][ItemLocation.INVENTORY]),
                    f"{snackData.pricePerItem:.2f}",
                ],
                entryIdentifier=snackId,
            )

        if self.snackDict[snackId][ItemLocation.SHOPPINGCART] == 0:
            self.snackListShoppingCart.removeEntry(entryIdentifier=snackId)
        elif self.snackListShoppingCart.hasEntry(entryIdentifier=snackId):
            self.snackListShoppingCart.updateEntry(
                entryIdentifier=snackId,
                newEntryContents=[
                    snackData.snackName,
                    str(self.snackDict[snackId][ItemLocation.SHOPPINGCART]),
                    f"{snackData.pricePerItem:.2f}",
                ],
            )
        else:
            self.snackListShoppingCart.addEntry(
                entryContents=[
                    snackData.snackName,
                    str(self.snackDict[snackId][ItemLocation.SHOPPINGCART]),
                    f"{snackData.pricePerItem:.2f}",
                ],
                entryIdentifier=snackId,
            )

    def initInventory(self):
        snacks = getAllSnacks()

        if self.screenManager.settingsManager.get_setting_value(
            settingName=SettingName.ORDER_INVENTORY_BY_MOST_PURCHASED
        ):
            mostPurchasedSnacks = getMostPurchasedSnacksByPatron(
                patronId=self.screenManager.getCurrentPatron().patronId
            )

            SnackReorderer.reorder_snacks_based_on_guide_list(
                snacks_to_reorder=snacks, snack_guide_list=mostPurchasedSnacks
            )

        for snack in snacks:
            self.snackDict[snack.snackId] = {
                ItemLocation.INVENTORY: snack.quantity,
                ItemLocation.SHOPPINGCART: 0,
            }

        self.snackListInventory.clearEntries()
        self.snackListShoppingCart.clearEntries()

        for snackDictEntry in self.snackDict.items():
            snackId = snackDictEntry[0]
            snack = getSnack(snackId)
            snacksInInventory = snackDictEntry[1][ItemLocation.INVENTORY]

            self.snackListInventory.addEntry(
                entryContents=[
                    snack.snackName,
                    str(snacksInInventory),
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
            popup = InsufficientFundsPopup(screenManager=self.screenManager)
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

        CreditsAnimationPopup(
            title="Thank you for your purchase!",
            creditsBefore=creditsBeforePurchase,
            creditsAfter=creditsAfterPurchase,
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
