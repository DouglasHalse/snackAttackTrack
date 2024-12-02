from kivy.uix.screenmanager import Screen
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.behaviors import ButtonBehavior
from database import getPatronData, UserData


class BoxLayoutButton(ButtonBehavior, BoxLayout):
    pass


class MainUserScreenHeader(GridLayout):
    def __init__(self, mainUserScreen, userData: UserData, **kwargs):
        super().__init__(**kwargs)
        self.mainUserScreen = mainUserScreen
        self.ids["welcomeTextLabel"].text = f"Welcome {userData.firstName}!"

    def onLogoutButtonPressed(self, *largs):
        self.mainUserScreen.logout()

    def OnWrenchPressed(self, *largs):
        self.mainUserScreen.GoToSettingsScreen()


class MainUserScreenBody(GridLayout):
    def __init__(self, mainUserScreen, **kwargs):
        super().__init__(**kwargs)
        self.mainUserScreen = mainUserScreen

    def onBuyButtonPressed(self, *largs):
        self.mainUserScreen.GoToBuyScreen()

    def onTopUpButtonPressed(self, *largs):
        self.mainUserScreen.GoToTopUpScreen()

    def onHistoryButtonPressed(self, *largs):
        self.mainUserScreen.GoToHistoryScreen()


class MainUserScreenWidget(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.userData = None

    def setUserId(self, userId: int):
        self.userData = getPatronData(userId)
        header = MainUserScreenHeader(self, self.userData)
        self.ids["mainUserScreenGridLayout"].add_widget(header)
        body = MainUserScreenBody(self)
        self.ids["mainUserScreenGridLayout"].add_widget(body)

    def GoToBuyScreen(self):
        print("Going to Buy screen")
        # Use screen manager to go to buy screen

    def GoToTopUpScreen(self):
        print("Going to Top up screen")
        # Use screen manager to go to buy screen

    def GoToHistoryScreen(self):
        print("Going to History screen")
        # Use screen manager to go to buy screen

    def GoToSettingsScreen(self):
        print("Going to Settings screen")
        # Use screen manager to go to settings screen
        self.ids["mainUserScreenGridLayout"].clear_widgets()
        adminScreen = self.manager.get_screen("adminScreen")
        adminScreen.setUserId(self.userData.patronId)
        self.manager.current = "adminScreen"

    def logout(self):
        self.ids["mainUserScreenGridLayout"].clear_widgets()
        self.manager.current = "splashScreen"
