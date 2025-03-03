from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.behaviors import ButtonBehavior
from widgets.customScreenManager import CustomScreenManager
from widgets.headerBodyLayout import HeaderBodyScreen
from widgets.clickableTable import ClickableTable


class BoxLayoutButton(ButtonBehavior, BoxLayout):
    pass


class EditSnacksScreenContent(GridLayout):
    def __init__(self, screenManager: CustomScreenManager, **kwargs):
        super().__init__(**kwargs)
        self.screenManager = screenManager
        self.snackTable = ClickableTable(
            columns=["Snack name", "Quantity", "Price", "Image ID"],
            columnExamples=["Long snack name", "100", "43.43", "AnImageId"],
            onEntryPressedCallback=self.onSnackEntryPressed,
        )
        self.add_widget(self.snackTable)
        self.addSnacksFromDatabase()

    def addSnacksFromDatabase(self):
        snacks = self.screenManager.database.get_all_snacks()

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

        self.snackTable.addCustomEntry(
            entryContents=["[i]Add a snack +[/i]"],
            onPressCallback=self.onAddSnackEntryPressed,
        )

    def onAddSnackEntryPressed(self):
        self.screenManager.transitionToScreen("addSnackScreen")

    def onSnackEntryPressed(self, identifier):
        snackToEdit = self.screenManager.database.get_snack(identifier)
        self.screenManager.setSnackToEdit(snackToEdit=snackToEdit)
        self.screenManager.transitionToScreen("editSnackScreen")


class EditSnacksScreen(HeaderBodyScreen):
    def __init__(self, **kwargs):
        super().__init__(previousScreen="adminScreen", **kwargs)
        self.headerSuffix = "Edit snacks screen"

    def on_pre_enter(self, *args):
        super().on_pre_enter(*args)
        self.body.add_widget(EditSnacksScreenContent(screenManager=self.manager))
