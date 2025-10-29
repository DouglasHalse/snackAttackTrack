from database import add_added_snack, addSnack
from widgets.GridLayoutScreen import GridLayoutScreen
from widgets.popups.errorMessagePopup import ErrorMessagePopup
from widgets.settingsManager import SettingName


class AddSnackScreen(GridLayoutScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.ids["snackNameInput"].setInputChangedCallback(self.updateText)
        self.ids["snackQuantityInput"].setInputChangedCallback(self.updateText)
        self.ids["snackPriceInput"].setInputChangedCallback(self.updateText)
        self.ids["snackFeeInput"].setInputChangedCallback(self.updateText)
        self.ids.header.bind(on_back_button_pressed=self.on_back_button_pressed)

    def on_back_button_pressed(self, *args):
        self.manager.transitionToScreen("editSnacksScreen", transitionDirection="right")

    def on_pre_enter(self, *args):
        purchaseFee = self.manager.settingsManager.get_setting_value(
            settingName=SettingName.PURCHASE_FEE
        )
        self.ids["snackFeeInput"].setText(f"{purchaseFee:.2f}")
        self.ids["purchaseFeeLabel"].text = f"including fee of {purchaseFee*100:.2f}%"

    def on_leave(self, *args):
        self.ids["snackNameInput"].setText("")
        self.ids["snackQuantityInput"].setText("")
        self.ids["snackPriceInput"].setText("")
        self.ids["numberOfItemsLabel"].text = "? of ?"
        self.ids["pricePerItemLabel"].text = "0.00 credits per item"
        return super().on_leave(*args)

    def updateText(self, instance, text):
        snackName = self.ids["snackNameInput"].getText()
        if snackName == "":
            snackName = "?"

        quantityText = self.ids["snackQuantityInput"].getText()
        try:
            quantity = int(quantityText)
        except ValueError:
            return

        totalPriceText = self.ids["snackPriceInput"].getText()
        try:
            totalPrice = float(totalPriceText)
        except ValueError:
            return

        purchaseFeeText = self.ids["snackFeeInput"].getText()
        try:
            purchaseFee = float(purchaseFeeText)
        except ValueError:
            purchaseFee = 0.0

        totalPrice *= 1 + purchaseFee

        if quantity == 0:
            return

        pricePerItem = round(float(totalPrice) / float(quantity), 2)

        self.ids["numberOfItemsLabel"].text = f"{quantity} of {snackName}"
        self.ids["pricePerItemLabel"].text = f"{pricePerItem:.2f} credits per item"
        self.ids["purchaseFeeLabel"].text = f"including fee of {purchaseFee*100:.2f}%"

    def onConfirm(self, *largs):
        snackName = self.ids["snackNameInput"].getText()
        if snackName == "":
            ErrorMessagePopup(errorMessage="Snack Name cannot be empty").open()
            return

        try:
            quantity = int(self.ids["snackQuantityInput"].getText())
        except ValueError:
            ErrorMessagePopup(errorMessage="Quantity must be a number").open()
            return
        if quantity == 0 or quantity < 0:
            ErrorMessagePopup(errorMessage="Quantity cannot be 0 or negative").open()
            return

        try:
            totalPrice = float(self.ids["snackPriceInput"].getText())
        except ValueError:
            ErrorMessagePopup(errorMessage="Price must be a number").open()
            return
        if totalPrice == 0 or totalPrice < 0:
            ErrorMessagePopup(errorMessage="Price cannot be 0 or negative").open()
            return

        try:
            purchaseFee = float(self.ids["snackFeeInput"].getText())
        except ValueError:
            purchaseFee = 0.0
        if purchaseFee < 0:
            ErrorMessagePopup(errorMessage="Fee cannot be negative").open()
            return

        priceWithFee = totalPrice * (1 + purchaseFee)

        pricePerItem = round(float(priceWithFee) / float(quantity), 2)

        addSnack(
            itemName=snackName,
            quantity=quantity,
            imageID="None",
            pricePerItem=pricePerItem,
        )
        add_added_snack(
            snack_name=snackName,
            quantity=quantity,
            value=totalPrice,
        )
        self.manager.transitionToScreen("editSnacksScreen", transitionDirection="right")

    def onCancel(self, *largs):
        self.manager.transitionToScreen("editSnacksScreen", transitionDirection="right")
