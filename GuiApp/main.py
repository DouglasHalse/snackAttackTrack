from kivy.app import App
from kivy.core.window import Window
from kivy.modules import inspector
from kivy.lang import Builder

from widgets.customScreenManager import CustomScreenManager
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
from widgets.editUserScreen import EditUserScreen
from widgets.historyScreen import HistoryScreen
from widgets.editSnackScreen import EditSnackScreen
from database import createAllTables, closeDatabase

# Disable all the unused-import violations due to .kv files
# pylint: disable=unused-import
import widgets.uiElements.buttons
import widgets.uiElements.textInputs

# pylint: enable=unused-import

# Size of Raspberry pi touchscreen
Window.size = (800, 480)


class snackAttackTrackApp(App):
    def __init__(self):
        self.title = "Snack Attack Track"
        self.sm = None
        Window.bind(on_key_down=self._on_keyboard_down)
        super().__init__()

    def _on_keyboard_down(self, _, keycode, _1, _2, _3):
        # F12
        if keycode == 293:
            Window.screenshot(name=self.sm.current + ".png")
            # self.sm.export_to_png(self.sm.current + ".png")
            return True
        return False

    def build(self):
        Builder.load_file("kv/main.kv")
        createAllTables()
        self.sm = CustomScreenManager()
        self.sm.add_widget(SplashScreenWidget(name="splashScreen"))
        self.sm.add_widget(LoginScreen(name="loginScreen"))
        self.sm.add_widget(MainUserScreen(name="mainUserPage"))
        self.sm.add_widget(CreateUserScreen(name="createUserScreen"))
        self.sm.add_widget(AdminScreen(name="adminScreen"))
        self.sm.add_widget(EditSnacksScreen(name="editSnacksScreen"))
        self.sm.add_widget(EditUsersScreen(name="editUsersScreen"))
        self.sm.add_widget(AddSnackScreen(name="addSnackScreen"))
        self.sm.add_widget(TopUpAmountScreen(name="topUpAmountScreen"))
        self.sm.add_widget(TopUpPaymentScreen(name="topUpPaymentScreen"))
        self.sm.add_widget(BuyScreen(name="buyScreen"))
        self.sm.add_widget(EditUserScreen(name="editUserScreen"))
        self.sm.add_widget(HistoryScreen(name="historyScreen"))
        self.sm.add_widget(EditSnackScreen(name="editSnackScreen"))

        inspector.create_inspector(Window, self.sm)
        return self.sm

    def on_stop(self):
        closeDatabase()
        return super().on_stop()


if __name__ == "__main__":
    snackAttackTrackApp().run()
