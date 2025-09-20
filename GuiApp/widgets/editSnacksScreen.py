from database import getAllSnacks, getSnack
from widgets.GridLayoutScreen import GridLayoutScreen


class EditSnacksScreen(GridLayoutScreen):
    ADD_SNACK_ENTRY_IDENTIFIER = -1

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.ids.header.bind(on_back_button_pressed=self.on_back_button_pressed)

    def on_back_button_pressed(self, *args):
        self.manager.transitionToScreen("adminScreen", transitionDirection="right")

    def on_pre_enter(self, *args):
        snacks = getAllSnacks()

        for snack in snacks:
            self.ids.snacksTable.addEntry(
                entryContents=[
                    snack.snackName,
                    str(snack.quantity),
                    f"{snack.pricePerItem:.2f}",
                    str(snack.imageID),
                ],
                entryIdentifier=snack.snackId,
            )

        self.ids.snacksTable.addEntry(
            entryContents=["[i]Add a snack +[/i]"],
            entryIdentifier=self.ADD_SNACK_ENTRY_IDENTIFIER,
        )
        return super().on_pre_enter(*args)

    def on_leave(self, *args):
        self.ids.snacksTable.clearEntries()

    def onAddSnackEntryPressed(self):
        self.manager.transitionToScreen("addSnackScreen")

    def onEditSnackEntryPressed(self, snackId):
        snackToEdit = getSnack(snackId)
        self.manager.setSnackToEdit(snackToEdit=snackToEdit)
        self.manager.transitionToScreen("editSnackScreen")

    def onEntryPressed(self, identifier):
        if identifier == self.ADD_SNACK_ENTRY_IDENTIFIER:
            self.onAddSnackEntryPressed()
        else:
            self.onEditSnackEntryPressed(identifier)
