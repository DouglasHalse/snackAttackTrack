from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.widget import Widget
from database import getAllPatrons, UserData


class BoxLayoutButton(ButtonBehavior, BoxLayout):
    pass


class LoginScreenUserWidget(BoxLayoutButton):
    def __init__(self, userData: UserData, loginScreenWidget, **kwargs):
        super().__init__(**kwargs)
        self.loginScreenWidget = loginScreenWidget
        self.userData = userData
        self.ids["userNameLabel"].text = self.userData.firstName

    def Clicked(self, *largs):
        self.loginScreenWidget.UserSelected(self.userData.patronId)


class LoginScreenWidget(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.AddUsersToLoginScreen()

    def on_enter(self, *args):
        self.clearUsersFromLoginScreen()
        self.AddUsersToLoginScreen()
        return super().on_enter(*args)

    def AddUsersToLoginScreen(self):
        userDataList = getAllPatrons()
        if userDataList:
            self.ids["LoginScreenUserGridLayout"].add_widget(Widget())  # Spacer widget
            for userData in userDataList:
                self.ids["LoginScreenUserGridLayout"].add_widget(
                    LoginScreenUserWidget(userData=userData, loginScreenWidget=self)
                )
                self.ids["LoginScreenUserGridLayout"].add_widget(
                    Widget()
                )  # Spacer widget

    def clearUsersFromLoginScreen(self):
        self.ids["LoginScreenUserGridLayout"].clear_widgets()

    def createNewUserButtonClicked(self, *largs):
        print("Adding test user")
        self.manager.current = "createUserScreen"

    def UserSelected(self, userId, *largs):
        mainUserPage = self.manager.get_screen("mainUserPage")
        mainUserPage.setUserId(userId)
        self.manager.current = "mainUserPage"
