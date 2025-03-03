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

        if firstName == "":
            ErrorMessagePopup(errorMessage="First Name cannot be empty").open()
            return

        if lastName == "":
            ErrorMessagePopup(errorMessage="Last Name cannot be empty").open()
            return

        existingPatronId = self.manager.database.get_patron_id_by_card_id(cardId)
        if existingPatronId and cardId != "":
            patronWithTheId = self.manager.database.get_patron_data(existingPatronId)
            ErrorMessagePopup(
                errorMessage=f"Card ID is already used by {patronWithTheId.firstName}"
            ).open()
            self.ids.cardIdInput.setText("")
            return

        self.manager.database.add_patron(firstName, lastName, cardId)

        self.manager.transitionToScreen("loginScreen", transitionDirection="right")

    def cancel(self):
        """Handle the cancel action."""
        self.manager.transitionToScreen("loginScreen", transitionDirection="right")

    def cardRead(self, cardId, *args):
        self.ids.cardIdInput.setText(str(cardId))

    def on_enter(self, *args):
        self.manager.registerCardReadCallback(self.cardRead)
        self.manager.RFIDReader.start()
        return super().on_enter(*args)

    def on_leave(self, *args):
        self.manager.RFIDReader.stop()
        self.manager.unregisterCardReadCallback()
        self.ids.firstNameInput.clearText()
        self.ids.lastNameInput.clearText()
        self.ids.cardIdInput.clearText()
        return super().on_leave(*args)
