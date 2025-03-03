from functools import partial

from kivy.uix.screenmanager import ScreenManager
from kivy.uix.screenmanager import SlideTransition
from kivy.properties import StringProperty
from kivy.properties import ObjectProperty
from kivy.clock import Clock

from widgets.settingsManager import SettingsManager
from RFIDReader import RFIDReader
from database import UserData, SnackData, Database

# pylint: disable=too-many-instance-attributes


class CustomScreenManager(ScreenManager):
    def __init__(self, settingsManager: SettingsManager):
        super().__init__()
        self._currentPatron: UserData = None
        self._patronToEdit: UserData = None
        self._snackToEdit: SnackData = None
        self.settingsManager: SettingsManager = settingsManager
        self.current: StringProperty
        self.transition: ObjectProperty
        self.RFIDReader = RFIDReader()
        self._cardReadCallback = None
        self.RFIDReader.registerCallbackFunction(self.onCardRead)
        self.database = Database()

    def registerCardReadCallback(self, function):
        self._cardReadCallback = function

    def unregisterCardReadCallback(self):
        self._cardReadCallback = None

    def onCardRead(self, cardId):
        if self._cardReadCallback:
            Clock.schedule_once(
                partial(self._cardReadCallback, cardId), 0
            )  # call after the next frame

    def login(self, patronId):
        self._currentPatron = self.database.get_patron_data(patronID=patronId)

    def logout(self):
        self._currentPatron = None

    def setPatronToEdit(self, patronToEdit: UserData):
        self._patronToEdit = patronToEdit

    def getPatronToEdit(self) -> UserData:
        return self._patronToEdit

    def resetPatronToEdit(self):
        self._patronToEdit = None

    def setSnackToEdit(self, snackToEdit: SnackData):
        self._snackToEdit = snackToEdit

    def getSnackToEdit(self) -> SnackData:
        return self._snackToEdit

    def resetSnackToEdit(self):
        self._snackToEdit = None

    def getCurrentPatron(self) -> UserData:
        return self._currentPatron

    def refreshCurrentPatron(self):
        self._currentPatron = self.database.get_patron_data(
            patronID=self._currentPatron.patronId
        )

    def transitionToScreen(self, screenName, transitionDirection: str = "left"):
        self.transition = SlideTransition(direction=transitionDirection)
        self.current = screenName
