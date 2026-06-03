from app_types import UserData
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.properties import NumericProperty, ObjectProperty, StringProperty
from kivy.uix.screenmanager import (
    Screen,
    ScreenManager,
    ScreenManagerException,
    SlideTransition,
)
from RFIDReader import RFIDReader
from logger import get_logger
from widgets.GridLayoutScreen import GridLayoutScreen
from widgets.settingsManager import SettingName, SettingsManager

# pylint: disable=too-many-instance-attributes

logger = get_logger(__name__)


class CustomScreenManager(ScreenManager):
    logged_in_user = ObjectProperty(None, allownone=True)
    top_up_requestee = StringProperty(None, allownone=True)
    idle_timer_remaining = NumericProperty(0)

    def __init__(self, settingsManager: SettingsManager, database, **kwargs):
        super().__init__()
        self._currentPatron: UserData = None
        self.settingsManager: SettingsManager = settingsManager
        self.current: StringProperty
        self.transition: ObjectProperty
        self.database = database
        self.RFIDReader = RFIDReader()
        Window.bind(on_touch_down=self._on_window_touch)
        self.log_out_timer = None
        self._logout_deadline = 0
        self._idle_display_event = None
        self.settingsManager.register_on_setting_change_callback(
            SettingName.DEBUG_AUTO_LOGOUT_TIMER,
            self._on_debug_timer_setting_changed,
        )

    def _reset_idle_timer(self):
        """Cancel any existing timer and schedule a new auto-logout.

        Safe to call anywhere — exceptions are caught so they can't
        accidentally prevent the timer from being reset.
        """
        try:
            if not self._currentPatron:
                return
            if not self.settingsManager.get_setting_value(
                settingName=SettingName.AUTO_LOGOUT_ON_IDLE_ENABLE
            ):
                return
            timeToLogout = self.settingsManager.get_setting_value(
                settingName=SettingName.AUTO_LOGOUT_ON_IDLE_TIME
            )
            if self.log_out_timer:
                self.log_out_timer.cancel()
            self.log_out_timer = Clock.schedule_once(
                lambda dt: self.auto_logout(), timeToLogout
            )
            # Debug display: store deadline for countdown calculation
            self._logout_deadline = Clock.get_time() + timeToLogout
            if self.settingsManager.get_setting_value(
                settingName=SettingName.DEBUG_AUTO_LOGOUT_TIMER
            ):
                self.idle_timer_remaining = timeToLogout
                self._start_debug_display()
        except Exception:  # pylint: disable=broad-exception-caught
            pass

    def _start_debug_display(self):
        """Start the display-only countdown interval if debug setting is enabled."""
        if self._idle_display_event:
            self._idle_display_event.cancel()
            self._idle_display_event = None
        if self.settingsManager.get_setting_value(
            settingName=SettingName.DEBUG_AUTO_LOGOUT_TIMER
        ):
            # Set the remaining time immediately so the label doesn't flicker
            self.idle_timer_remaining = max(0, self._logout_deadline - Clock.get_time())
            self._idle_display_event = Clock.schedule_interval(
                self._update_debug_display, 0.1
            )

    def _stop_debug_display(self):
        """Stop the debug display interval and reset the remaining time."""
        if self._idle_display_event:
            self._idle_display_event.cancel()
            self._idle_display_event = None
        self.idle_timer_remaining = 0

    def _update_debug_display(self, dt):
        """Update the remaining time from the stored deadline (display only)."""
        # Safety check: if debug setting was toggled off, stop immediately
        if not self.settingsManager.get_setting_value(
            settingName=SettingName.DEBUG_AUTO_LOGOUT_TIMER
        ):
            self._stop_debug_display()
            return
        self.idle_timer_remaining = max(0, self._logout_deadline - Clock.get_time())

    def _on_debug_timer_setting_changed(self, value):
        """React immediately when the debug timer setting is toggled."""
        if value and self._currentPatron:
            self._start_debug_display()
        elif not value:
            self._stop_debug_display()

    def _on_window_touch(self, _window, _touch):
        """Called on every touch to the screen. Resets the idle timer."""
        self._reset_idle_timer()

    def login(self, patronId):
        patron = self.database.getPatronData(patronID=patronId)
        if patron is None:
            logger.warning("Login failed: no patron found for ID %s", patronId)
            return
        self._currentPatron = patron
        self.logged_in_user = self._currentPatron
        logger.info(
            "User logged in: %s %s (ID: %s)",
            patron.firstName,
            patron.lastName,
            patron.patronId,
        )
        self._reset_idle_timer()

    def auto_logout(self):
        if self._currentPatron:
            logger.info(
                "Auto-logout triggered for %s %s",
                self._currentPatron.firstName,
                self._currentPatron.lastName,
            )
        else:
            logger.info("Auto-logout triggered")
        self.logout()
        self.transitionToScreen("splashScreen", transitionDirection="right")

    def logout(self):
        if self._currentPatron:
            logger.info(
                "User logged out: %s %s (ID: %s)",
                self._currentPatron.firstName,
                self._currentPatron.lastName,
                self._currentPatron.patronId,
            )
        self._currentPatron = None
        self.logged_in_user = None

        # If the user was topping up from the buy screen, clear the stashed snacks
        if self.top_up_requestee == "buyScreen":
            self.get_screen("buyScreen").snackStash = {}

        self.top_up_requestee = None
        if self.log_out_timer:
            self.log_out_timer.cancel()
            self.log_out_timer = None
        self._stop_debug_display()

    def getCurrentPatron(self) -> UserData:
        return self._currentPatron

    def refreshCurrentPatron(self):
        self._currentPatron = self.database.getPatronData(
            patronID=self._currentPatron.patronId
        )
        self.logged_in_user = self._currentPatron

    def transitionToScreen(self, screenName, transitionDirection: str = "left"):
        old_screen = (
            self.current if hasattr(self, "current") and self.current else "(none)"
        )
        logger.debug(
            "Screen transition: %s -> %s (direction: %s)",
            old_screen,
            screenName,
            transitionDirection,
        )
        self.transition = SlideTransition(direction=transitionDirection)
        self.current = screenName

    def transition_back_from_top_up(self):
        if self.top_up_requestee:
            self.transitionToScreen(self.top_up_requestee, transitionDirection="right")
            self.top_up_requestee = None
        else:
            self.transitionToScreen("mainUserPage", transitionDirection="right")

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
