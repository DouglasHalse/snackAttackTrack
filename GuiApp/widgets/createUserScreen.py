from kivy.uix.screenmanager import Screen
from widgets.popups.errorMessagePopup import ErrorMessagePopup


class CreateUserScreen(Screen):
    def __init__(self, **kwargs):
        self.cardId = None
        self.update_event = None
        super().__init__(**kwargs)

    def registerUser(self):
        """Handle the registration logic."""
        firstName = self.ids.firstNameInput.getText()
        lastName = self.ids.lastNameInput.getText()
        cardId = self.ids.cardIdInput.getText()
        pin = self.ids.pinInput.getText()
        confirmPin = self.ids.confirmPinInput.getText()

        if firstName == "":
            ErrorMessagePopup(errorMessage="First Name cannot be empty").open()
            return

        if lastName == "":
            ErrorMessagePopup(errorMessage="Last Name cannot be empty").open()
            return

        if pin == "":
            ErrorMessagePopup(errorMessage="PIN is required for security").open()
            return

        if len(pin) != 4:
            ErrorMessagePopup(errorMessage="PIN must be exactly 4 digits").open()
            return

        if not pin.isdigit():
            ErrorMessagePopup(errorMessage="PIN must contain only numbers").open()
            return

        if pin != confirmPin:
            ErrorMessagePopup(errorMessage="PINs do not match").open()
            return

        existingPatronId = self.manager.database.getPatronIdByCardId(cardId)
        if existingPatronId and cardId != "":
            patronWithTheId = self.manager.database.getPatronData(existingPatronId)
            ErrorMessagePopup(
                errorMessage=f"Card ID is already used by {patronWithTheId.firstName}"
            ).open()
            self.ids.cardIdInput.setText("")
            return

        self.manager.database.addPatron(firstName, lastName, cardId, pin)

        self.manager.transitionToScreen("loginScreen", transitionDirection="right")

    def cancel(self):
        """Handle the cancel action."""
        self.manager.transitionToScreen("loginScreen", transitionDirection="right")

    def cardRead(self, cardId, *args):
        self.ids.cardIdInput.setText(str(cardId))

    def on_enter(self, *args):
        self.manager.RFIDReader.start(self.cardRead)
        return super().on_enter(*args)

    def on_pre_leave(self, *args):
        self.manager.RFIDReader.stop()
        return super().on_pre_leave(*args)

    def on_leave(self, *args):
        self.ids.firstNameInput.clearText()
        self.ids.lastNameInput.clearText()
        self.ids.cardIdInput.clearText()
        self.ids.pinInput.clearText()
        self.ids.confirmPinInput.clearText()
        return super().on_leave(*args)
