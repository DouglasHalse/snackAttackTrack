"""
Main entry point for the Qt-based Snack Attack Track proof of concept.

Launches the PySide6 GUI with splash, login, create user, and main user
screens.  Shares the same backend (database, settings, logger) with the
existing Kivy application.

Usage::

    python -m QtApp.main
"""

import argparse
import logging
import os
import sys

# Ensure GuiApp is importable
_gui_app_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "GuiApp")
if _gui_app_dir not in sys.path:
    sys.path.insert(0, os.path.abspath(_gui_app_dir))

# pylint: disable=wrong-import-position

from PySide6.QtGui import QAction, QKeySequence
from PySide6.QtWidgets import QApplication, QMainWindow, QStackedWidget

from database import DatabaseConnector
from logger import get_logger, setup_logging
from widgets.settingsManager import SettingName, SettingsManager

# Import screen widgets
from QtApp.screens.splashScreen import SplashScreen
from QtApp.screens.loginScreen import LoginScreen
from QtApp.screens.createUserScreen import CreateUserScreen
from QtApp.screens.mainUserScreen import MainUserScreen
from QtApp.stateManager import StateManager

logger = get_logger(__name__)

# ──────────────────────────────────────────────────────────────────────
# Color palette (same as Kivy app)
# ──────────────────────────────────────────────────────────────────────

COLORS = {
    "background": "#A5E7EA",
    "secondary_background": "#087F8C",
    "button": "#FCACC4",
    "green_button": "#5CB338",
    "yellow_button": "#ECE851",
    "orange_button": "#FFC145",
    "red_button": "#FB4141",
}


# ──────────────────────────────────────────────────────────────────────
# MainWindow
# ──────────────────────────────────────────────────────────────────────


class MainWindow(QMainWindow):
    """The main application window containing the stacked widget."""

    def __init__(self, state_manager: StateManager, settings_manager: SettingsManager):
        super().__init__()
        self._state_manager = state_manager
        self._settings_manager = settings_manager

        self.setWindowTitle("Snack Attack Track")
        self.setGeometry(0, 0, 800, 480)
        # Show fullscreen by default
        # self.showFullScreen()  # called in main()

        # Central stacked widget for screen navigation
        self.stacked_widget = QStackedWidget(self)
        self.stacked_widget.setStyleSheet("background-color: #A5E7EA;")
        self.setCentralWidget(self.stacked_widget)

        # Give state_manager access to the stacked widget
        self._state_manager.set_stacked_widget(self.stacked_widget)

        # Register screens
        self._register_screens()

        # Keyboard shortcuts
        self._setup_shortcuts()

    def _register_screens(self):
        """Create and register all screen widgets."""
        # Order: first added = index 0 (default shown)
        screens = [
            SplashScreen(self._state_manager),
            LoginScreen(self._state_manager),
            CreateUserScreen(self._state_manager),
            MainUserScreen(self._state_manager),
        ]
        for screen in screens:
            self.stacked_widget.addWidget(screen)

        # Start on the splash screen
        # The screens' on_show() will be called on first transition
        self._state_manager.transition_to_screen("splashScreen")

    def _setup_shortcuts(self):
        """Set up keyboard shortcuts matching the Kivy app (F10/F11/F12)."""
        # F10 — toggle window size
        f10 = QAction("Resize", self)
        f10.setShortcut(QKeySequence("F10"))
        f10.triggered.connect(self._toggle_window_size)
        self.addAction(f10)

        # F11 — fake RFID read
        f11 = QAction("Fake RFID", self)
        f11.setShortcut(QKeySequence("F11"))
        f11.triggered.connect(self._fake_rfid)
        self.addAction(f11)

        # F12 — screenshot
        f12 = QAction("Screenshot", self)
        f12.setShortcut(QKeySequence("F12"))
        f12.triggered.connect(self._take_screenshot)
        self.addAction(f12)

    def _toggle_window_size(self):
        """Toggle between 1280x800 and 800x480 (same as Kivy)."""
        if self.width() == 1280:
            self.resize(800, 480)
        else:
            self.resize(1280, 800)
        logger.info("Window resized to %dx%d", self.width(), self.height())

    def _fake_rfid(self):
        """Trigger a fake RFID read (F11)."""
        self._state_manager.rfid_adapter.triggerFakeRead()
        logger.info("Fake RFID read triggered (F11)")

    def _take_screenshot(self):
        """Save a screenshot (F12)."""
        pixmap = self.grab()
        filename = (
            f"screenshot_{self._state_manager.get_screen_name_for_screenshot()}.png"
        )
        pixmap.save(filename)
        logger.info("Screenshot saved: %s", filename)


# ──────────────────────────────────────────────────────────────────────
# Settings factory (same as Kivy main.py)
# ──────────────────────────────────────────────────────────────────────


def create_settings_manager(settings_path: str) -> SettingsManager:
    """Register all default settings (mirrors Kivy app)."""
    # Imported here to avoid circular dependency at module level
    # (app_types may import other modules that interact with kivy config)
    from app_types import LogLevel  # pylint: disable=import-outside-toplevel

    sm = SettingsManager(settings_path)

    sm.add_float_setting(SettingName.SPILL_FACTOR, 1.05, 1.0, 10.0)
    sm.add_float_setting(SettingName.PURCHASE_FEE, 0.05, 0.0, 1.0)
    sm.add_bool_setting(SettingName.AUTO_LOGOUT_ON_IDLE_ENABLE, True)
    sm.add_float_setting(SettingName.AUTO_LOGOUT_ON_IDLE_TIME, 120.0, 20.0, 600.0)
    sm.add_bool_setting(SettingName.AUTO_LOGOUT_AFTER_PURCHASE, False)
    sm.add_string_setting(SettingName.PAYMENT_SWISH_NUMBER, "0723071057")
    sm.add_bool_setting(SettingName.GO_TO_SPLASH_SCREEN_ON_IDLE_ENABLE, True)
    sm.add_float_setting(SettingName.GO_TO_SPLASH_SCREEN_ON_IDLE_TIME, 10.0, 5.0, 600.0)
    sm.add_bool_setting(SettingName.ORDER_INVENTORY_BY_MOST_PURCHASED, True)
    sm.add_bool_setting(SettingName.ENABLE_GAMBLING, True)
    sm.add_bool_setting(SettingName.EXCITING_GAMBLING, True)
    sm.add_enum_setting(SettingName.LOG_LEVEL, LogLevel.INFO, LogLevel)
    sm.add_bool_setting(SettingName.DEBUG_AUTO_LOGOUT_TIMER, False)

    return sm


# ──────────────────────────────────────────────────────────────────────
# Main
# ──────────────────────────────────────────────────────────────────────


def main():
    # Parse log level
    log_level_str = os.environ.get("SNACKATTACK_LOG_LEVEL", "INFO")
    log_level = getattr(logging, log_level_str.upper(), logging.INFO)
    setup_logging(log_level=log_level)
    logger.info("Snack Attack Track (Qt PoC) starting up")

    parser = argparse.ArgumentParser(description="Snack Attack Track (Qt PoC)")
    parser.add_argument(
        "--settings",
        type=str,
        default="settings.json",
        help="Path to settings JSON file",
    )
    parser.add_argument(
        "--database",
        type=str,
        default="database.db",
        help="Path to SQLite database file",
    )
    parser.add_argument(
        "--inspect",
        action="store_true",
        default=False,
        help="Enable inspection tools (placeholder for future use)",
    )
    args = parser.parse_args()

    # Move to project root so relative paths work
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(script_dir, ".."))
    os.chdir(project_root)

    # Backend
    database = DatabaseConnector(database_path=args.database)
    settings_manager = create_settings_manager(args.settings)
    state_manager = StateManager(database=database, settings_manager=settings_manager)

    # Application
    app = QApplication(sys.argv)
    app.setApplicationName("Snack Attack Track")

    window = MainWindow(state_manager=state_manager, settings_manager=settings_manager)

    # Windowed mode for development (800x480 matches Kivy default)
    window.show()

    logger.info("Qt PoC started successfully")
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
