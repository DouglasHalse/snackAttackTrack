from database import addSnack
from kivy.uix.gridlayout import GridLayout
from widgets.customScreenManager import CustomScreenManager
from widgets.headerBodyLayout import HeaderBodyScreen
from widgets.popups.errorMessagePopup import ErrorMessagePopup
from widgets.settingsManager import SettingName


class AddSnackScreenContent(GridLayout):
    def __init__(self, screenManager: CustomScreenManager, **kwargs):
        super().__init__(**kwargs)
        self.screenManager = screenManager
        self.ids["snackNameInput"].setInputChangedCallback(self.updateText)
        self.ids["snackQuantityInput"].setInputChangedCallback(self.updateText)
        self.ids["snackPriceInput"].setInputChangedCallback(self.updateText)

        purchaseFee = self.screenManager.settingsManager.get_setting_value(
            settingName=SettingName.PURCHASE_FEE
        )
        self.ids["purchaseFeeLabel"].text = f"including fee of {purchaseFee*100:.2f}%"

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

        purchaseFee = self.screenManager.settingsManager.get_setting_value(
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
            totalPrice = float(self.ids["snackPriceInput"].getText())
        except ValueError:
            ErrorMessagePopup(errorMessage="Price must be a number").open()
            return
        if totalPrice == 0 or totalPrice < 0:
            ErrorMessagePopup(errorMessage="Price cannot be 0 or negative").open()
            return

        purchaseFee = self.screenManager.settingsManager.get_setting_value(
            settingName=SettingName.PURCHASE_FEE
        )

        totalPrice *= 1 + purchaseFee

        pricePerItem = round(float(totalPrice) / float(quantity), 2)

        addSnack(
            itemName=snackName,
            quantity=quantity,
            imageID="None",
            pricePerItem=pricePerItem,
        )
        self.screenManager.transitionToScreen(
            "editSnacksScreen", transitionDirection="right"
        )

    def onCancel(self, *largs):
        self.screenManager.transitionToScreen(
            "editSnacksScreen", transitionDirection="right"
        )


class AddSnackScreen(HeaderBodyScreen):
    def __init__(self, **kwargs):
        super().__init__(previousScreen="editSnacksScreen", **kwargs)
        self.headerSuffix = "Add snack screen"

    def on_pre_enter(self, *args):
        super().on_pre_enter(*args)
        self.body.add_widget(AddSnackScreenContent(screenManager=self.manager))
