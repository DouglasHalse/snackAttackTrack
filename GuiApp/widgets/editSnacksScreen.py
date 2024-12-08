from kivy.uix.screenmanager import ScreenManager
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.behaviors import ButtonBehavior
from database import getAllSnacks, SnackData
from widgets.headerBodyLayout import HeaderBodyScreen


class BoxLayoutButton(ButtonBehavior, BoxLayout):
    pass


class EditSnacksScreenContent(GridLayout):
    def __init__(self, screenManager: ScreenManager, **kwargs):
        super().__init__(**kwargs)
        self.screenManager = screenManager
        self.addSnacksFromDatabase()

    def addSnacksFromDatabase(self):
        snacks = getAllSnacks()
        layout = GridLayout(cols=1, padding="10dp", spacing=10, size_hint_y=None)
        for snack in snacks:
            layout.add_widget(
                SnackEntry(screenManager=self.screenManager, snackData=snack)
            )
        layout.add_widget(AddSnackEntry(screenManager=self.screenManager))
        self.ids["editSnacksScrollView"].add_widget(layout)


class EditSnacksScreen(HeaderBodyScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.headerSuffix = "Edit snacks screen"

    def on_enter(self, *args):
        super().on_enter(*args)
        self.body.add_widget(EditSnacksScreenContent(screenManager=self.manager))


class SnackEntry(BoxLayoutButton):
    def __init__(self, screenManager: ScreenManager, snackData: SnackData, **kwargs):
        super().__init__(**kwargs)
        self.screenManager = screenManager
        self.ids["snackNameLabel"].text = snackData.snackName
        self.ids["snackQuantityLabel"].text = str(snackData.quantity)
        self.ids["snackPriceLabel"].text = f"{snackData.pricePerItem:.2f}"
        self.ids["snackImageIdLabel"].text = str(snackData.imageID)

    def onPress(self, *largs):
        print("Going to edit snack screen")
        # Use screen manager to go to edit snack screen


class AddSnackEntry(BoxLayoutButton):
    def __init__(self, screenManager: ScreenManager, **kwargs):
        super().__init__(**kwargs)
        self.screenManager = screenManager

    def onPress(self, *largs):
        self.screenManager.current = "addSnackScreen"
        # Use screen manager to go to add snack screen
