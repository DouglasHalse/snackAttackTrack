from kivy.uix.screenmanager import Screen

from widgets.popups.errorMessagePopup import ErrorMessagePopup
from database import addPatron


class CreateUserScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def registerUser(self):
        """Handle the registration logic."""
        firstName = self.ids.firstNameInput.getText()
        lastName = self.ids.lastNameInput.getText()
        cardId = self.ids.cardIdInput.getText()

        if firstName == "":
            ErrorMessagePopup(errorMessage="First Name cannot be empty").open()
            return

        if lastName == "":
            ErrorMessagePopup(errorMessage="Last Name cannot be empty").open()
            return

        addPatron(firstName, lastName, cardId)

        self.manager.transitionToScreen("loginScreen", transitionDirection="right")

    def cancel(self):
        """Handle the cancel action."""
        self.manager.transitionToScreen("loginScreen", transitionDirection="right")

    def on_leave(self, *args):
        self.ids.firstNameInput.clearText()
        self.ids.lastNameInput.clearText()
        self.ids.cardIdInput.clearText()
        return super().on_leave(*args)
