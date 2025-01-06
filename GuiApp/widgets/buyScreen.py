from enum import Enum
from datetime import datetime
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.behaviors import ButtonBehavior
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


class ItemLocation(Enum):
    INVENTORY = 0
    SHOPPINGCART = 1


class BoxLayoutButton(ButtonBehavior, BoxLayout):
    pass


class SnackList(GridLayout):
    def __init__(self, heading: str, **kwargs):
        super().__init__(**kwargs)
        self.ids["snackListHeading"].text = heading


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

        self.snackListInventory = SnackList(heading="Inventory")
        self.snackListShoppingCart = SnackList(heading="Shopping Cart")

        self.ids["shoppingItemSelection"].add_widget(self.snackListInventory)
        self.ids["shoppingItemSelection"].add_widget(self.snackListShoppingCart)

        self.updateSnackLists()

    def updateSnackLists(self):
        inventoryLayout = GridLayout(
            cols=1, padding="10dp", spacing=10, size_hint_y=None
        )
        shoppingCartLayout = GridLayout(
            cols=1, padding="10dp", spacing=10, size_hint_y=None
        )

        for snackDictEntry in self.snackDict.items():
            snackId = snackDictEntry[0]
            snack = getSnack(snackId)
            snackInInventory = snackDictEntry[1][ItemLocation.INVENTORY]
            snackInShoppingCart = snackDictEntry[1][ItemLocation.SHOPPINGCART]

            if snackInInventory:
                inventoryLayout.add_widget(
                    SnackShoppingEntry(
                        buyScreenContent=self,
                        snackData=snack,
                        itemLocation=ItemLocation.INVENTORY,
                    )
                )
            if snackInShoppingCart:
                shoppingCartLayout.add_widget(
                    SnackShoppingEntry(
                        buyScreenContent=self,
                        snackData=snack,
                        itemLocation=ItemLocation.SHOPPINGCART,
                    )
                )

        self.snackListInventory.ids["snacksScrollView"].clear_widgets()
        self.snackListShoppingCart.ids["snacksScrollView"].clear_widgets()
        self.snackListInventory.ids["snacksScrollView"].add_widget(inventoryLayout)
        self.snackListShoppingCart.ids["snacksScrollView"].add_widget(
            shoppingCartLayout
        )

    def snackClicked(self, snackId: int, itemLocation: ItemLocation):
        if itemLocation == ItemLocation.INVENTORY:
            self.snackDict[snackId][ItemLocation.INVENTORY] -= 1
            self.snackDict[snackId][ItemLocation.SHOPPINGCART] += 1
        else:
            self.snackDict[snackId][ItemLocation.SHOPPINGCART] -= 1
            self.snackDict[snackId][ItemLocation.INVENTORY] += 1
        self.updateSnackLists()
        self.updateTotalPrice()

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
            snackId = snackDictEntry[0]
            snack = getSnack(snackId)
            snackPrice = snack.pricePerItem
            snackInShoppingCart = snackDictEntry[1][ItemLocation.SHOPPINGCART]
            snackBought = SnackData(
                snackId=snackId,
                snackName=snack.snackName,
                quantity=snackInShoppingCart,
                imageID=snack.imageID,
                pricePerItem=snackPrice,
            )
            snacksBought.append(snackBought)
            totalPrice += snackPrice * snackInShoppingCart
            if snackInShoppingCart > 0:
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


class SnackShoppingEntry(BoxLayoutButton):
    def __init__(
        self,
        buyScreenContent: BuyScreenContent,
        snackData: SnackData,
        itemLocation: ItemLocation,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.buyScreenContent = buyScreenContent
        self.snackData = snackData
        self.itemLocation = itemLocation
        self.ids["snackNameLabel"].text = self.snackData.snackName
        self.ids["snackQuantityLabel"].text = str(
            self.buyScreenContent.snackDict[self.snackData.snackId][self.itemLocation]
        )
        self.ids["snackPriceLabel"].text = f"{self.snackData.pricePerItem:.2f}"

    def onPress(self, *largs):
        self.buyScreenContent.snackClicked(
            snackId=self.snackData.snackId, itemLocation=self.itemLocation
        )
