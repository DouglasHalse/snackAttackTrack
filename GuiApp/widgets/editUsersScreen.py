from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.behaviors import ButtonBehavior
from widgets.customScreenManager import CustomScreenManager
from widgets.headerBodyLayout import HeaderBodyScreen

from database import getAllPatrons, UserData


class BoxLayoutButton(ButtonBehavior, BoxLayout):
    pass


class EditUsersScreenContent(GridLayout):
    def __init__(self, screenManager: CustomScreenManager, **kwargs):
        super().__init__(**kwargs)
        self.screenManager = screenManager
        self.addUsersFromDatabase()

    def addUsersFromDatabase(self):
        users = getAllPatrons()
        for user in users:
            self.ids["editUsersScrollViewLayout"].add_widget(
                UserEntry(screenManager=self.screenManager, patronData=user)
            )


class EditUsersScreen(HeaderBodyScreen):
    def __init__(self, **kwargs):
        super().__init__(previousScreen="adminScreen", **kwargs)
        self.headerSuffix = "Edit users screen"

    def on_pre_enter(self, *args):
        super().on_pre_enter(*args)
        self.body.add_widget(EditUsersScreenContent(screenManager=self.manager))


class UserEntry(BoxLayoutButton):
    def __init__(
        self, screenManager: CustomScreenManager, patronData: UserData, **kwargs
    ):
        super().__init__(**kwargs)
        self.screenManager = screenManager
        self.patronData = patronData
        self.ids["userFirstNameLabel"].text = patronData.firstName
        self.ids["userLastNameLabel"].text = patronData.lastName
        self.ids["userIdLabel"].text = patronData.employeeID
        self.ids["userTotalCreditsLabel"].text = f"{patronData.totalCredits:.2f}"

    def onPress(self, *largs):
        self.screenManager.setPatronToEdit(patronToEdit=self.patronData)
        self.screenManager.transitionToScreen("editUserScreen")
