from datetime import datetime

from database import (
    UserData,
    addEditTransaction,
    getPatronData,
    getPatronIdByCardId,
    removePatron,
    updatePatronData,
)
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.modalview import ModalView
from widgets.customScreenManager import CustomScreenManager
from widgets.headerBodyLayout import HeaderBodyScreen
from widgets.popups.errorMessagePopup import ErrorMessagePopup


class BoxLayoutButton(ButtonBehavior, BoxLayout):
    pass


class EditUserScreenContent(GridLayout):
    def __init__(self, screenManager: CustomScreenManager, **kwargs):
        super().__init__(**kwargs)
        self.screenManager = screenManager
        self.patronToEdit: UserData = self.screenManager.getPatronToEdit()
        self.ids["firstNameInput"].setText(self.patronToEdit.firstName)
        self.ids["lastNameInput"].setText(self.patronToEdit.lastName)
        self.ids["creditsInput"].setText(f"{self.patronToEdit.totalCredits:.2f}")
        self.ids["cardIdInput"].setText(self.patronToEdit.employeeID)

        if self.patronToEdit.employeeID:
            self.ids["cardIdInput"].header_text = "Login card (tap card to change)"

    def cardRead(self, cardId, *args):
        self.ids["cardIdInput"].setText(str(cardId))

    def onConfirm(self):
        newFirstName = self.ids["firstNameInput"].getText()
        newLastName = self.ids["lastNameInput"].getText()
        newcardId = self.ids["cardIdInput"].getText()
        newCredits = self.ids["creditsInput"].getText()

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
            and existingPatronId != self.patronToEdit.patronId
            and newcardId != ""
        ):
            patronWithTheId = getPatronData(existingPatronId)
            ErrorMessagePopup(
                errorMessage=f"Card ID is already used by {patronWithTheId.firstName}"
            ).open()
            self.ids["cardIdInput"].setText("")
            return

        newUserData = UserData(
            patronId=self.patronToEdit.patronId,
            firstName=newFirstName,
            lastName=newLastName,
            employeeID=newcardId,
            totalCredits=newCredits,
        )

        if self.patronToEdit.totalCredits != newCredits:
            addEditTransaction(
                patronID=self.patronToEdit.patronId,
                amountBeforeTransaction=self.patronToEdit.totalCredits,
                amountAfterTransaction=newCredits,
                transactionDate=datetime.now(),
            )

        updatePatronData(patronId=self.patronToEdit.patronId, newUserData=newUserData)

        # Update current patron with new data
        self.screenManager.refreshCurrentPatron()

        self.screenManager.transitionToScreen(
            "editUsersScreen", transitionDirection="right"
        )

    def onCancel(self):
        self.screenManager.transitionToScreen(
            "editUsersScreen", transitionDirection="right"
        )

    def onRemove(self):
        popup = RemoveUserConfirmationPopup(
            screenManager=self.screenManager, patronToRemove=self.patronToEdit
        )
        popup.open()


class EditUserScreen(HeaderBodyScreen):
    def __init__(self, **kwargs):
        super().__init__(previousScreen="editUsersScreen", **kwargs)
        self.headerSuffix = "Edit User screen"
        self.content = None

    def on_pre_enter(self, *args):
        super().on_pre_enter(*args)
        self.content = EditUserScreenContent(screenManager=self.manager)
        self.body.add_widget(self.content)

    def on_enter(self, *args):
        self.manager.RFIDReader.start(self.content.cardRead)
        return super().on_enter(*args)

    def on_pre_leave(self, *args):
        self.manager.RFIDReader.stop()
        return super().on_pre_leave(*args)

    def on_leave(self, *args):
        super().on_leave(*args)
        self.manager.resetPatronToEdit()


class RemoveUserConfirmationPopup(ModalView):
    def __init__(
        self, screenManager: CustomScreenManager, patronToRemove: UserData, **kwargs
    ):
        super().__init__(**kwargs)
        self.screenManager = screenManager
        self.patronToRemove = patronToRemove
        self.ids[
            "areYouSureLabel"
        ].text = f"Are you sure you want to \nremove {self.patronToRemove.firstName}?"

    def onCancel(self):
        self.dismiss()

    def onRemove(self):
        removePatron(self.patronToRemove.patronId)
        self.dismiss()
        self.screenManager.transitionToScreen(
            "editUsersScreen", transitionDirection="right"
        )
