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
from widgets.clickableTable import ClickableTable


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
            ["Snack name", "Quantity", "Price"],
            onEntryPressedCallback=self.itemClickedInInventory,
        )
        self.snackListShoppingCart = ClickableTable(
            ["Snack name", "Quantity", "Price"],
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

    def onBuy(self):
        # TODO: Verify enough items are in the database?
        # TODO: Verify user has enough credits
        totalPrice = 0.0
        snacksBought = []
        for snackDictEntry in self.snackDict.items():
            snackInShoppingCart = snackDictEntry[1][ItemLocation.SHOPPINGCART]
            # Skip snacks that are not in the shopping cart
            if snackInShoppingCart == 0:
                continue

            snackId = snackDictEntry[0]
            snack = getSnack(snackId)
            snackPrice = snack.pricePerItem

            snackBought = SnackData(
                snackId=snackId,
                snackName=snack.snackName,
                quantity=snackInShoppingCart,
                imageID=snack.imageID,
                pricePerItem=snackPrice,
            )
            snacksBought.append(snackBought)
            totalPrice += snackPrice * snackInShoppingCart
            if snackInShoppingCart == snack.quantity:
                removeSnack(snackId=snack.snackId)
            else:
                subtractSnackQuantity(
                    snackId=snack.snackId, quantity=snackInShoppingCart
                )

        currentPatron = self.screenManager.getCurrentPatron()
        patronsCreditsBeforePurchase = currentPatron.totalCredits
        patronsCreditsAfterPurchase = patronsCreditsBeforePurchase - totalPrice
        addPurchaseTransaction(
            patronID=currentPatron.patronId,
            amountBeforeTransaction=patronsCreditsBeforePurchase,
            amountAfterTransaction=patronsCreditsAfterPurchase,
            transactionDate=datetime.now(),
            transactionItems=snacksBought,
        )
        subtractPatronCredits(
            patronID=currentPatron.patronId, creditsToSubtract=totalPrice
        )

        # Update current patron with new data
        self.screenManager.refreshCurrentPatron()

        popup = PurchaseCompletedPopup(
            creditsBeforePurchase=patronsCreditsBeforePurchase,
            creditsAfterPurchase=patronsCreditsAfterPurchase,
        )
        popup.open()
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
