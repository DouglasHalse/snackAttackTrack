from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.widget import Widget

from widgets.customScreenManager import CustomScreenManager
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
        return super().on_enter(*args)

    def on_leave(self, *args):
        self.ids["LoginScreenUserGridLayout"].clear_widgets()

    def AddUsersToLoginScreen(self):
        userDataList = getAllPatrons()
        if userDataList:
            self.ids["LoginScreenUserGridLayout"].add_widget(Widget())  # Spacer widget
            for userData in userDataList:
                self.ids["LoginScreenUserGridLayout"].add_widget(
                    LoginScreenUserWidget(userData=userData, screenManager=self.manager)
                )
                self.ids["LoginScreenUserGridLayout"].add_widget(
                    Widget()
                )  # Spacer widget

    def createNewUserButtonClicked(self, *largs):
        self.manager.transitionToScreen("createUserScreen")
