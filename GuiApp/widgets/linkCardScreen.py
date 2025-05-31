from database import getAllPatrons, getPatronData
from kivy.uix.screenmanager import Screen
from widgets.popups.linkCardConfirmationPopup import LinkCardConfirmationPopup


class LinkCardScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.cardId = None

    def on_pre_enter(self, *args):
        super().on_pre_enter(*args)
        self.addUsersFromDatabase()

    def on_leave(self, *args):
        self.ids.usersTable.clearEntries()
        return super().on_leave(*args)

    def addUsersFromDatabase(self):
        patrons = getAllPatrons()
        for patron in patrons:
            self.ids.usersTable.addEntry(
                entryContents=[
                    patron.firstName,
                    patron.lastName,
                    patron.employeeID if patron.employeeID != "" else "None",
                ],
                entryIdentifier=patron.patronId,
            )

    def setCardToLink(self, cardId):
        self.cardId = cardId

    def cancel(self):
        self.manager.transitionToScreen("splashScreen", transitionDirection="right")

    def onUserEntryPressed(self, identifier):
        selectedPatron = getPatronData(patronID=identifier)
        if selectedPatron.employeeID == "":
            LinkCardConfirmationPopup(
                screenManager=self.manager,
                patronId=identifier,
                newCardId=self.cardId,
                changeType=LinkCardConfirmationPopup.NEW_CARD,
            ).open()
        else:
            LinkCardConfirmationPopup(
                screenManager=self.manager,
                patronId=identifier,
                newCardId=self.cardId,
                changeType=LinkCardConfirmationPopup.EXISTING_CARD,
            ).open()
