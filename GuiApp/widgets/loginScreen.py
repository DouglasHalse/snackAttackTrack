from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.widget import Widget
from database import getAllPatrons, addPatron


class BoxLayoutButton(ButtonBehavior, BoxLayout):
    pass


class LoginScreenUserWidget(BoxLayoutButton):
    def __init__(self, name: str,  loginScreenWidget, **kwargs):
        super(LoginScreenUserWidget, self).__init__(**kwargs)
        self.loginScreenWidget = loginScreenWidget
        self.userName = name
        self.ids['userNameLabel'].text = self.userName

    def Clicked(self, *largs):
        self.loginScreenWidget.UserSelected(self.userName)


class LoginScreenWidget(Screen):
    def __init__(self, **kwargs):
        super(LoginScreenWidget, self).__init__(**kwargs)
        self.AddUsersToLoginScreen()

    def AddUsersToLoginScreen(self):
        users = getAllPatrons()
        if users:
            self.ids['LoginScreenUserGridLayout'].add_widget(Widget()) # Spacer widget
            for user in users:
                firstName = user[1]
                self.ids['LoginScreenUserGridLayout'].add_widget(LoginScreenUserWidget(name=firstName, loginScreenWidget=self))
                self.ids['LoginScreenUserGridLayout'].add_widget(Widget()) # Spacer widget

    def clearUsersFromLoginScreen(self):
        self.ids['LoginScreenUserGridLayout'].clear_widgets()

    def createNewUserButtonClicked(self, *largs):
        print("Adding test user")
        addPatron("Test", "User", 100)
        self.clearUsersFromLoginScreen()
        self.AddUsersToLoginScreen()

    def UserSelected(self, userName, *largs):
        print("User selected: " + userName)
