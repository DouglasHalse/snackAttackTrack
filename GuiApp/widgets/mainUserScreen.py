from kivy.uix.screenmanager import ScreenManager
from kivy.uix.gridlayout import GridLayout
from widgets.headerBodyLayout import HeaderBodyScreen


class MainUserScreenContent(GridLayout):
    def __init__(self, screenManager: ScreenManager, **kwargs):
        super().__init__(**kwargs)
        self.screenManager = screenManager

    def onBuyButtonPressed(self):
        self.screenManager.current = "buyScreen"

    def onTopUpButtonPressed(self):
        self.screenManager.current = "topUpAmountScreen"

    def onHistoryButtonPressed(self):
        print("Going to History screen")
        # Use screen manager to go to buy screen


class MainUserScreen(HeaderBodyScreen):
    def __init__(self, **kwargs):
        super().__init__(enableSettingsButton=True, **kwargs)
        self.headerSuffix = "Main user screen"

    def on_pre_enter(self, *args):
        super().on_pre_enter(*args)
        self.body.add_widget(MainUserScreenContent(screenManager=self.manager))
