from kivy.uix.screenmanager import ScreenManager
from kivy.uix.screenmanager import SlideTransition
from kivy.properties import StringProperty
from kivy.properties import ObjectProperty

from database import UserData, SnackData, getPatronData


class CustomScreenManager(ScreenManager):
    def __init__(self):
        super().__init__()
        self._currentPatron: UserData = None
        self._patronToEdit: UserData = None
        self._snackToEdit: SnackData = None
        self.current: StringProperty
        self.transition: ObjectProperty

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
