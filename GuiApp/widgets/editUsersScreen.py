from widgets.GridLayoutScreen import GridLayoutScreen


class EditUsersScreen(GridLayoutScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.ids.header.bind(on_back_button_pressed=self.on_back_button_pressed)

    def on_back_button_pressed(self, *args):
        self.manager.transitionToScreen("adminScreen", transitionDirection="right")

    def on_pre_enter(self, *args):
        super().on_pre_enter(*args)
        users = self.manager.database.getAllPatrons()
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

    def on_leave(self, *args):
        self.ids.usersTable.clearEntries()

    def onUserEntryPressed(self, identifier):
        userToEdit = self.manager.database.getPatronData(patronID=identifier)
        self.manager.get_screen("editUserScreen").user_to_edit = userToEdit
        self.manager.transitionToScreen("editUserScreen")
