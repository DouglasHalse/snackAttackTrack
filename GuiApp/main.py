from kivy.app import App
from kivy.core.window import Window
from kivy.modules import inspector
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager

from widgets.splashScreen import SplashScreenWidget
from widgets.loginScreen import LoginScreen
from widgets.mainUserScreen import MainUserScreen
from widgets.createUserScreen import CreateUserScreen
from widgets.adminScreen import AdminScreen
from widgets.editSnacksScreen import EditSnacksScreen
from widgets.editUsersScreen import EditUsersScreen
from widgets.addSnackScreen import AddSnackScreen
from widgets.topUpAmountScreen import TopUpAmountScreen
from widgets.topUpPaymentScreen import TopUpPaymentScreen
from widgets.buyScreen import BuyScreen
from database import createAllTables, closeDatabase, UserData, getPatronData

# Size of Raspberry pi touchscreen
Window.size = (800, 480)


class CustomScreenManager(ScreenManager):
    def __init__(self):
        super().__init__()
        self._currentPatron: UserData = None

    def login(self, patronId):
        self._currentPatron = getPatronData(patronID=patronId)

    def logout(self):
        self._currentPatron = None

    def getCurrentPatron(self) -> UserData:
        return self._currentPatron

    def refreshCurrentPatron(self):
        self._currentPatron = getPatronData(patronID=self._currentPatron.patronId)


class snackAttackTrackApp(App):
    def __init__(self):
        self.title = "Snack Attack Track"
        super().__init__()

    def build(self):
        Builder.load_file("kv/main.kv")
        createAllTables()
        sm = CustomScreenManager()
        sm.add_widget(SplashScreenWidget(name="splashScreen"))
        sm.add_widget(LoginScreen(name="loginScreen"))
        sm.add_widget(MainUserScreen(name="mainUserPage"))
        sm.add_widget(CreateUserScreen(name="createUserScreen"))
        sm.add_widget(AdminScreen(name="adminScreen"))
        sm.add_widget(EditSnacksScreen(name="editSnacksScreen"))
        sm.add_widget(EditUsersScreen(name="editUsersScreen"))
        sm.add_widget(AddSnackScreen(name="addSnackScreen"))
        sm.add_widget(TopUpAmountScreen(name="topUpAmountScreen"))
        sm.add_widget(TopUpPaymentScreen(name="topUpPaymentScreen"))
        sm.add_widget(BuyScreen(name="buyScreen"))

        inspector.create_inspector(Window, sm)
        return sm

    def on_stop(self):
        closeDatabase()
        return super().on_stop()


if __name__ == "__main__":
    snackAttackTrackApp().run()
