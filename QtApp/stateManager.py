"""
Central state manager for the Qt-based Snack Attack Track GUI.

Replaces the Kivy ``CustomScreenManager`` with a pure Qt/QObject
approach.  Responsibilities:

* Current-user / login state (replaces ``logged_in_user`` Kivy property)
* Screen navigation on a QStackedWidget
* Idle auto-logout timer
* Debug idle-timer display
* RFID adapter lifecycle
"""

import sys
import os
import time as time_module

# Ensure GuiApp is importable
_gui_app_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "GuiApp")
if _gui_app_dir not in sys.path:
    sys.path.insert(0, os.path.abspath(_gui_app_dir))

# pylint: disable=wrong-import-position,too-many-instance-attributes

from PySide6.QtCore import QObject, QTimer, Signal

from database import DatabaseConnector
from logger import get_logger
from widgets.settingsManager import SettingName, SettingsManager

from QtApp.rfidAdapter import RFIDAdapter

logger = get_logger(__name__)


class StateManager(QObject):
    """Manages application state and screen navigation.

    Signals
    -------
    logged_in_user_changed(object)
        Emitted when a user logs in or out (logout sends None).
    logged_out()
        Convenience signal emitted only on logout.
    credits_changed(Credits)
        Emitted when the logged-in user's credits change.
    """

    logged_in_user_changed = Signal(object)  # UserData or None
    logged_out = Signal()
    credits_changed = Signal(object)  # Credits

    def __init__(
        self,
        database: DatabaseConnector,
        settings_manager: SettingsManager,
        parent=None,
    ):
        super().__init__(parent)
        self._database: DatabaseConnector = database
        self._settings_manager: SettingsManager = settings_manager
        self._current_patron = None
        self._stacked_widget = None  # set by MainWindow

        # RFID
        self.rfid_adapter = RFIDAdapter(self)

        # Idle / auto-logout timers
        self._logout_timer = QTimer(self)
        self._logout_timer.setSingleShot(True)
        self._logout_timer.timeout.connect(self._on_idle_timeout)

        self._splash_return_timer = QTimer(self)
        self._splash_return_timer.setSingleShot(True)
        self._splash_return_timer.timeout.connect(self._on_splash_return_timeout)

        # Debug timer display (100 ms interval)
        self._debug_timer = QTimer(self)
        self._debug_timer.setInterval(100)
        self._debug_timer.timeout.connect(self._update_debug_display)
        self._logout_deadline: float = 0.0
        self._debug_remaining: float = 0.0

        # Listen for debug-timer setting changes
        self._settings_manager.register_on_setting_change_callback(
            SettingName.DEBUG_AUTO_LOGOUT_TIMER, self._on_debug_timer_setting_changed
        )

    # ---- Properties ----------------------------------------------------------

    @property
    def database(self) -> DatabaseConnector:
        return self._database

    @property
    def settings_manager(self) -> SettingsManager:
        return self._settings_manager

    @property
    def current_patron(self):
        return self._current_patron

    # ---- Screen navigation ---------------------------------------------------

    def set_stacked_widget(self, stacked_widget):
        """Set the QStackedWidget used for screen transitions."""
        self._stacked_widget = stacked_widget

    def transition_to_screen(self, screen_name: str):
        """Switch the stacked widget to the screen named *screen_name*.

        Calls ``on_hide()`` on the current screen (if implemented) and
        ``on_show()`` on the target screen (if implemented).

        The screen must have been registered in the stacked widget with
        ``stacked_widget.addWidget(screen_widget)`` and the widget's
        ``objectName`` must equal *screen_name*.
        """
        if self._stacked_widget is None:
            logger.error("transition_to_screen: stacked_widget not set")
            return

        # Notify the current screen that it's being hidden
        current = self._stacked_widget.currentWidget()
        if (
            current is not None
            and hasattr(current, "on_hide")
            and callable(current.on_hide)
        ):
            current.on_hide()

        for i in range(self._stacked_widget.count()):
            w = self._stacked_widget.widget(i)
            if w.objectName() == screen_name:
                # Notify screen that it's about to be shown
                if hasattr(w, "on_show") and callable(w.on_show):
                    w.on_show()
                self._stacked_widget.setCurrentWidget(w)
                return
        logger.warning("Screen '%s' not found in stacked widget", screen_name)

    def get_screen(self, screen_name: str):
        """Return the widget whose objectName equals *screen_name*, or None."""
        if self._stacked_widget is None:
            return None
        for i in range(self._stacked_widget.count()):
            w = self._stacked_widget.widget(i)
            if w.objectName() == screen_name:
                return w
        return None

    # ---- Login / logout ------------------------------------------------------

    def login(self, patron_id: int):
        """Look up the patron and set them as the current user."""
        patron = self._database.getPatronData(patronID=patron_id)
        if patron is None:
            logger.warning("Login failed: no patron found for ID %s", patron_id)
            return
        self._current_patron = patron
        self.logged_in_user_changed.emit(patron)
        self.credits_changed.emit(patron.totalCredits)
        logger.info(
            "User logged in: %s %s (ID: %s)",
            patron.firstName,
            patron.lastName,
            patron.patronId,
        )
        self._reset_idle_timer()

    def logout(self):
        """Clear the current user and stop timers."""
        if self._current_patron:
            logger.info(
                "User logged out: %s %s (ID: %s)",
                self._current_patron.firstName,
                self._current_patron.lastName,
                self._current_patron.patronId,
            )
        self._current_patron = None
        self.logged_in_user_changed.emit(None)
        self.logged_out.emit()
        self._stop_idle_timer()
        self._stop_debug_display()

    def get_current_patron(self):
        return self._current_patron

    def refresh_current_patron(self):
        """Reload the current user's data from the database."""
        if self._current_patron is None:
            return
        patron = self._database.getPatronData(patronID=self._current_patron.patronId)
        if patron is not None:
            self._current_patron = patron
            self.logged_in_user_changed.emit(patron)
            self.credits_changed.emit(patron.totalCredits)

    # ---- Idle / auto-logout timer -------------------------------------------

    def _reset_idle_timer(self):
        """Restart the auto-logout timer if the user is logged in and the
        setting is enabled."""
        if self._current_patron is None:
            return
        if not self._settings_manager.get_setting_value(
            SettingName.AUTO_LOGOUT_ON_IDLE_ENABLE
        ):
            return
        time_to_logout = self._settings_manager.get_setting_value(
            SettingName.AUTO_LOGOUT_ON_IDLE_TIME
        )
        self._logout_timer.stop()
        self._logout_timer.start(int(time_to_logout * 1000))

        # Store deadline for debug display
        self._logout_deadline = time_module.time() + time_to_logout

        if self._settings_manager.get_setting_value(
            SettingName.DEBUG_AUTO_LOGOUT_TIMER
        ):
            self._debug_remaining = time_to_logout
            self._start_debug_display()

    def _stop_idle_timer(self):
        self._logout_timer.stop()

    def _on_idle_timeout(self):
        """Called when the auto-logout timer fires."""
        if self._current_patron:
            logger.info(
                "Auto-logout triggered for %s %s",
                self._current_patron.firstName,
                self._current_patron.lastName,
            )
        self.logout()
        self.transition_to_screen("loginScreen")

    # ---- Debug timer display -------------------------------------------------

    def _start_debug_display(self):
        self._debug_timer.start()

    def _stop_debug_display(self):
        self._debug_timer.stop()
        self._debug_remaining = 0.0

    def _update_debug_display(self):
        remaining = max(0.0, self._logout_deadline - time_module.time())
        self._debug_remaining = remaining
        # The main user screen can read this property

    def _on_debug_timer_setting_changed(self, value):
        if value and self._current_patron:
            self._start_debug_display()
        elif not value:
            self._stop_debug_display()

    @property
    def debug_remaining(self) -> float:
        return self._debug_remaining

    # ---- Splash-screen idle return (for LoginScreen) -------------------------

    def reset_splash_return_timer(self, timeout_seconds: float):
        """Schedule a transition back to the splash screen."""
        self._splash_return_timer.stop()
        self._splash_return_timer.start(int(timeout_seconds * 1000))

    def stop_splash_return_timer(self):
        self._splash_return_timer.stop()

    def _on_splash_return_timeout(self):
        self.transition_to_screen("splashScreen")

    # ---- RFID convenience ----------------------------------------------------

    def start_rfid(self, callback=None):
        """Start the RFID reader and connect its signal to *callback*."""
        if callback is not None:
            self.rfid_adapter.card_read.connect(callback)
        self.rfid_adapter.start()

    def stop_rfid(self, callback=None):
        """Stop the RFID reader and disconnect *callback* if given."""
        if callback is not None:
            try:
                self.rfid_adapter.card_read.disconnect(callback)
            except TypeError:
                pass
        self.rfid_adapter.stop()

    # ---- Screenshot helper ---------------------------------------------------

    def get_screen_name_for_screenshot(self) -> str:
        """Return the objectName of the currently visible screen (for screenshot naming)."""
        if self._stacked_widget is not None:
            w = self._stacked_widget.currentWidget()
            if w is not None:
                return w.objectName()
        return "unknown"
