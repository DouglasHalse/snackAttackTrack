from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.behaviors import ButtonBehavior
from kivy.clock import Clock

from widgets.customScreenManager import CustomScreenManager
from widgets.settingsManager import SettingName
from database import getAllPatrons, UserData


class BoxLayoutButton(ButtonBehavior, BoxLayout):
    pass


class LoginScreenUserWidget(BoxLayoutButton):
    def __init__(
        self, userData: UserData, screenManager: CustomScreenManager, **kwargs
    ):
        super().__init__(**kwargs)
        self.screenManager = screenManager
        self.userData = userData
        self.ids["userNameLabel"].text = self.userData.firstName

    def Clicked(self, *largs):
        self.screenManager.login(self.userData.patronId)
        self.screenManager.transitionToScreen("mainUserPage")


class LoginScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def on_pre_enter(self, *args):
        self.AddUsersToLoginScreen()
        self.ids["scrollView"].scroll_x = 0.5

        if self.manager.settingsManager.get_setting_value(
            settingName=SettingName.GO_TO_SPLASH_SCREEN_ON_IDLE_ENABLE
        ):
            Clock.schedule_once(
                self.goToSplashScreen,
                self.manager.settingsManager.get_setting_value(
                    settingName=SettingName.GO_TO_SPLASH_SCREEN_ON_IDLE_TIME
                ),
            )

        return super().on_enter(*args)

    def goToSplashScreen(self, *args):
        self.manager.transitionToScreen("splashScreen", transitionDirection="right")

    def on_leave(self, *args):
        Clock.unschedule(self.goToSplashScreen)
        self.ids["LoginScreenUserGridLayout"].clear_widgets()

    def on_touch_down(self, touch):
        # Reset timer for returning to splash screen
        if self.manager.settingsManager.get_setting_value(
            settingName=SettingName.GO_TO_SPLASH_SCREEN_ON_IDLE_ENABLE
        ):
            timeToAutoLogout = self.manager.settingsManager.get_setting_value(
                settingName=SettingName.GO_TO_SPLASH_SCREEN_ON_IDLE_TIME
            )
            Clock.unschedule(self.goToSplashScreen)
            Clock.schedule_once(self.goToSplashScreen, timeToAutoLogout)
        return super().on_touch_down(touch)

    def AddUsersToLoginScreen(self):
        userDataList = getAllPatrons()
        if userDataList:
            for userData in userDataList:
                self.ids["LoginScreenUserGridLayout"].add_widget(
                    LoginScreenUserWidget(userData=userData, screenManager=self.manager)
                )

    def createNewUserButtonClicked(self, *largs):
        self.manager.transitionToScreen("createUserScreen")
