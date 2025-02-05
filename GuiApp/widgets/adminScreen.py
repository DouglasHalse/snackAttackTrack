from kivy.uix.gridlayout import GridLayout

from widgets.customScreenManager import CustomScreenManager
from widgets.headerBodyLayout import HeaderBodyScreen


class AdminScreenContent(GridLayout):
    def __init__(self, screenManager: CustomScreenManager, **kwargs):
        super().__init__(**kwargs)
        self.screenManager = screenManager

    def onEditSystemSettingsButtonPressed(self, *largs):
        self.screenManager.transitionToScreen("editSystemSettingsScreen")

    def onEditSnacksButtonPressed(self, *largs):
        self.screenManager.transitionToScreen("editSnacksScreen")

    def onEditUsersButtonPressed(self, *largs):
        self.screenManager.transitionToScreen("editUsersScreen")
    
    def registerCardIdtoDataBase(self, *largs):
        self.screenManager.transitionToScreen("registerCardIdScreen")

class AdminScreen(HeaderBodyScreen):
    def __init__(self, **kwargs):
        super().__init__(previousScreen="mainUserPage", **kwargs)
        self.headerSuffix = "Admin screen"

    def on_pre_enter(self, *args):
        super().on_pre_enter(*args)
        self.body.add_widget(AdminScreenContent(screenManager=self.manager))
