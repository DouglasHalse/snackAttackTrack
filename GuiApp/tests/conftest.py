# -- Kivy config MUST be set before any Kivy imports --
# Prevents the Clock from pausing when the window loses focus,
# which would cause screen transitions to never complete and tests to fail.
# pylint: disable=wrong-import-position,wrong-import-order,ungrouped-imports
from kivy.config import Config

Config.set("kivy", "pause_on_minimize", "0")

import asyncio
import logging
import os
import time

import pytest
import pytest_asyncio
from kivy.core.window import Window

from app_types import Credits
from GuiApp.main import snackAttackTrackApp
from GuiApp.widgets.editSnacksScreen import EditSnacksScreen
from tests.SchemaBuilder import SchemaBuilder

# Fixtures are counted as redefine-outer-name
# pylint: disable=redefined-outer-name

# Disable too-many-public-methods for test class
# pylint: disable=too-many-public-methods

TEST_DB = "PytestDatabase.db"
TEST_SETTINGS = "PytestSettings.json"

Window.size = (1280, 800)


import logger as app_logger


@pytest.fixture
def log_dir(tmp_path):
    """Set up a temporary log directory and patch logger constants."""
    log_path = tmp_path / "logs"
    log_path.mkdir()
    app_logger.LOG_DIR = str(log_path)
    app_logger.LOG_FILE = str(log_path / "snackattack.log")
    yield log_path
    app_logger.LOG_DIR = "logs"
    app_logger.LOG_FILE = "logs/snackattack.log"


@pytest.fixture
def configured_logger(log_dir):
    """Set up logging and clean up after."""
    root = logging.getLogger()
    root.handlers.clear()
    app_logger.setup_logging(logging.DEBUG)
    yield root
    root.handlers.clear()


def pytest_addoption(parser):
    """Add the --schema-version option for testing different migration paths."""
    parser.addoption(
        "--schema-version",
        default="v3",
        choices=["v1", "v2", "v3"],
        help="Schema version to start from: v1, v2, or v3 (default: v3)",
    )


async def tear_down(event_loop):
    """Cancel all pending asyncio tasks and clean up test artifacts."""
    try:
        current_task = asyncio.current_task(event_loop)
        tasks = asyncio.all_tasks(event_loop)
        tasks = [t for t in tasks if not t.done() and t is not current_task]

        for task in tasks:
            task.cancel()

        if tasks:
            await asyncio.wait(tasks, timeout=5.0)
    except Exception:  # pylint: disable=broad-exception-caught
        pass

    for path in (TEST_DB, TEST_SETTINGS):
        _remove_if_exists(path)


def _remove_if_exists(path, retries=3, delay=0.2):
    """Try to remove a file, retrying on PermissionError (Windows SQLite)."""
    for attempt in range(retries):
        try:
            if os.path.exists(path):
                os.remove(path)
            return
        except OSError:
            if attempt < retries - 1:
                time.sleep(delay)


@pytest.fixture(scope="session")
def schema_version(request):
    """Return the --schema-version option value (v1, v2, or v3)."""
    return request.config.getoption("--schema-version")


@pytest_asyncio.fixture
async def app_with_nothing(schema_version):
    _remove_if_exists(TEST_DB)
    _remove_if_exists(TEST_SETTINGS)

    # Build a pre-migration database if schema_version is not v3
    # (schema only, no seed data — fixtures add their own data)
    if schema_version != "v3":
        SchemaBuilder.build(TEST_DB, schema_version, seed=False)

    app = snackAttackTrackApp(
        settings_path=TEST_SETTINGS,
        database_path=TEST_DB,
    )
    # start the Kivy event loop in background so tests can drive it
    asyncio.create_task(app.async_run(), name="kivy_event_loop")
    # wait a bit for the window and initial frames to appear
    await asyncio.sleep(0.5)

    try:
        yield app
    finally:
        app.screenManager.database.close()
        await tear_down(asyncio.get_event_loop())


@pytest_asyncio.fixture
async def app_with_only_users(app_with_nothing):
    app_with_nothing.screenManager.database.addPatron(
        first_name="User1FirstName", last_name="User1LastName", employee_id="987654321"
    )
    app_with_nothing.screenManager.database.addPatron(
        first_name="User2FirstName", last_name="User2LastName", employee_id="123456789"
    )
    app_with_nothing.screenManager.database.addPatron(
        first_name="User3FirstName", last_name="User3LastName", employee_id="555555555"
    )

    # Give user 3 20 credits so they can buy snacks in tests
    app_with_nothing.screenManager.database.addCredits(
        userId=app_with_nothing.screenManager.database.getPatronIdByCardId("555555555"),
        amount=Credits("11.00"),
    )

    return app_with_nothing


@pytest_asyncio.fixture
async def app(app_with_only_users):
    app_with_only_users.screenManager.database.addSnack(
        "Snack1", 42, "TestImage1", Credits("10.00")
    )
    app_with_only_users.screenManager.database.addSnack(
        "Snack2", 5, "TestImage2", Credits("12.00")
    )
    app_with_only_users.screenManager.database.addSnack(
        "Snack3", 16, "TestImage3", Credits("15.00")
    )

    return app_with_only_users


@pytest_asyncio.fixture
async def app_on_add_snack_screen(app):

    assert app.screenManager.current == "splashScreen"

    assert app.screenManager.database.getPatronIdByCardId("555555555") is not None

    app.screenManager.RFIDReader.triggerFakeRead(card_id="555555555")

    assert app.screenManager.current == "mainUserPage"

    app.screenManager.current_screen.ids.header.settings_button.dispatch("on_release")

    assert app.screenManager.current == "adminScreen"

    app.screenManager.current_screen.ids.editSnacksOption.dispatch("on_release")

    assert app.screenManager.current == "editSnacksScreen"

    app.screenManager.current_screen.onEntryPressed(
        identifier=EditSnacksScreen.ADD_SNACK_ENTRY_IDENTIFIER
    )

    assert app.screenManager.current == "addSnackScreen"

    return app


@pytest_asyncio.fixture
async def app_on_edit_snack_screen(app):

    assert app.screenManager.current == "splashScreen"

    assert app.screenManager.database.getPatronIdByCardId("555555555") is not None

    app.screenManager.RFIDReader.triggerFakeRead(card_id="555555555")

    assert app.screenManager.current == "mainUserPage"

    app.screenManager.current_screen.ids.header.settings_button.dispatch("on_release")

    assert app.screenManager.current == "adminScreen"

    app.screenManager.current_screen.ids.editSnacksOption.dispatch("on_release")

    assert app.screenManager.current == "editSnacksScreen"

    snacks = app.screenManager.database.getAllSnacks()
    assert len(snacks) > 0

    app.screenManager.current_screen.onEntryPressed(identifier=snacks[0].snackId)

    assert app.screenManager.current == "editSnackScreen"

    return app


@pytest_asyncio.fixture
async def app_on_buy_screen(app):

    assert app.screenManager.current == "splashScreen"

    assert app.screenManager.database.getPatronIdByCardId("555555555") is not None

    app.screenManager.RFIDReader.triggerFakeRead(card_id="555555555")

    assert app.screenManager.current == "mainUserPage"

    app.screenManager.current_screen.ids.buyOption.dispatch("on_release")

    assert app.screenManager.current == "buyScreen"

    await asyncio.sleep(0.5)

    return app


@pytest_asyncio.fixture
async def app_on_user_statistics_screen(app):

    assert app.screenManager.current == "splashScreen"

    assert app.screenManager.database.getPatronIdByCardId("555555555") is not None

    app.screenManager.RFIDReader.triggerFakeRead(card_id="555555555")

    assert app.screenManager.current == "mainUserPage"

    # Go to settings (admin screen)
    app.screenManager.current_screen.ids.header.settings_button.dispatch("on_release")
    await asyncio.sleep(0.5)

    assert app.screenManager.current == "adminScreen"

    # Go back to main user page
    app.screenManager.current_screen.ids.header.ids.backButton.dispatch("on_release")
    await asyncio.sleep(0.5)

    assert app.screenManager.current == "mainUserPage"

    # Go to profile screen
    app.screenManager.current_screen.ids.profileOption.dispatch("on_release")
    await asyncio.sleep(0.5)

    assert app.screenManager.current == "profileScreen"

    # Open user statistics
    app.screenManager.current_screen.ids.statisticsOption.dispatch("on_release")
    await asyncio.sleep(0.5)

    assert app.screenManager.current == "userStatisticsScreen"

    return app


@pytest_asyncio.fixture
async def app_on_store_statistics_screen(app):

    assert app.screenManager.current == "splashScreen"

    assert app.screenManager.database.getPatronIdByCardId("555555555") is not None

    app.screenManager.RFIDReader.triggerFakeRead(card_id="555555555")

    assert app.screenManager.current == "mainUserPage"

    # Go to admin screen
    app.screenManager.current_screen.ids.header.settings_button.dispatch("on_release")
    await asyncio.sleep(0.5)

    assert app.screenManager.current == "adminScreen"

    # Open store statistics
    app.screenManager.current_screen.ids.storeStatsOption.dispatch("on_release")
    await asyncio.sleep(0.5)

    assert app.screenManager.current == "storeStatsScreen"

    return app
