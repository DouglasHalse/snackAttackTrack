from kivy.uix.screenmanager import Screen
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.behaviors import ButtonBehavior
from database import getPatronData, UserData, getAllSnacks


class BoxLayoutButton(ButtonBehavior, BoxLayout):
    pass


class EditSnacksScreenHeader(GridLayout):
    def __init__(self, adminScreen, userData: UserData, **kwargs):
        super().__init__(**kwargs)
        self.mainUserScreen = adminScreen
        self.ids[
            "welcomeTextLabel"
        ].text = f"Welcome {userData.firstName} - edit snacks"

    def onLogoutButtonPressed(self, *largs):
        self.mainUserScreen.logout()


class EditSnacksScreenBody(GridLayout):
    def __init__(self, adminScreen, **kwargs):
        super().__init__(**kwargs)
        self.adminScreen = adminScreen

    def onEditSnacksButtonPressed(self, *largs):
        self.adminScreen.GoToEditSnacksScreen()

    def onEditUsersButtonPressed(self, *largs):
        self.adminScreen.GoToEditUsersScreen()


class SnackEntry(GridLayout):
    def __init__(self, snackName, **kwargs):
        super().__init__(**kwargs)
        self.ids["snackNameLabel"].text = snackName


class EditSnacksScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.userData = None
        self.header = None
        self.body = None

    def on_enter(self, *args):
        # self.clearSnacksList()
        self.addSnacksFromDatabase()
        return super().on_enter(*args)

    # def clearSnacksList(self):
    # self.ids['editSnacksScrollView'].clear_widgets()

    def addSnacksFromDatabase(self):
        snacks = getAllSnacks()
        layout = GridLayout(cols=1, padding=10, spacing=10, size_hint=(1, 1), width=500)
        for snack in snacks:
            layout.add_widget(SnackEntry(snack.itemName))
        self.body.ids["editSnacksScrollView"].add_widget(layout)

    def setUserId(self, userId: int):
        self.userData = getPatronData(userId)
        self.header = EditSnacksScreenHeader(self, self.userData)
        self.ids["editSnacksGridLayout"].add_widget(self.header)
        self.body = EditSnacksScreenBody(self)
        self.ids["editSnacksGridLayout"].add_widget(self.body)

    def GoToEditSnacksScreen(self):
        print("Going to edit snacks screen")
        # Use screen manager to go to edit snacks screen

    def GoToEditUsersScreen(self):
        print("Going to edit users screen")
        # Use screen manager to go to edit users screen

    def logout(self):
        self.ids["editSnacksGridLayout"].clear_widgets()
        self.manager.current = "splashScreen"
