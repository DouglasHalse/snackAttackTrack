from kivy.uix.modalview import ModalView
from widgets.popups.errorMessagePopup import ErrorMessagePopup


class LinkCardConfirmationPopup(ModalView):
    NEW_CARD = 0
    EXISTING_CARD = 1

    def __init__(self, screenManager, patronId, newCardId, changeType: int, **kwargs):
        super().__init__(**kwargs)
        self.screenManager = screenManager
        self.selectedPatron = self.manager.database.getPatronData(patronID=patronId)
        self.newCardId = newCardId
        self.changeType = changeType
        if changeType == self.NEW_CARD:
            self.ids.title.text = f"Link card to {self.selectedPatron.firstName} {self.selectedPatron.lastName}?"
            self.ids.question.text = "Are you sure you want to link this card?"
        elif changeType == self.EXISTING_CARD:
            self.ids.title.text = f"Change linked card for {self.selectedPatron.firstName} {self.selectedPatron.lastName}?"
            self.ids.question.text = "Are you sure you want to change the linked card?"
        else:
            raise ValueError("Invalid change type")

    def onConfirm(self):
        self.dismiss()

        if not self.manager.database.getPatronIdByCardId(cardId=self.newCardId) is None:
            ErrorMessagePopup(
                errorMessage="Card ID already linked to another user."
            ).open()
            return

        self.selectedPatron.employeeID = self.newCardId
        self.manager.database.updatePatronData(
            patronId=self.selectedPatron.patronId, newUserData=self.selectedPatron
        )
        self.screenManager.transitionToScreen(
            "splashScreen", transitionDirection="right"
        )

    def onCancel(self):
        self.dismiss()
