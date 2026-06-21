"""
pytest-qt conftest for the Qt Snack Attack Track proof of concept.

Provides shared fixtures matching the Kivy test patterns:
    - ``qapp`` (session-scoped QApplication)
    - ``temp_db`` / ``temp_settings`` (temporary files, cleaned up)
    - ``database`` / ``settings_manager`` / ``state_manager``
    - ``app_with_nothing`` (empty database)
    - ``app_with_users`` (3 pre-created users)
    - ``app_with_users_on_login`` (pre-navigated to login screen)
    - ``app_on_create_user`` (pre-navigated to create user screen)
"""

import json
import os
import sys
import tempfile

import pytest
from PySide6.QtWidgets import QApplication

# Ensure GuiApp is importable
_gui_app_dir = os.path.join(os.path.dirname(__file__), "..", "..", "GuiApp")
if _gui_app_dir not in sys.path:
    sys.path.insert(0, os.path.abspath(_gui_app_dir))

# Ensure QtApp is importable
_qt_app_dir = os.path.join(os.path.dirname(__file__), "..")
if _qt_app_dir not in sys.path:
    sys.path.insert(0, os.path.abspath(_qt_app_dir))

os.environ["KIVY_NO_ARGS"] = "1"
os.environ["MOCK_RFID_READER"] = "1"

# pylint: disable=wrong-import-position,redefined-outer-name

from app_types import Credits
from database import DatabaseConnector

from QtApp.main import create_settings_manager
from QtApp.stateManager import StateManager


# ─────────────────────────────────────────────────────────────────────────────
# Session-scoped QApplication
# ─────────────────────────────────────────────────────────────────────────────


@pytest.fixture(scope="session")
def qapp():
    """Create a QApplication instance for the test session."""
    # Force offscreen platform
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    yield app
    # No need to call app.quit() — pytest-qt handles cleanup


# ─────────────────────────────────────────────────────────────────────────────
# Temporary files
# ─────────────────────────────────────────────────────────────────────────────


@pytest.fixture
def temp_db():
    """Yield a temporary database file path, then delete it."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = f.name
    yield db_path
    if os.path.exists(db_path):
        os.unlink(db_path)


@pytest.fixture
def temp_settings():
    """Yield a temporary settings JSON file path, then delete it."""
    with tempfile.NamedTemporaryFile(
        suffix=".json", mode="w", delete=False, encoding="utf-8"
    ) as f:
        json.dump({}, f)
        settings_path = f.name
    yield settings_path
    if os.path.exists(settings_path):
        os.unlink(settings_path)


# ─────────────────────────────────────────────────────────────────────────────
# Core fixtures
# ─────────────────────────────────────────────────────────────────────────────


@pytest.fixture
def database(temp_db):
    """Create a DatabaseConnector with a temporary database."""
    db = DatabaseConnector(database_path=temp_db)
    yield db
    db.close()


@pytest.fixture
def settings_manager(temp_settings):
    """Create a SettingsManager with all default settings registered."""
    sm = create_settings_manager(temp_settings)
    yield sm


@pytest.fixture
def state_manager(database, settings_manager):
    """Create a StateManager without automatically starting RFID."""
    sm = StateManager(database=database, settings_manager=settings_manager)
    yield sm


# ─────────────────────────────────────────────────────────────────────────────
# App fixtures
# ─────────────────────────────────────────────────────────────────────────────


def _create_app(
    database, settings_manager, state_manager, qtbot=None
):  # pylint: disable=import-outside-toplevel
    """Helper to build the test application with all screens."""
    from PySide6.QtWidgets import (
        QMainWindow,
        QStackedWidget,
    )  # pylint: disable=import-outside-toplevel

    from QtApp.screens.splashScreen import (
        SplashScreen,
    )  # pylint: disable=import-outside-toplevel
    from QtApp.screens.loginScreen import (
        LoginScreen,
    )  # pylint: disable=import-outside-toplevel
    from QtApp.screens.createUserScreen import (
        CreateUserScreen,
    )  # pylint: disable=import-outside-toplevel
    from QtApp.screens.mainUserScreen import (
        MainUserScreen,
    )  # pylint: disable=import-outside-toplevel

    window = QMainWindow()
    window.state_manager = state_manager
    window.stacked_widget = QStackedWidget(window)
    window.setCentralWidget(window.stacked_widget)

    state_manager.set_stacked_widget(window.stacked_widget)

    screens = [
        SplashScreen(state_manager),
        LoginScreen(state_manager),
        CreateUserScreen(state_manager),
        MainUserScreen(state_manager),
    ]
    for screen in screens:
        window.stacked_widget.addWidget(screen)

    # Start on splash
    state_manager.transition_to_screen("splashScreen")

    return window


def _add_users(database):
    """Add 3 test users matching the Kivy test pattern."""
    database.addPatron("User1FirstName", "User1LastName", "111111111")
    database.addPatron("User2FirstName", "User2LastName", "222222222")
    database.addPatron("User3FirstName", "User3LastName", "555555555")
    # Give User3 some credits
    database.addCredits(3, Credits("11.00"))


@pytest.fixture
def app_with_nothing(database, settings_manager, state_manager, qtbot):
    """MainWindow with empty database (no users/snacks)."""
    window = _create_app(database, settings_manager, state_manager, qtbot)
    yield window


@pytest.fixture
def app_with_users(database, settings_manager, state_manager, qtbot):
    """MainWindow with 3 pre-created users."""
    _add_users(database)
    window = _create_app(database, settings_manager, state_manager, qtbot)
    yield window


def _navigate_to(window, screen_name: str, qtbot):
    """Helper: navigate to a screen and wait for it."""
    window.state_manager.transition_to_screen(screen_name)
    # Wait for the transition to take effect
    qtbot.waitUntil(
        lambda: window.stacked_widget.currentWidget() is not None
        and window.stacked_widget.currentWidget().objectName() == screen_name,
        timeout=2000,
    )


@pytest.fixture
def app_with_users_on_login(app_with_users, qtbot):
    """Pre-navigated to the login screen."""
    _navigate_to(app_with_users, "loginScreen", qtbot)
    yield app_with_users


@pytest.fixture
def app_on_create_user(app_with_nothing, qtbot):
    """Pre-navigated to the create user screen."""
    _navigate_to(app_with_nothing, "createUserScreen", qtbot)
    yield app_with_nothing
