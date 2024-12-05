from kivy.uix.screenmanager import Screen
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.behaviors import ButtonBehavior
from database import getPatronData, UserData, getAllSnacks, SnackData


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
        self.editSnacksList = EditSnackListWidget()
        self.add_widget(self.editSnacksList)
        self.adminScreen = adminScreen

    def onEditSnacksButtonPressed(self, *largs):
        self.adminScreen.GoToEditSnacksScreen()

    def onEditUsersButtonPressed(self, *largs):
        self.adminScreen.GoToEditUsersScreen()


class EditSnacksScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.userData = None
        self.header = None
        self.body = None

    def on_enter(self, *args):
        # self.clearSnacksList()
        # addSnack("banana", 10, "test")
        self.addSnacksFromDatabase()
        return super().on_enter(*args)

    # def clearSnacksList(self):
    # self.ids['editSnacksScrollView'].clear_widgets()

    def addSnacksFromDatabase(self):
        snacks = getAllSnacks()
        layout = GridLayout(
            cols=1, padding="10dp", spacing=10, size_hint_y=None
        )  # , width=500)
        for snack in snacks[1:3]:
            layout.add_widget(SnackEntry(addSnacksScreen=self, snackData=snack))
        layout.add_widget(AddSnackEntry(addSnacksScreen=self))
        self.body.editSnacksList.ids["editSnacksScrollView"].add_widget(layout)

    def setUserId(self, userId: int):
        self.userData = getPatronData(userId)
        self.header = EditSnacksScreenHeader(self, self.userData)
        self.ids["editSnacksGridLayout"].add_widget(self.header)
        self.body = EditSnacksScreenBody(self)
        self.ids["editSnacksGridLayout"].add_widget(self.body)

    def GoToAddSnackScreen(self):
        print("Going to add snack screen")
        # Use screen manager to go to edit snacks screen

    def GoToEditSnackScreen(self):
        print("Going to edit snack screen")
        # Use screen manager to go to edit snacks screen

    def logout(self):
        self.ids["editSnacksGridLayout"].clear_widgets()
        self.manager.current = "splashScreen"


class SnackEntry(BoxLayoutButton):
    def __init__(
        self, addSnacksScreen: EditSnacksScreen, snackData: SnackData, **kwargs
    ):
        super().__init__(**kwargs)
        self.addSnacksScreen = addSnacksScreen
        self.ids["snackNameLabel"].text = snackData.snackName
        self.ids["snackQuantityLabel"].text = str(snackData.quantity)
        self.ids["snackImageIdLabel"].text = str(snackData.imageID)

    def onPress(self, *largs):
        self.addSnacksScreen.GoToEditSnackScreen()


class AddSnackEntry(BoxLayoutButton):
    def __init__(self, addSnacksScreen: EditSnacksScreen, **kwargs):
        super().__init__(**kwargs)
        self.addSnacksScreen = addSnacksScreen

    def onPress(self, *largs):
        self.addSnacksScreen.GoToAddSnackScreen()


class EditSnackListWidget(GridLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
