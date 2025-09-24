from database import UserData, getPatronData
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.properties import ObjectProperty, StringProperty
from kivy.uix.screenmanager import (
    Screen,
    ScreenManager,
    ScreenManagerException,
    SlideTransition,
)
from RFIDReader import RFIDReader
from widgets.GridLayoutScreen import GridLayoutScreen
from widgets.settingsManager import SettingName, SettingsManager

# pylint: disable=too-many-instance-attributes


class CustomScreenManager(ScreenManager):
    logged_in_user = ObjectProperty(None, allownone=True)

    def __init__(self, settingsManager: SettingsManager):
        super().__init__()
        self._currentPatron: UserData = None
        self.settingsManager: SettingsManager = settingsManager
        self.current: StringProperty
        self.transition: ObjectProperty
        self.RFIDReader = RFIDReader()
        Window.bind(on_touch_down=self.on_activity)
        self.log_out_timer = None

    def on_activity(self, _, __):
        if self._currentPatron:
            if self.settingsManager.get_setting_value(
                settingName=SettingName.AUTO_LOGOUT_ON_IDLE_ENABLE
            ):
                timeToAutoLogout = self.settingsManager.get_setting_value(
                    settingName=SettingName.AUTO_LOGOUT_ON_IDLE_TIME
                )
                if self.log_out_timer:
                    self.log_out_timer.cancel()
                self.log_out_timer = Clock.schedule_once(
                    lambda dt: self.auto_logout(), timeToAutoLogout
                )

    def login(self, patronId):
        self._currentPatron = getPatronData(patronID=patronId)
        self.logged_in_user = self._currentPatron
        if self.settingsManager.get_setting_value(
            settingName=SettingName.AUTO_LOGOUT_ON_IDLE_ENABLE
        ):
            timeToAutoLogout = self.settingsManager.get_setting_value(
                settingName=SettingName.AUTO_LOGOUT_ON_IDLE_TIME
            )
            self.log_out_timer = Clock.schedule_once(
                lambda dt: self.auto_logout(), timeToAutoLogout
            )

    def auto_logout(self):
        self.logout()
        self.transitionToScreen("splashScreen", transitionDirection="right")

    def logout(self):
        self._currentPatron = None
        self.logged_in_user = None
        if self.log_out_timer:
            self.log_out_timer.cancel()
            self.log_out_timer = None

    def getCurrentPatron(self) -> UserData:
        return self._currentPatron

    def refreshCurrentPatron(self):
        self._currentPatron = getPatronData(patronID=self._currentPatron.patronId)
        self.logged_in_user = self._currentPatron

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
