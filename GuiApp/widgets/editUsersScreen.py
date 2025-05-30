from database import getAllPatrons, getPatronData
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from widgets.customScreenManager import CustomScreenManager
from widgets.headerBodyLayout import HeaderBodyScreen


class BoxLayoutButton(ButtonBehavior, BoxLayout):
    pass


class EditUsersScreenContent(GridLayout):
    def __init__(self, screenManager: CustomScreenManager, **kwargs):
        super().__init__(**kwargs)
        self.screenManager = screenManager
        self.addUsersFromDatabase()

    def addUsersFromDatabase(self):
        users = getAllPatrons()
        for user in users:
            self.ids.usersTable.addEntry(
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


class EditUsersScreen(HeaderBodyScreen):
    def __init__(self, **kwargs):
        super().__init__(previousScreen="adminScreen", **kwargs)
        self.headerSuffix = "Edit users screen"

    def on_pre_enter(self, *args):
        super().on_pre_enter(*args)
        self.body.add_widget(EditUsersScreenContent(screenManager=self.manager))
