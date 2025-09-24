from datetime import datetime

from database import (
    UserData,
    addEditTransaction,
    getPatronData,
    getPatronIdByCardId,
    removePatron,
    updatePatronData,
)
from kivy.properties import ObjectProperty
from kivy.uix.modalview import ModalView
from widgets.customScreenManager import CustomScreenManager
from widgets.GridLayoutScreen import GridLayoutScreen
from widgets.popups.errorMessagePopup import ErrorMessagePopup


class EditUserScreen(GridLayoutScreen):
    user_to_edit = ObjectProperty(None, allownone=True)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.ids.header.bind(on_back_button_pressed=self.on_back_button_pressed)

    def on_back_button_pressed(self, *args):
        self.manager.transitionToScreen("editUsersScreen", transitionDirection="right")

    def on_pre_enter(self, *args):
        super().on_pre_enter(*args)

    def on_enter(self, *args):
        self.manager.RFIDReader.start(self.cardRead)
        return super().on_enter(*args)

    def on_pre_leave(self, *args):
        self.manager.RFIDReader.stop()
        return super().on_pre_leave(*args)

    def on_leave(self, *args):
        self.user_to_edit = None
        super().on_leave(*args)

    def on_user_to_edit(self, _, value):
        if value:
            self.ids.firstNameInput.setText(value.firstName)
            self.ids.lastNameInput.setText(value.lastName)
            self.ids.creditsInput.setText(f"{value.totalCredits:.2f}")
            self.ids.cardIdInput.setText(value.employeeID)
            if value.employeeID:
                self.ids.cardIdInput.header_text = "Login card (tap card to change)"
            else:
                self.ids.cardIdInput.header_text = "Login card (tap card to set)"
        else:
            self.ids.firstNameInput.setText("FIRSTNAME")
            self.ids.lastNameInput.setText("LASTNAME")
            self.ids.creditsInput.setText("AMOUNT")
            self.ids.cardIdInput.setText("CARD ID")
            self.ids.cardIdInput.header_text = "Login card"

    def cardRead(self, cardId, *args):
        self.ids.cardIdInput.setText(str(cardId))

    def onConfirm(self):
        newFirstName = self.ids.firstNameInput.getText()
        newLastName = self.ids.lastNameInput.getText()
        newcardId = self.ids.cardIdInput.getText()
        newCredits = self.ids.creditsInput.getText()

        if newFirstName == "":
            ErrorMessagePopup(errorMessage="First name cannot be empty").open()
            return

        if newLastName == "":
            ErrorMessagePopup(errorMessage="Last name cannot be empty").open()
            return

        try:
            newCredits = float(newCredits)
        except ValueError:
            ErrorMessagePopup(errorMessage="Credits must be a number").open()
            return

        if newCredits < 0:
            ErrorMessagePopup(errorMessage="Credits cannot be negative").open()
            return

        existingPatronId = getPatronIdByCardId(newcardId)
        if (
            existingPatronId
            and existingPatronId != self.user_to_edit.patronId
            and newcardId != ""
        ):
            patron_with_id = getPatronData(existingPatronId)
            ErrorMessagePopup(
                errorMessage=f"Card ID is already used by {patron_with_id.firstName}"
            ).open()
            self.ids.cardIdInput.setText("")
            return

        newUserData = UserData(
            patronId=self.user_to_edit.patronId,
            firstName=newFirstName,
            lastName=newLastName,
            employeeID=newcardId,
            totalCredits=newCredits,
        )

        if self.user_to_edit.totalCredits != newCredits:
            addEditTransaction(
                patronID=self.user_to_edit.patronId,
                amountBeforeTransaction=self.user_to_edit.totalCredits,
                amountAfterTransaction=newCredits,
                transactionDate=datetime.now(),
            )

        updatePatronData(patronId=self.user_to_edit.patronId, newUserData=newUserData)

        # Update current patron with new data
        self.manager.refreshCurrentPatron()

        self.manager.transitionToScreen("editUsersScreen", transitionDirection="right")

    def onCancel(self):
        self.manager.transitionToScreen("editUsersScreen", transitionDirection="right")

    def onRemove(self):
        popup = RemoveUserConfirmationPopup(
            screenManager=self.manager, patronToRemove=self.user_to_edit
        )
        popup.open()


class RemoveUserConfirmationPopup(ModalView):
    def __init__(
        self, screenManager: CustomScreenManager, patronToRemove: UserData, **kwargs
    ):
        super().__init__(**kwargs)
        self.screenManager = screenManager
        self.patronToRemove = patronToRemove
        self.ids.areYouSureLabel.text = (
            f"Are you sure you want to \nremove {self.patronToRemove.firstName}?"
        )

    def onCancel(self):
        self.dismiss()

    def onRemove(self):
        removePatron(self.patronToRemove.patronId)
        self.dismiss()
        self.screenManager.transitionToScreen(
            "editUsersScreen", transitionDirection="right"
        )
