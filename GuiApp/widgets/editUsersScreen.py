from kivy.uix.screenmanager import ScreenManager
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.behaviors import ButtonBehavior
from widgets.headerBodyLayout import HeaderBodyScreen

from database import getAllPatrons, UserData


class BoxLayoutButton(ButtonBehavior, BoxLayout):
    pass


class EditUsersScreenContent(GridLayout):
    def __init__(self, screenManager: ScreenManager, **kwargs):
        super().__init__(**kwargs)
        self.screenManager = screenManager
        self.addUsersFromDatabase()

    def addUsersFromDatabase(self):
        users = getAllPatrons()
        layout = GridLayout(cols=1, padding="10dp", spacing=10, size_hint_y=None)
        for user in users:
            layout.add_widget(
                UserEntry(screenManager=self.screenManager, userData=user)
            )
        self.ids["editUsersScrollView"].add_widget(layout)


class EditUsersScreen(HeaderBodyScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.headerSuffix = "Edit users screen"

    def on_pre_enter(self, *args):
        super().on_pre_enter(*args)
        self.body.add_widget(EditUsersScreenContent(screenManager=self.manager))


class UserEntry(BoxLayoutButton):
    def __init__(self, screenManager: ScreenManager, userData: UserData, **kwargs):
        super().__init__(**kwargs)
        self.screenManager = screenManager
        self.ids["userFirstNameLabel"].text = userData.firstName
        self.ids["userLastNameLabel"].text = userData.lastName
        self.ids["userIdLabel"].text = userData.employeeID
        self.ids["userTotalCreditsLabel"].text = str(userData.totalCredits)

    def onPress(self, *largs):
        print("Going to edit user screen")
