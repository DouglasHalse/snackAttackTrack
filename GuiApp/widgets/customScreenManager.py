from database import SnackData, UserData, getPatronData
from kivy.properties import ObjectProperty, StringProperty
from kivy.uix.screenmanager import ScreenManager, SlideTransition
from RFIDReader import RFIDReader
from widgets.settingsManager import SettingsManager

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

    def login(self, patronId):
        self._currentPatron = getPatronData(patronID=patronId)

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
        self._currentPatron = getPatronData(patronID=self._currentPatron.patronId)

    def transitionToScreen(self, screenName, transitionDirection: str = "left"):
        self.transition = SlideTransition(direction=transitionDirection)
        self.current = screenName
