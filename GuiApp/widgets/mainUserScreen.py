from kivy.uix.screenmanager import ScreenManager
from kivy.uix.gridlayout import GridLayout
from widgets.headerBodyLayout import HeaderBodyScreen


class MainUserScreenContent(GridLayout):
    def __init__(self, screenManager: ScreenManager, **kwargs):
        super().__init__(**kwargs)
        self.screenManager = screenManager

    def onBuyButtonPressed(self):
        print("Going to Buy screen")
        # Use screen manager to go to buy screen

    def onTopUpButtonPressed(self):
        print("Going to Top up screen")
        # Use screen manager to go to buy screen

    def onHistoryButtonPressed(self):
        print("Going to History screen")
        # Use screen manager to go to buy screen


class MainUserScreen(HeaderBodyScreen):
    def __init__(self, **kwargs):
        super().__init__(enableSettingsButton=True, **kwargs)
        self.headerSuffix = "Main user screen"

    def on_enter(self, *args):
        super().on_enter(*args)
        self.body.add_widget(MainUserScreenContent(screenManager=self.manager))

    def GoToSettingsScreen(self):
        print("Going to Settings screen")
        # Use screen manager to go to settings screen
        adminScreen = self.manager.get_screen("adminScreen")
        adminScreen.setUserId(self.userData.patronId)
        self.manager.current = "adminScreen"

    def logout(self):
        self.ids["mainUserScreenGridLayout"].clear_widgets()
        self.manager.current = "splashScreen"
