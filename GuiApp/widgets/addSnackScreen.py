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
        self.ids.header.bind(on_back_button_pressed=self.on_back_button_pressed)

    def on_back_button_pressed(self, *args):
        self.manager.transitionToScreen("editSnacksScreen", transitionDirection="right")

    def on_pre_enter(self, *args):
        purchaseFee = self.manager.settingsManager.get_setting_value(
            settingName=SettingName.PURCHASE_FEE
        )
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

        purchaseFee = self.manager.settingsManager.get_setting_value(
            settingName=SettingName.PURCHASE_FEE
        )

        totalPrice *= 1 + purchaseFee

        pricePerItem = round(float(totalPrice) / float(quantity), 2)

        self.ids["numberOfItemsLabel"].text = f"{quantity} of {snackName}"
        self.ids["pricePerItemLabel"].text = f"{pricePerItem:.2f} credits per item"

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
            price = float(self.ids["snackPriceInput"].getText())
        except ValueError:
            ErrorMessagePopup(errorMessage="Price must be a number").open()
            return
        if price == 0 or price < 0:
            ErrorMessagePopup(errorMessage="Price cannot be 0 or negative").open()
            return

        purchaseFee = self.manager.settingsManager.get_setting_value(
            settingName=SettingName.PURCHASE_FEE
        )

        priceWithFee = price * (1 + purchaseFee)

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
            value=price,
            cost_per_item=pricePerItem,
        )
        self.manager.transitionToScreen("editSnacksScreen", transitionDirection="right")

    def onCancel(self, *largs):
        self.manager.transitionToScreen("editSnacksScreen", transitionDirection="right")
