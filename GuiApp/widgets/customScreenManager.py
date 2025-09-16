from database import SnackData, UserData, getPatronData
from kivy.properties import ObjectProperty, StringProperty
from kivy.uix.screenmanager import (
    Screen,
    ScreenManager,
    ScreenManagerException,
    SlideTransition,
)
from RFIDReader import RFIDReader
from widgets.GridLayoutScreen import GridLayoutScreen
from widgets.settingsManager import SettingsManager

# pylint: disable=too-many-instance-attributes


class CustomScreenManager(ScreenManager):
    logged_in_user = ObjectProperty(None, allownone=True)

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
        self.logged_in_user = self._currentPatron

    def logout(self):
        self._currentPatron = None
        self.logged_in_user = None

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

    def add_widget(self, widget, *args, **kwargs):
        """
        .. versionchanged:: 2.1.0
            Renamed argument `screen` to `widget`.
        """
        if not isinstance(widget, (GridLayoutScreen, Screen)):
            raise ScreenManagerException("ScreenManager accepts only Screen widget.")
        if widget.manager:
            if widget.manager is self:
                raise ScreenManagerException(
                    "Screen already managed by this ScreenManager (are you "
                    "calling `switch_to` when you should be setting "
                    "`current`?)"
                )
            raise ScreenManagerException(
                "Screen already managed by another ScreenManager."
            )
        widget.manager = self
        widget.bind(name=self._screen_name_changed)
        self.screens.append(widget)
        if self.current is None:
            self.current = widget.name

    def remove_widget(self, widget, *args, **kwargs):
        if not isinstance(widget, (GridLayoutScreen, Screen)):
            raise ScreenManagerException(
                "ScreenManager uses remove_widget only for removing Screens."
            )

        if widget not in self.screens:
            return

        if self.current_screen == widget:
            other = next(self)
            if widget.name == other:
                self.current = None
                widget.parent.real_remove_widget(widget)
            else:
                self.current = other

        widget.manager = None
        widget.unbind(name=self._screen_name_changed)
        self.screens.remove(widget)
