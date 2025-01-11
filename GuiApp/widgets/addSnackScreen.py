from kivy.uix.gridlayout import GridLayout

from widgets.customScreenManager import CustomScreenManager
from widgets.headerBodyLayout import HeaderBodyScreen
from database import addSnack


class AddSnackScreenContent(GridLayout):
    def __init__(self, screenManager: CustomScreenManager, **kwargs):
        super().__init__(**kwargs)
        self.screenManager = screenManager
        self.ids["snackNameInput"].setInputChangedCallback(self.updateText)
        self.ids["snackQuantityInput"].setInputChangedCallback(self.updateText)
        self.ids["snackPriceInput"].setInputChangedCallback(self.updateText)

    def updateText(self, instance, text):
        # TODO sanitize input
        snackName = self.ids["snackNameInput"].getText()
        if snackName == "":
            snackName = "?"
        quantity = self.ids["snackQuantityInput"].getText()
        if quantity == "":
            quantity = "?"
        totalPrice = self.ids["snackPriceInput"].getText()
        pricePerItem = 0
        if totalPrice == "" or quantity == "?":
            totalPrice = "?"
        else:
            pricePerItem = float(totalPrice) / float(quantity)

        self.ids["numberOfItemsLabel"].text = f"{quantity} of {snackName}"
        self.ids["pricePerItemLabel"].text = f"{pricePerItem:.2f} credits per item"

    def onConfirm(self, *largs):
        # TODO sanitize input
        snackName = self.ids["snackNameInput"].getText()
        quantity = int(self.ids["snackQuantityInput"].getText())
        totalPrice = float(self.ids["snackPriceInput"].getText())
        pricePerItem = totalPrice / float(quantity)
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
        super().__init__(
            previousScreen="editSnacksScreen", enableSettingsButton=True, **kwargs
        )
        self.headerSuffix = "Add snack screen"

    def on_pre_enter(self, *args):
        super().on_pre_enter(*args)
        self.body.add_widget(AddSnackScreenContent(screenManager=self.manager))
