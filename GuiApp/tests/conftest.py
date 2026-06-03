# -- Kivy config MUST be set before any Kivy imports --
# Prevents the Clock from pausing when the window loses focus,
# which would cause screen transitions to never complete and tests to fail.
# pylint: disable=wrong-import-position,wrong-import-order,ungrouped-imports
from kivy.config import Config

Config.set("kivy", "pause_on_minimize", "0")

import asyncio
import os
import sqlite3
import time

import pytest_asyncio
from kivy.core.window import Window

from app_types import Credits
from GuiApp.main import snackAttackTrackApp
from GuiApp.widgets.editSnacksScreen import EditSnacksScreen

# Fixtures are counted as redefine-outer-name
# pylint: disable=redefined-outer-name

# Disable too-many-public-methods for test class
# pylint: disable=too-many-public-methods

TEST_DB = "PytestDatabase.db"
TEST_SETTINGS = "PytestSettings.json"
TEST_LEGACY = os.environ.get("TEST_LEGACY_DB") == "1"

Window.size = (1280, 800)


V1_SCHEMA = (
    "CREATE TABLE IF NOT EXISTS Patrons ("
    "PatronID INTEGER PRIMARY KEY AUTOINCREMENT, "
    "FirstName TEXT NOT NULL, LastName TEXT NOT NULL, EmployeeID TEXT NOT NULL, "
    "TotalCredits REAL NOT NULL DEFAULT 0.0); "
    "CREATE TABLE IF NOT EXISTS Snacks ("
    "ItemID INTEGER PRIMARY KEY AUTOINCREMENT, "
    "ItemName TEXT NOT NULL, Quantity INTEGER NOT NULL, ImageID TEXT NOT NULL, "
    "PricePerItem REAL NOT NULL); "
    "CREATE TABLE IF NOT EXISTS Transactions ("
    "TransactionID INTEGER PRIMARY KEY AUTOINCREMENT, "
    "TransactionType TEXT NOT NULL, PatronID INTEGER NOT NULL, "
    "TransactionDate TEXT NOT NULL, AmountBeforeTransaction REAL NOT NULL, "
    "AmountAfterTransaction REAL NOT NULL, "
    "FOREIGN KEY(PatronID) REFERENCES Patrons(PatronID)); "
    "CREATE TABLE IF NOT EXISTS TransactionItems ("
    "TransactionItemId INTEGER PRIMARY KEY AUTOINCREMENT, "
    "TransactionID INTEGER NOT NULL, ItemName TEXT NOT NULL, "
    "Quantity INTEGER NOT NULL, PricePerItem REAL NOT NULL, "
    "FOREIGN KEY(TransactionID) REFERENCES Transactions(TransactionID)); "
    "CREATE TABLE IF NOT EXISTS AddedSnacks ("
    "AddedID INTEGER PRIMARY KEY AUTOINCREMENT, "
    "SnackName TEXT NOT NULL, AddedDate TEXT NOT NULL, "
    "Quantity INTEGER NOT NULL, Value REAL NOT NULL); "
    "CREATE TABLE IF NOT EXISTS LostSnacks ("
    "LostID INTEGER PRIMARY KEY AUTOINCREMENT, "
    "SnackName TEXT NOT NULL, Reason INTEGER NOT NULL, "
    "LostDate TEXT NOT NULL, Quantity INTEGER NOT NULL, Value REAL NOT NULL);"
)


def _seed_v1_database(db_path: str):
    """
    Create a database with the v1 schema (REAL credits) and no settings
    table, so the app's auto-migration runs on startup.
    No seed rows — tests add their own data after migration.
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.executescript(V1_SCHEMA)
    conn.commit()
    conn.close()


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


@pytest_asyncio.fixture
async def app_with_nothing():
    _remove_if_exists(TEST_DB)
    _remove_if_exists(TEST_SETTINGS)

    if TEST_LEGACY:
        _seed_v1_database(TEST_DB)

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

    # Give user 3 credits so they can buy snacks in tests
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
