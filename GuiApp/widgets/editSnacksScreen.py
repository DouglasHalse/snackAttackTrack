from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.behaviors import ButtonBehavior
from database import getAllSnacks, getSnack
from widgets.customScreenManager import CustomScreenManager
from widgets.headerBodyLayout import HeaderBodyScreen
from widgets.clickableTable import ClickableTable


class BoxLayoutButton(ButtonBehavior, BoxLayout):
    pass


class EditSnacksScreenContent(GridLayout):
    ADD_SNACK_ENTRY_IDENTIFIER = -1

    def __init__(self, screenManager: CustomScreenManager, **kwargs):
        super().__init__(**kwargs)
        self.screenManager = screenManager
        self.snackTable = ClickableTable(
            columns=["Snack name", "Quantity", "Price", "Image ID"],
            columnExamples=["Long snack name", "100", "43.43", "AnImageId"],
            onEntryPressedCallback=self.onEntryPressed,
        )
        self.add_widget(self.snackTable)
        self.addSnacksFromDatabase()

    def addSnacksFromDatabase(self):
        snacks = getAllSnacks()

        for snack in snacks:
            self.snackTable.addEntry(
                entryContents=[
                    snack.snackName,
                    str(snack.quantity),
                    f"{snack.pricePerItem:.2f}",
                    str(snack.imageID),
                ],
                entryIdentifier=snack.snackId,
            )

        self.snackTable.addEntry(
            entryContents=["[i]Add a snack +[/i]"],
            entryIdentifier=self.ADD_SNACK_ENTRY_IDENTIFIER,
        )

    def onAddSnackEntryPressed(self):
        self.screenManager.transitionToScreen("addSnackScreen")

    def onEditSnackEntryPressed(self, snackId):
        snackToEdit = getSnack(snackId)
        self.screenManager.setSnackToEdit(snackToEdit=snackToEdit)
        self.screenManager.transitionToScreen("editSnackScreen")

    def onEntryPressed(self, identifier):
        if identifier == self.ADD_SNACK_ENTRY_IDENTIFIER:
            self.onAddSnackEntryPressed()
        else:
            self.onEditSnackEntryPressed(identifier)


class EditSnacksScreen(HeaderBodyScreen):
    def __init__(self, **kwargs):
        super().__init__(previousScreen="adminScreen", **kwargs)
        self.headerSuffix = "Edit snacks screen"

    def on_pre_enter(self, *args):
        super().on_pre_enter(*args)
        self.body.add_widget(EditSnacksScreenContent(screenManager=self.manager))
