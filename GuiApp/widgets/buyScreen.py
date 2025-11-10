from datetime import datetime
from enum import Enum

from database import SnackData
from snackReorderer import SnackReorderer
from widgets.GridLayoutScreen import GridLayoutScreen
from widgets.popups.creditsAnimationPopup import CreditsAnimationPopup
from widgets.popups.errorMessagePopup import ErrorMessagePopup
from widgets.popups.insufficientFundsPopup import InsufficientFundsPopup
from widgets.settingsManager import SettingName


class ItemLocation(Enum):
    INVENTORY = 0
    SHOPPINGCART = 1


class BuyScreen(GridLayoutScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.snackDict = {}
        self.snackStash = {}
        self.ids.header.bind(on_back_button_pressed=self.on_back_button_pressed)

    def on_back_button_pressed(self, *args):
        self.manager.transitionToScreen("mainUserPage", transitionDirection="right")

    def on_going_to_top_up_screen(self, *args):
        snacksInShoppingCart = self.getSnacksInShoppingCart()
        for snack in snacksInShoppingCart:
            self.snackStash[snack.snackId] = snack.quantity

        self.manager.top_up_requestee = "buyScreen"

    def pop_snack_stash(self):
        for snackId, quantity in self.snackStash.items():
            if snackId in self.snackDict:
                if quantity <= self.snackDict[snackId][ItemLocation.INVENTORY]:
                    self.snackDict[snackId][ItemLocation.INVENTORY] -= quantity
                    self.snackDict[snackId][ItemLocation.SHOPPINGCART] += quantity
                    self.updateSnackInLists(snackId=snackId)
                else:
                    self.snackDict[snackId][
                        ItemLocation.SHOPPINGCART
                    ] += self.snackDict[snackId][ItemLocation.INVENTORY]
                    self.snackDict[snackId][ItemLocation.INVENTORY] = 0
                    self.updateSnackInLists(snackId=snackId)
        self.snackStash = {}

    def on_pre_leave(self, *args):
        self.snackStash = {}
        return super().on_pre_leave(*args)

    def on_pre_enter(self, *args):
        self.initInventory()
        self.updateTotalPrice()
        return super().on_pre_enter(*args)

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
        snackData = self.manager.database.getSnack(snackId)

        if self.snackDict[snackId][ItemLocation.INVENTORY] == 0:
            self.ids.inventoryTable.removeEntry(entryIdentifier=snackId)
        elif self.ids.inventoryTable.hasEntry(entryIdentifier=snackId):
            self.ids.inventoryTable.updateEntry(
                entryIdentifier=snackId,
                newEntryContents=[
                    snackData.snackName,
                    str(self.snackDict[snackId][ItemLocation.INVENTORY]),
                    f"{snackData.pricePerItem:.2f}",
                ],
            )
        else:
            self.ids.inventoryTable.addEntry(
                entryContents=[
                    snackData.snackName,
                    str(self.snackDict[snackId][ItemLocation.INVENTORY]),
                    f"{snackData.pricePerItem:.2f}",
                ],
                entryIdentifier=snackId,
            )

        if self.snackDict[snackId][ItemLocation.SHOPPINGCART] == 0:
            self.ids.shoppingCartTable.removeEntry(entryIdentifier=snackId)
        elif self.ids.shoppingCartTable.hasEntry(entryIdentifier=snackId):
            self.ids.shoppingCartTable.updateEntry(
                entryIdentifier=snackId,
                newEntryContents=[
                    snackData.snackName,
                    str(self.snackDict[snackId][ItemLocation.SHOPPINGCART]),
                    f"{snackData.pricePerItem:.2f}",
                ],
            )
        else:
            self.ids.shoppingCartTable.addEntry(
                entryContents=[
                    snackData.snackName,
                    str(self.snackDict[snackId][ItemLocation.SHOPPINGCART]),
                    f"{snackData.pricePerItem:.2f}",
                ],
                entryIdentifier=snackId,
            )

    def initInventory(self):
        self.snackDict = {}
        snacks = self.manager.database.getAllSnacks()

        if self.manager.settingsManager.get_setting_value(
            settingName=SettingName.ORDER_INVENTORY_BY_MOST_PURCHASED
        ):
            mostPurchasedSnacks = self.manager.database.getMostPurchasedSnacksByPatron(
                patronId=self.manager.getCurrentPatron().patronId
            )

            SnackReorderer.reorder_snacks_based_on_guide_list(
                snacks_to_reorder=snacks, snack_guide_list=mostPurchasedSnacks
            )

        for snack in snacks:
            self.snackDict[snack.snackId] = {
                ItemLocation.INVENTORY: snack.quantity,
                ItemLocation.SHOPPINGCART: 0,
            }

        self.ids.inventoryTable.clearEntries()
        self.ids.shoppingCartTable.clearEntries()

        for snackDictEntry in self.snackDict.items():
            snackId = snackDictEntry[0]
            snack = self.manager.database.getSnack(snackId)
            snacksInInventory = snackDictEntry[1][ItemLocation.INVENTORY]

            self.ids.inventoryTable.addEntry(
                entryContents=[
                    snack.snackName,
                    str(snacksInInventory),
                    f"{snack.pricePerItem:.2f}",
                ],
                entryIdentifier=snackId,
            )

        if self.snackStash:
            self.pop_snack_stash()

    def updateTotalPrice(self):
        totalPrice = 0.0
        for snackDictEntry in self.snackDict.items():
            snackId = snackDictEntry[0]
            snack = self.manager.database.getSnack(snackId)
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
                snack = self.manager.database.getSnack(snackId)
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

        currentPatron = self.manager.getCurrentPatron()

        if totalPrice > currentPatron.totalCredits:
            creditsNeeded = totalPrice - currentPatron.totalCredits
            popup = InsufficientFundsPopup(
                screen_manager=self.manager, credits_needed=creditsNeeded
            )
            popup.bind(on_top_up_pressed=self.on_going_to_top_up_screen)
            popup.open()
            return

        #
        # Purchase validation passed
        #

        creditsBeforePurchase = currentPatron.totalCredits
        creditsAfterPurchase = creditsBeforePurchase - totalPrice

        # Update snack database
        for snack in snacksInShoppingCart:
            if snack.quantity == self.manager.database.getSnack(snack.snackId).quantity:
                self.manager.database.removeSnack(snackId=snack.snackId)
            else:
                self.manager.database.subtractSnackQuantity(
                    snackId=snack.snackId, quantity=snack.quantity
                )

        # Update transaction database
        self.manager.database.addPurchaseTransaction(
            patronID=currentPatron.patronId,
            amountBeforeTransaction=creditsBeforePurchase,
            amountAfterTransaction=creditsAfterPurchase,
            transactionDate=datetime.now(),
            transactionItems=snacksInShoppingCart,
        )

        # Update patron credits
        self.manager.database.subtractPatronCredits(
            patronID=currentPatron.patronId, creditsToSubtract=totalPrice
        )

        # Update current patron with new data
        self.manager.refreshCurrentPatron()

        CreditsAnimationPopup(
            title="Thank you for your purchase!",
            creditsBefore=creditsBeforePurchase,
            creditsAfter=creditsAfterPurchase,
        ).open()

        if self.manager.settingsManager.get_setting_value(
            settingName=SettingName.AUTO_LOGOUT_AFTER_PURCHASE
        ):
            self.manager.logout()
            self.manager.transitionToScreen("splashScreen", transitionDirection="right")
        else:
            self.manager.transitionToScreen("mainUserPage", transitionDirection="right")

    def onCancel(self):
        self.manager.transitionToScreen("mainUserPage", transitionDirection="right")
