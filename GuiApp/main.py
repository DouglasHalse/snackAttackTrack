import argparse

# Disable all the unused-import violations due to .kv files
# pylint: disable=unused-import
import widgets.clickableTable
import widgets.uiElements.buttons
import widgets.uiElements.layouts
import widgets.uiElements.textInputs
from database import closeDatabase, createAllTables
from kivy.app import App
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.modules import inspector
from widgets.addSnackScreen import AddSnackScreen
from widgets.adminScreen import AdminScreen
from widgets.buyScreen import BuyScreen
from widgets.createUserScreen import CreateUserScreen
from widgets.customScreenManager import CustomScreenManager
from widgets.editSnackScreen import EditSnackScreen
from widgets.editSnacksScreen import EditSnacksScreen
from widgets.editSystemSettingsScreen import EditSystemSettingsScreen
from widgets.editUserScreen import EditUserScreen
from widgets.editUsersScreen import EditUsersScreen
from widgets.historyScreen import HistoryScreen
from widgets.linkCardScreen import LinkCardScreen
from widgets.loginScreen import LoginScreen
from widgets.mainUserScreen import MainUserScreen
from widgets.settingsManager import SettingDataType, SettingName, SettingsManager
from widgets.splashScreen import SplashScreenWidget
from widgets.topUpAmountScreen import TopUpAmountScreen
from widgets.topUpPaymentScreen import TopUpPaymentScreen

# pylint: enable=unused-import


class snackAttackTrackApp(App):
    def __init__(self, use_inspector=True):
        self.title = "Snack Attack Track"
        self.settingsManager = self.create_settings_manager()
        self.screenManager = CustomScreenManager(settingsManager=self.settingsManager)
        self.use_inspector = use_inspector
        Window.bind(on_key_down=self._on_keyboard_down)
        self.colors = {
            "background": (165 / 255, 231 / 255, 234 / 255, 1),
            "secondary_background": (8 / 255, 127 / 255, 140 / 255, 1),
            "button": (252 / 255, 172 / 255, 196 / 255, 1),
            "green_button": (92 / 255, 179 / 255, 56 / 255, 1),
            "yellow_button": (236 / 255, 232 / 255, 82 / 255, 1),
            "orange_button": (255 / 255, 193 / 255, 69 / 255, 1),
            "red_button": (251 / 255, 65 / 255, 65 / 255, 1),
        }
        super().__init__()

    def _on_keyboard_down(self, _, keycode, _1, _2, _3):
        # F12
        if keycode == 293:
            Window.screenshot(name=self.screenManager.current + ".png")
            return True
        # F11
        if keycode == 292:
            self.screenManager.RFIDReader.triggerFakeRead()
            return True
        # F10
        if keycode == 291:
            if Window.size == (1280, 800):
                Window.size = (800, 480)
            else:
                Window.size = (1280, 800)
            return True
        return False

    def create_settings_manager(self) -> SettingsManager:
        sm = SettingsManager("settings.json")

        sm.add_setting_if_undefined(
            settingName=SettingName.SPILL_FACTOR,
            default_value=1.05,
            datatype=SettingDataType.FLOAT,
            min_value=1.0,
            max_value=10.0,
        )

        sm.add_setting_if_undefined(
            settingName=SettingName.PURCHASE_FEE,
            default_value=0.05,
            datatype=SettingDataType.FLOAT,
            min_value=0.0,
            max_value=1.0,
        )

        sm.add_setting_if_undefined(
            settingName=SettingName.AUTO_LOGOUT_ON_IDLE_ENABLE,
            default_value=True,
            datatype=SettingDataType.BOOL,
            min_value=0,
            max_value=1,
        )

        sm.add_setting_if_undefined(
            settingName=SettingName.AUTO_LOGOUT_ON_IDLE_TIME,
            default_value=120.0,
            datatype=SettingDataType.FLOAT,
            min_value=20.0,
            max_value=600.0,
        )

        sm.add_setting_if_undefined(
            settingName=SettingName.AUTO_LOGOUT_AFTER_PURCHASE,
            default_value=False,
            datatype=SettingDataType.BOOL,
            min_value=0,
            max_value=1,
        )

        sm.add_setting_if_undefined(
            settingName=SettingName.PAYMENT_SWISH_NUMBER,
            default_value="0723071057",
            datatype=SettingDataType.STRING,
            min_value=0,
            max_value=0,
        )

        sm.add_setting_if_undefined(
            settingName=SettingName.GO_TO_SPLASH_SCREEN_ON_IDLE_ENABLE,
            default_value=True,
            datatype=SettingDataType.BOOL,
            min_value=0,
            max_value=1,
        )

        sm.add_setting_if_undefined(
            settingName=SettingName.GO_TO_SPLASH_SCREEN_ON_IDLE_TIME,
            default_value=10.0,
            datatype=SettingDataType.FLOAT,
            min_value=5.0,
            max_value=600.0,
        )

        sm.add_setting_if_undefined(
            settingName=SettingName.ORDER_INVENTORY_BY_MOST_PURCHASED,
            default_value=True,
            datatype=SettingDataType.BOOL,
            min_value=0,
            max_value=1,
        )

        return sm

    def build(self):
        Builder.load_file("kv/main.kv")
        createAllTables()
        self.screenManager.add_widget(SplashScreenWidget(name="splashScreen"))
        self.screenManager.add_widget(LoginScreen(name="loginScreen"))
        self.screenManager.add_widget(MainUserScreen(name="mainUserPage"))
        self.screenManager.add_widget(CreateUserScreen(name="createUserScreen"))
        self.screenManager.add_widget(AdminScreen(name="adminScreen"))
        self.screenManager.add_widget(EditSnacksScreen(name="editSnacksScreen"))
        self.screenManager.add_widget(EditUsersScreen(name="editUsersScreen"))
        self.screenManager.add_widget(AddSnackScreen(name="addSnackScreen"))
        self.screenManager.add_widget(TopUpAmountScreen(name="topUpAmountScreen"))
        self.screenManager.add_widget(TopUpPaymentScreen(name="topUpPaymentScreen"))
        self.screenManager.add_widget(BuyScreen(name="buyScreen"))
        self.screenManager.add_widget(EditUserScreen(name="editUserScreen"))
        self.screenManager.add_widget(HistoryScreen(name="historyScreen"))
        self.screenManager.add_widget(EditSnackScreen(name="editSnackScreen"))
        self.screenManager.add_widget(
            EditSystemSettingsScreen(name="editSystemSettingsScreen")
        )
        self.screenManager.add_widget(LinkCardScreen(name="linkCardScreen"))

        if self.use_inspector:
            inspector.create_inspector(Window, self.screenManager)
        return self.screenManager

    def on_stop(self):
        closeDatabase()
        return super().on_stop()


def main():
    parser = argparse.ArgumentParser(description="Snack Attack Track Application")
    parser.add_argument(
        "--no-inspector", action="store_true", help="Run the app without the inspector"
    )
    parser.add_argument(
        "--rotate-screen",
        type=int,
        choices=range(0, 361),
        default=0,
        help="Rotate the screen by an angle between 0 and 360 degrees",
    )
    parser.add_argument("--hide-cursor", action="store_true", help="Hide the cursor")

    args = parser.parse_args()

    # Size of Raspberry pi touchscreen
    Window.size = (800, 480)
    Window.rotation = args.rotate_screen
    Window.show_cursor = not args.hide_cursor

    if args.no_inspector:
        app = snackAttackTrackApp(use_inspector=False)
    else:
        app = snackAttackTrackApp(use_inspector=True)

    app.run()


if __name__ == "__main__":
    main()
