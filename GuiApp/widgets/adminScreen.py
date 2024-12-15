from kivy.uix.screenmanager import ScreenManager
from kivy.uix.gridlayout import GridLayout
from widgets.headerBodyLayout import HeaderBodyScreen


class AdminScreenContent(GridLayout):
    def __init__(self, screenManager: ScreenManager, **kwargs):
        super().__init__(**kwargs)
        self.screenManager = screenManager

    def onEditSnacksButtonPressed(self, *largs):
        self.screenManager.current = "editSnacksScreen"

    def onEditUsersButtonPressed(self, *largs):
        self.screenManager.current = "editUsersScreen"


class AdminScreen(HeaderBodyScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.headerSuffix = "Admin screen"

    def on_pre_enter(self, *args):
        super().on_pre_enter(*args)
        self.body.add_widget(AdminScreenContent(screenManager=self.manager))
