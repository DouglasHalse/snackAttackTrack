from database import UserData, getAllPatrons, getPatronIdByCardId
from kivy.clock import Clock
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import Screen
from widgets.customScreenManager import CustomScreenManager
from widgets.popups.createUserOrLinkCardPopup import CreateUserOrLinkCardPopup
from widgets.settingsManager import SettingName


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

        return super().on_pre_enter(*args)

    def on_enter(self, *args):
        self.manager.RFIDReader.start(self.cardRead)
        return super().on_enter(*args)

    def on_pre_leave(self, *args):
        self.manager.RFIDReader.stop()
        return super().on_pre_leave(*args)

    def on_leave(self, *args):
        Clock.unschedule(self.goToSplashScreen)
        self.ids["LoginScreenUserGridLayout"].clear_widgets()
        return super().on_leave(*args)

    def cardRead(self, cardId, *args):
        patronId = getPatronIdByCardId(cardId=cardId)
        if patronId is None:
            CreateUserOrLinkCardPopup(
                screenManager=self.manager, readCard=cardId
            ).open()
            return

        self.manager.login(patronId)
        self.manager.transitionToScreen("mainUserPage")

    def goToSplashScreen(self, *args):
        self.manager.transitionToScreen("splashScreen", transitionDirection="right")

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
