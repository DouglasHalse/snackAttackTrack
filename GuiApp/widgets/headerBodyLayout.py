from kivy.uix.screenmanager import Screen
from kivy.uix.gridlayout import GridLayout
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.boxlayout import BoxLayout
from kivy.clock import Clock


from widgets.customScreenManager import CustomScreenManager
from widgets.settingsManager import SettingName


class BoxLayoutButton(ButtonBehavior, BoxLayout):
    pass


class Header(GridLayout):
    def __init__(
        self,
        screenManager: CustomScreenManager,
        enableSettingsButton: bool = False,
        previousScreen=None,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.screenManager: CustomScreenManager = screenManager
        self.currentPatron = self.screenManager.getCurrentPatron()
        self.ids["welcomeTextLabel"].text = f"Welcome {self.currentPatron.firstName}"
        if enableSettingsButton:
            self.ids["rightContent"].add_widget(
                SettingsButton(screenManager=self.screenManager)
            )
        if previousScreen:
            backButton = BackButton(
                previousScreen=previousScreen, screenManager=self.screenManager
            )
            self.ids["leftContent"].add_widget(backButton, index=1)

    def onLogoutButtonPressed(self, *largs):
        self.screenManager.transitionToScreen(
            "splashScreen", transitionDirection="right"
        )

    def setSuffix(self, suffix: str):
        self.ids["welcomeTextLabel"].text += " - " + suffix


class Body(GridLayout):
    def __init__(self, screenManager: CustomScreenManager, **kwargs):
        super().__init__(**kwargs)
        self.screenManager = screenManager


class BackButton(BoxLayoutButton):
    def __init__(self, previousScreen, screenManager: CustomScreenManager, **kwargs):
        super().__init__(**kwargs)
        self.previousScreen = previousScreen
        self.screenManager: CustomScreenManager = screenManager

    def onPressed(self, *largs):
        self.screenManager.transitionToScreen(
            self.previousScreen, transitionDirection="right"
        )


class SettingsButton(BoxLayoutButton):
    def __init__(self, screenManager: CustomScreenManager, **kwargs):
        super().__init__(**kwargs)
        self.screenManager = screenManager

    def onPressed(self, *largs):
        self.screenManager.transitionToScreen("adminScreen")


class HeaderBodyScreen(Screen):
    header: Header
    body: Body

    def __init__(
        self, enableSettingsButton: bool = False, previousScreen=None, **kwargs
    ):
        super().__init__(**kwargs)
        self.enableSettingsButton = enableSettingsButton
        self.previousScreen = previousScreen
        self.headerSuffix = None
        self.header = None
        self.body = None

    def on_pre_enter(self, *args):
        super().on_pre_enter(*args)
        self.header = Header(
            screenManager=self.manager,
            enableSettingsButton=self.enableSettingsButton,
            previousScreen=self.previousScreen,
        )
        if self.headerSuffix:
            self.header.setSuffix(self.headerSuffix)
        self.ids["screenLayout"].add_widget(self.header)

        self.body = Body(screenManager=self.manager)
        self.ids["screenLayout"].add_widget(self.body)

        if self.manager.settingsManager.get_setting_value(
            settingName=SettingName.AUTO_LOGOUT_ON_IDLE_ENABLE
        ):
            timeToAutoLogout = self.manager.settingsManager.get_setting_value(
                settingName=SettingName.AUTO_LOGOUT_ON_IDLE_TIME
            )
            Clock.schedule_once(self.autoLogout, timeToAutoLogout)

    def autoLogout(self, *args):
        self.manager.logout()
        self.manager.transitionToScreen("splashScreen", transitionDirection="right")

    def on_leave(self, *args):
        self.ids["screenLayout"].clear_widgets()
        return super().on_leave(*args)

    def on_touch_down(self, touch):
        # Reset auto logout timer
        if self.manager.settingsManager.get_setting_value(
            settingName=SettingName.AUTO_LOGOUT_ON_IDLE_ENABLE
        ):
            timeToAutoLogout = self.manager.settingsManager.get_setting_value(
                settingName=SettingName.AUTO_LOGOUT_ON_IDLE_TIME
            )
            Clock.unschedule(self.autoLogout)
            Clock.schedule_once(self.autoLogout, timeToAutoLogout)
        return super().on_touch_down(touch)
