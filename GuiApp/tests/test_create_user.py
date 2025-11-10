import asyncio
import os

import pytest
import pytest_asyncio
from kivy.core.window import Window

from GuiApp.main import snackAttackTrackApp

# Fixtures are counted as redefine-outer-name
# pylint: disable=redefined-outer-name

# Disable too-many-public-methods for test class
# pylint: disable=too-many-public-methods

Window.size = (800, 480)


async def tear_down(event_loop):
    # Collect all tasks and cancel those that are not 'done'.
    tasks = asyncio.all_tasks(event_loop)
    tasks = [t for t in tasks if not t.done()]
    for task in tasks:
        task.cancel()

    # Wait for all tasks to complete, ignoring any CancelledErrors
    try:
        await asyncio.wait(tasks)
    except asyncio.exceptions.CancelledError:
        pass


@pytest_asyncio.fixture
async def app():
    print("Starting app fixture")
    app = snackAttackTrackApp(
        settings_path="TestCreateUserScreenSettings.json",
        database_path="TestCreateUserScreenDatabase.db",
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


class TestCreateUserScreen:
    def setup_class(self):
        if os.path.exists("TestCreateUserScreenDatabase.db"):
            os.remove("TestCreateUserScreenDatabase.db")
        if os.path.exists("TestCreateUserScreenSettings.json"):
            os.remove("TestCreateUserScreenSettings.json")

    def teardown_class(self):
        if os.path.exists("TestCreateUserScreenDatabase.db"):
            os.remove("TestCreateUserScreenDatabase.db")
        if os.path.exists("TestCreateUserScreenSettings.json"):
            os.remove("TestCreateUserScreenSettings.json")

    @pytest.mark.asyncio
    async def test_create_user_cancel(self, app):

        assert app.screenManager.current == "splashScreen"
        app.screenManager.current_screen.onPressed()
        await asyncio.sleep(1)
        assert app.screenManager.current == "loginScreen"
        app.screenManager.current_screen.createNewUserButtonClicked()
        await asyncio.sleep(1)
        assert app.screenManager.current == "createUserScreen"

        app.screenManager.current_screen.ids.cancelButton.dispatch("on_release")
        await asyncio.sleep(1)
        assert app.screenManager.current == "loginScreen"

    @pytest.mark.asyncio
    async def test_create_user_blank_first_and_last_name(self, app):

        number_of_patrons_before = len(app.screenManager.database.getAllPatrons())

        assert app.screenManager.current == "splashScreen"
        app.screenManager.current_screen.onPressed()
        await asyncio.sleep(1)
        assert app.screenManager.current == "loginScreen"
        app.screenManager.current_screen.createNewUserButtonClicked()
        await asyncio.sleep(1)
        assert app.screenManager.current == "createUserScreen"

        app.screenManager.current_screen.registerUser()
        await asyncio.sleep(1)
        assert app.screenManager.current == "createUserScreen"

        assert (
            len(app.screenManager.database.getAllPatrons()) == number_of_patrons_before
        )

    @pytest.mark.asyncio
    async def test_create_user_blank_first_name(self, app):

        number_of_patrons_before = len(app.screenManager.database.getAllPatrons())

        assert app.screenManager.current == "splashScreen"
        app.screenManager.current_screen.onPressed()
        await asyncio.sleep(1)
        assert app.screenManager.current == "loginScreen"
        app.screenManager.current_screen.createNewUserButtonClicked()
        await asyncio.sleep(1)
        assert app.screenManager.current == "createUserScreen"

        app.screenManager.current_screen.ids.lastNameInput.setText("LastName")
        app.screenManager.current_screen.registerUser()
        await asyncio.sleep(1)
        assert app.screenManager.current == "createUserScreen"

        assert (
            len(app.screenManager.database.getAllPatrons()) == number_of_patrons_before
        )

    @pytest.mark.asyncio
    async def test_create_user_blank_last_name(self, app):

        number_of_patrons_before = len(app.screenManager.database.getAllPatrons())

        assert app.screenManager.current == "splashScreen"
        app.screenManager.current_screen.onPressed()
        await asyncio.sleep(1)
        assert app.screenManager.current == "loginScreen"
        app.screenManager.current_screen.createNewUserButtonClicked()
        await asyncio.sleep(1)
        assert app.screenManager.current == "createUserScreen"

        app.screenManager.current_screen.ids.firstNameInput.setText("FirstName")
        app.screenManager.current_screen.registerUser()
        await asyncio.sleep(1)
        assert app.screenManager.current == "createUserScreen"

        assert (
            len(app.screenManager.database.getAllPatrons()) == number_of_patrons_before
        )

    @pytest.mark.asyncio
    async def test_create_user(self, app):

        number_of_patrons_before = len(app.screenManager.database.getAllPatrons())

        assert app.screenManager.current == "splashScreen"
        app.screenManager.current_screen.onPressed()
        await asyncio.sleep(1)
        assert app.screenManager.current == "loginScreen"
        app.screenManager.current_screen.createNewUserButtonClicked()
        await asyncio.sleep(1)
        assert app.screenManager.current == "createUserScreen"

        app.screenManager.current_screen.ids.firstNameInput.setText("User1FirstName")
        app.screenManager.current_screen.ids.lastNameInput.setText("User1LastName")
        app.screenManager.current_screen.registerUser()
        await asyncio.sleep(1)
        assert app.screenManager.current == "loginScreen"

        assert (
            len(app.screenManager.database.getAllPatrons())
            == number_of_patrons_before + 1
        )

    @pytest.mark.asyncio
    async def test_create_user_with_card_id(self, app):

        number_of_patrons_before = len(app.screenManager.database.getAllPatrons())

        assert app.screenManager.current == "splashScreen"
        app.screenManager.current_screen.onPressed()
        await asyncio.sleep(1)
        assert app.screenManager.current == "loginScreen"
        app.screenManager.current_screen.createNewUserButtonClicked()
        await asyncio.sleep(1)
        assert app.screenManager.current == "createUserScreen"

        app.screenManager.current_screen.ids.firstNameInput.setText("User2FirstName")
        app.screenManager.current_screen.ids.lastNameInput.setText("User2LastName")
        app.screenManager.current_screen.cardRead(123456789)
        app.screenManager.current_screen.registerUser()
        await asyncio.sleep(1)
        assert app.screenManager.current == "loginScreen"

        assert (
            len(app.screenManager.database.getAllPatrons())
            == number_of_patrons_before + 1
        )

    @pytest.mark.asyncio
    async def test_create_user_with_used_card(self, app):

        number_of_patrons_before = len(app.screenManager.database.getAllPatrons())

        assert app.screenManager.database.getPatronIdByCardId(123456789) is not None

        assert app.screenManager.current == "splashScreen"
        app.screenManager.current_screen.onPressed()
        await asyncio.sleep(1)
        assert app.screenManager.current == "loginScreen"
        app.screenManager.current_screen.createNewUserButtonClicked()
        await asyncio.sleep(1)
        assert app.screenManager.current == "createUserScreen"

        app.screenManager.current_screen.ids.firstNameInput.setText("User3FirstName")
        app.screenManager.current_screen.ids.lastNameInput.setText("User3LastName")
        app.screenManager.current_screen.cardRead(123456789)
        app.screenManager.current_screen.registerUser()
        await asyncio.sleep(1)
        assert app.screenManager.current == "createUserScreen"

        assert (
            len(app.screenManager.database.getAllPatrons()) == number_of_patrons_before
        )
