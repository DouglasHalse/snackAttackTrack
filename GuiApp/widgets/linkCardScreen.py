from kivy.uix.screenmanager import Screen
from widgets.popups.linkCardConfirmationPopup import LinkCardConfirmationPopup
from widgets.popups.errorMessagePopup import ErrorMessagePopup


class LinkCardScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.card_id_to_link = None

    def on_pre_enter(self, *args):
        super().on_pre_enter(*args)
        self.add_users_from_database()

    def on_leave(self, *args):
        self.ids.usersTable.clearEntries()
        return super().on_leave(*args)

    def add_users_from_database(self):
        patrons = self.manager.database.getAllPatrons()
        for patron in patrons:
            self.ids.usersTable.addEntry(
                entryContents=[
                    patron.firstName,
                    patron.lastName,
                    patron.employeeID if patron.employeeID != "" else "None",
                ],
                entryIdentifier=patron.patronId,
            )

    def set_card_to_link(self, cardId):
        self.card_id_to_link = cardId

    def cancel(self):
        self.manager.transitionToScreen("splashScreen", transitionDirection="right")

    def on_user_entry_pressed(self, identifier):
        selectedPatron = self.manager.database.getPatronData(patronID=identifier)

        def on_confirm(*args):
            if (
                not self.manager.database.getPatronIdByCardId(
                    cardId=self.card_id_to_link
                )
                is None
            ):
                ErrorMessagePopup(
                    errorMessage="Card ID already linked to another user."
                ).open()
                return

            selectedPatron.employeeID = self.card_id_to_link
            self.manager.database.updatePatronData(
                patronId=selectedPatron.patronId, newUserData=selectedPatron
            )
            self.manager.transitionToScreen("splashScreen", transitionDirection="right")

        change_type = (
            LinkCardConfirmationPopup.NEW_CARD
            if selectedPatron.employeeID == ""
            else LinkCardConfirmationPopup.EXISTING_CARD
        )

        popup = LinkCardConfirmationPopup(
            patron_to_edit=selectedPatron,
            change_type=change_type,
        )
        popup.bind(on_confirm=on_confirm)
        popup.open()
