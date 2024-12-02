from kivy.uix.screenmanager import Screen
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.behaviors import ButtonBehavior
from database import getPatronData, UserData


class BoxLayoutButton(ButtonBehavior, BoxLayout):
    pass


class AdminScreenHeader(GridLayout):
    def __init__(self, adminScreen, userData: UserData, **kwargs):
        super().__init__(**kwargs)
        self.mainUserScreen = adminScreen
        self.ids[
            "welcomeTextLabel"
        ].text = f"Welcome {userData.firstName} - admin screen"

    def onLogoutButtonPressed(self, *largs):
        self.mainUserScreen.logout()


class AdminScreenBody(GridLayout):
    def __init__(self, adminScreen, **kwargs):
        super().__init__(**kwargs)
        self.adminScreen = adminScreen

    def onEditSnacksButtonPressed(self, *largs):
        self.adminScreen.GoToEditSnacksScreen()

    def onEditUsersButtonPressed(self, *largs):
        self.adminScreen.GoToEditUsersScreen()


class AdminScreenWidget(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.userData = None

    def setUserId(self, userId: int):
        self.userData = getPatronData(userId)
        header = AdminScreenHeader(self, self.userData)
        self.ids["adminScreenGridLayout"].add_widget(header)
        body = AdminScreenBody(self)
        self.ids["adminScreenGridLayout"].add_widget(body)

    def GoToEditSnacksScreen(self):
        print("Going to edit snacks screen")
        # Use screen manager to go to edit snacks screen

    def GoToEditUsersScreen(self):
        print("Going to edit users screen")
        # Use screen manager to go to edit users screen

    def logout(self):
        self.ids["adminScreenGridLayout"].clear_widgets()
        self.manager.current = "splashScreen"
