from kivy.uix.screenmanager import ScreenManager
from kivy.uix.gridlayout import GridLayout
from widgets.headerBodyLayout import HeaderBodyScreen
from database import addSnack


class AddSnackScreenContent(GridLayout):
    def __init__(self, screenManager: ScreenManager, **kwargs):
        super().__init__(**kwargs)
        self.screenManager = screenManager
        self.ids["snackNameTextInput"].bind(text=self.updateText)
        self.ids["snackQuantityTextInput"].bind(text=self.updateText)
        self.ids["snackTotalPriceTextInput"].bind(text=self.updateText)

    def updateText(self, instance, text):
        # TODO sanitize input
        snackName = self.ids["snackNameTextInput"].text
        if snackName == "":
            snackName = "?"
        quantity = self.ids["snackQuantityTextInput"].text
        if quantity == "":
            quantity = "?"
        totalPrice = self.ids["snackTotalPriceTextInput"].text
        pricePerItem = 0
        if totalPrice == "" or quantity == "?":
            totalPrice = "?"
        else:
            pricePerItem = float(totalPrice) / float(quantity)

        self.ids["numberOfItemsLabel"].text = f"{quantity} of {snackName}"
        self.ids["pricePerItemLabel"].text = f"{pricePerItem:.2f} credits per item"

    def onConfirm(self, *largs):
        # TODO sanitize input
        snackName = self.ids["snackNameTextInput"].text
        quantity = int(self.ids["snackQuantityTextInput"].text)
        totalPrice = float(self.ids["snackTotalPriceTextInput"].text)
        pricePerItem = totalPrice / float(quantity)
        addSnack(
            itemName=snackName,
            quantity=quantity,
            imageID="None",
            pricePerItem=pricePerItem,
        )
        self.screenManager.current = "editSnacksScreen"

    def onCancel(self, *largs):
        self.screenManager.current = "editSnacksScreen"


class AddSnackScreen(HeaderBodyScreen):
    def __init__(self, **kwargs):
        super().__init__(enableSettingsButton=True, **kwargs)
        self.headerSuffix = "Add snack screen"

    def on_enter(self, *args):
        super().on_enter(*args)
        self.body.add_widget(AddSnackScreenContent(screenManager=self.manager))
