import os
import asyncio
import pytest
from kivy.core.window import Window
from main import snackAttackTrackApp

# Change working directory up one level
os.chdir(os.path.dirname(os.path.abspath(__file__)) + "/..")

# Add path to sys.path
import sys

sys.path.append(os.getcwd())

DELAY = 1
"""
@pytest.fixture(scope="function")
def event_loop():
    loop = asyncio.get_event_loop()
    yield loop
    loop.close()
"""


@pytest.fixture(scope="function")
def app_instance():
    """
    Fixture to create and return an instance of the app.
    """

    app = snackAttackTrackApp()
    return app


async def stop_app(app_instance):
    """
    Stop the app and clean up resources.
    """
    # Stop the app
    if app_instance is not None:
        print("Stopping the app...")
        app_instance.stop()

    # Allow time for cleanup
    await asyncio.sleep(1)

    # Cancel any pending asyncio tasks
    pending_tasks = [task for task in asyncio.all_tasks() if not task.done()]
    for task in pending_tasks:
        if task is not asyncio.current_task():
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass

    loop = asyncio.get_event_loop()
    loop.close()

    await asyncio.sleep(5)

    # Stop the Kivy event loop explicitly
    from kivy.base import EventLoop

    if EventLoop.status == "started":
        EventLoop.close()

    # Force garbage collection to clean up lingering references
    import gc

    gc.collect()


"""
@pytest.fixture
async def configured_app(app_instance):

    # Set the window size
    Window.size = (800, 480)

    # Launch the app asynchronously
    loop = asyncio.get_event_loop()
    app_task = loop.create_task(app_instance.async_run())
    await asyncio.sleep(1)  # Allow the app to initialize

    # Yield the app instance to the test
    try:
        yield app_instance
    finally:
        # Cleanup: Stop the app and cancel the task
        app_instance.stop()
        await asyncio.sleep(1)  # Allow time for cleanup
        app_task.cancel()
        try:
            await app_task
        except asyncio.CancelledError:
            pass
"""


async def launch_and_configure_app(app_instance):

    # Clear the database
    if os.path.exists("database.db"):
        os.remove("database.db")

    # Set the window size
    Window.size = (800, 480)

    # Start the app asynchronously
    loop = asyncio.get_event_loop()
    loop.create_task(app_instance.async_run())

    # Allow the app to initialize
    await asyncio.sleep(1)


async def tap_on_splash_screen(app):
    """
    Simulate tapping on the splash screen.
    """
    assert app.screenManager.current == "splashScreen"

    app.screenManager.current_screen.onPressed()
    await asyncio.sleep(DELAY)

    assert app.screenManager.current == "loginScreen"


async def tap_on_create_user_button(app):
    """
    Simulate tapping on the create user button.
    """
    assert app.screenManager.current == "loginScreen"

    app.screenManager.current_screen.createNewUserButtonClicked()
    await asyncio.sleep(DELAY)

    assert app.screenManager.current == "createUserScreen"


async def tap_on_register_button(app):
    """
    Simulate tapping on the register button.
    """
    assert app.screenManager.current == "createUserScreen"

    app.screenManager.current_screen.registerUser()
    await asyncio.sleep(DELAY)

    assert app.screenManager.current == "loginScreen"


async def focus_on_text_input_with_header(app, text_input_id):
    """
    Focus on a TextInput widget.
    """
    app.screenManager.current_screen.ids[text_input_id].ids.input.focus = True

    await asyncio.sleep(DELAY)


async def get_text_from_input_with_header(app, text_input_id):
    """
    Get the TextInput popup.
    """
    text = app.screenManager.current_screen.ids[text_input_id].ids.input.text

    await asyncio.sleep(DELAY)

    return text


async def enter_text_in_text_input_with_header_popup(app, text_input_id, text):
    """
    Enter text in a TextInput widget.
    """
    app.screenManager.current_screen.ids[
        text_input_id
    ].textInputPopup.ids.textInput.insertText(text)

    await asyncio.sleep(DELAY)


async def dismiss_text_input_with_header_popup(app, text_input_id):
    """
    Dismiss the TextInput popup.
    """
    app.screenManager.current_screen.ids[text_input_id].textInputPopup.dismiss()

    await asyncio.sleep(DELAY)


async def fake_rfid_read(app, card_id):
    """
    Simulate a fake RFID read.
    """
    app.screenManager.RFIDReader.triggerFakeReadWithId(card_id)

    await asyncio.sleep(DELAY)
