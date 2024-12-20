from kivy.uix.screenmanager import ScreenManager
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.popup import Popup
from widgets.headerBodyLayout import HeaderBodyScreen

from database import UserData, updatePatronData, removePatron


class BoxLayoutButton(ButtonBehavior, BoxLayout):
    pass


class EditUserScreenContent(GridLayout):
    def __init__(self, screenManager: ScreenManager, **kwargs):
        super().__init__(**kwargs)
        self.screenManager = screenManager
        self.patronToEdit: UserData = self.screenManager.getPatronToEdit()
        self.ids["firstNameInput"].text = self.patronToEdit.firstName
        self.ids["lastNameInput"].text = self.patronToEdit.lastName
        self.ids["creditsInput"].text = f"{self.patronToEdit.totalCredits:.2f}"
        self.ids["cardIdInput"].text = self.patronToEdit.employeeID

    def onConfirm(self):
        newFirstName = self.ids["firstNameInput"].text
        newLastName = self.ids["lastNameInput"].text
        newcardId = self.ids["cardIdInput"].text
        newCredits = self.ids["creditsInput"].text
        newUserData = UserData(
            patronId=self.patronToEdit.patronId,
            firstName=newFirstName,
            lastName=newLastName,
            employeeID=newcardId,
            totalCredits=newCredits,
        )
        updatePatronData(patronId=self.patronToEdit.patronId, newUserData=newUserData)
        self.screenManager.refreshCurrentPatron()
        self.screenManager.current = "editUsersScreen"

    def onCancel(self):
        self.screenManager.current = "editUsersScreen"

    def onRemove(self):
        popup = RemoveUserConfirmationPopup(
            screenManager=self.screenManager, patronToRemove=self.patronToEdit
        )
        popup.open()


class EditUserScreen(HeaderBodyScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.headerSuffix = "Edit User screen"

    def on_pre_enter(self, *args):
        super().on_pre_enter(*args)
        self.body.add_widget(EditUserScreenContent(screenManager=self.manager))

    def on_leave(self, *args):
        super().on_leave(*args)
        self.manager.resetPatronToEdit()


class RemoveUserConfirmationPopup(Popup):
    def __init__(
        self, screenManager: ScreenManager, patronToRemove: UserData, **kwargs
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
        self.screenManager.current = "editUsersScreen"
