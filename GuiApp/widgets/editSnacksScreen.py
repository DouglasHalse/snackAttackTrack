from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.behaviors import ButtonBehavior
from database import getAllSnacks, SnackData
from widgets.customScreenManager import CustomScreenManager
from widgets.headerBodyLayout import HeaderBodyScreen


class BoxLayoutButton(ButtonBehavior, BoxLayout):
    pass


class EditSnacksScreenContent(GridLayout):
    def __init__(self, screenManager: CustomScreenManager, **kwargs):
        super().__init__(**kwargs)
        self.screenManager = screenManager
        self.addSnacksFromDatabase()

    def addSnacksFromDatabase(self):
        snacks = getAllSnacks()

        for snack in snacks:
            self.ids["editSnacksScrollViewLayout"].add_widget(
                SnackEntry(screenManager=self.screenManager, snackData=snack)
            )

        self.ids["editSnacksScrollViewLayout"].add_widget(
            AddSnackEntry(screenManager=self.screenManager)
        )


class EditSnacksScreen(HeaderBodyScreen):
    def __init__(self, **kwargs):
        super().__init__(previousScreen="adminScreen", **kwargs)
        self.headerSuffix = "Edit snacks screen"

    def on_pre_enter(self, *args):
        super().on_pre_enter(*args)
        self.body.add_widget(EditSnacksScreenContent(screenManager=self.manager))


class SnackEntry(BoxLayoutButton):
    def __init__(
        self, screenManager: CustomScreenManager, snackData: SnackData, **kwargs
    ):
        super().__init__(**kwargs)
        self.screenManager = screenManager
        self.snackData = snackData
        self.ids["snackNameLabel"].text = snackData.snackName
        self.ids["snackQuantityLabel"].text = str(snackData.quantity)
        self.ids["snackPriceLabel"].text = f"{snackData.pricePerItem:.2f}"
        self.ids["snackImageIdLabel"].text = str(snackData.imageID)

    def onPress(self, *largs):
        self.screenManager.setSnackToEdit(snackToEdit=self.snackData)
        self.screenManager.transitionToScreen("editSnackScreen")


class AddSnackEntry(BoxLayoutButton):
    def __init__(self, screenManager: CustomScreenManager, **kwargs):
        super().__init__(**kwargs)
        self.screenManager = screenManager

    def onPress(self, *largs):
        self.screenManager.transitionToScreen("addSnackScreen")
