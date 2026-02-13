import asyncio
import os

import pytest_asyncio
from kivy.core.window import Window

from GuiApp.main import snackAttackTrackApp
from GuiApp.widgets.editSnacksScreen import EditSnacksScreen

# Fixtures are counted as redefine-outer-name
# pylint: disable=redefined-outer-name

# Disable too-many-public-methods for test class
# pylint: disable=too-many-public-methods

Window.size = (1280, 800)


async def tear_down(event_loop):
    # Collect all tasks and cancel those that are not 'done'.
    tasks = asyncio.all_tasks(event_loop)
    tasks = [t for t in tasks if not t.done()]
    for task in tasks:
        task.cancel()

    if os.path.exists("PytestDatabase.db"):
        os.remove("PytestDatabase.db")
    if os.path.exists("PytestSettings.json"):
        os.remove("PytestSettings.json")

    # Wait for all tasks to complete, ignoring any CancelledErrors
    try:
        await asyncio.wait(tasks)
    except asyncio.exceptions.CancelledError:
        pass


@pytest_asyncio.fixture
async def app_with_nothing():
    print("Starting app fixture")

    if os.path.exists("PytestDatabase.db"):
        os.remove("PytestDatabase.db")
    if os.path.exists("PytestSettings.json"):
        os.remove("PytestSettings.json")

    app = snackAttackTrackApp(
        settings_path="PytestSettings.json",
        database_path="PytestDatabase.db",
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
        first_name="User1FirstName", last_name="User1LastName", employee_id=987654321
    )
    app_with_nothing.screenManager.database.addPatron(
        first_name="User2FirstName", last_name="User2LastName", employee_id=123456789
    )
    app_with_nothing.screenManager.database.addPatron(
        first_name="User3FirstName", last_name="User3LastName", employee_id=555555555
    )
    return app_with_nothing


@pytest_asyncio.fixture
async def app(app_with_only_users):
    app_with_only_users.screenManager.database.addSnack("Snack1", 42, "TestImage1", 10)
    app_with_only_users.screenManager.database.addSnack("Snack2", 5, "TestImage2", 12)
    app_with_only_users.screenManager.database.addSnack("Snack3", 16, "TestImage3", 15)

    return app_with_only_users


@pytest_asyncio.fixture
async def app_on_add_snack_screen(app):

    assert app.screenManager.current == "splashScreen"

    assert app.screenManager.database.getPatronIdByCardId(555555555) is not None

    app.screenManager.RFIDReader.triggerFakeRead(card_id=555555555)

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
