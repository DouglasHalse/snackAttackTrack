from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.behaviors import ButtonBehavior
from widgets.customScreenManager import CustomScreenManager
from widgets.headerBodyLayout import HeaderBodyScreen
from widgets.clickableTable import ClickableTable


from database import getAllPatrons, getPatronData


class BoxLayoutButton(ButtonBehavior, BoxLayout):
    pass


class EditUsersScreenContent(GridLayout):
    def __init__(self, screenManager: CustomScreenManager, **kwargs):
        super().__init__(**kwargs)
        self.screenManager = screenManager
        self.usersTable = ClickableTable(
            ["Availabe CardId", "Total Registered CardId for use"],
            onEntryPressedCallback=self.onUserEntryPressed,
        )
        self.add_widget(self.usersTable)
        self.addCardIdFromDatabase()

    def addCardIdFromDatabase(self):
        users = getAllPatrons()
        for user in users:
            self.usersTable.addEntry(
                entryContents=[
                    user.firstName,
                    user.lastName,
                    user.employeeID if user.employeeID != "" else "None",
                    f"{user.totalCredits:.2f}",
                ],
                entryIdentifier=user.patronId,
            )

    def onUserEntryPressed(self, identifier):
        userToEdit = getPatronData(patronID=identifier)
        self.screenManager.setPatronToEdit(patronToEdit=userToEdit)
        self.screenManager.transitionToScreen("editUserScreen")


class RegisterCardIdScreen(HeaderBodyScreen):
    def __init__(self, **kwargs):
        super().__init__(previousScreen="adminScreen", **kwargs)
        self.headerSuffix = "Como?"

    def on_pre_enter(self, *args):
        super().on_pre_enter(*args)
        self.body.add_widget(EditUsersScreenContent(screenManager=self.manager))
