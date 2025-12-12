import asyncio

import pytest
from kivy.core.window import Window


@pytest.mark.asyncio
async def test_login_by_selecting_user(app_with_users):

    assert app_with_users.screenManager.current == "splashScreen"
    app_with_users.screenManager.current_screen.onPressed()
    assert app_with_users.screenManager.current == "loginScreen"

    usersOnScreen = app_with_users.screenManager.current_screen.ids[
        "LoginScreenUserGridLayout"
    ].children
    assert len(usersOnScreen) > 0

    for userButton in usersOnScreen:
        if "User2FirstName" in userButton.ids.userNameLabel.text:
            userButton.Clicked()
            break

    # Wait for PIN entry popup to appear
    await asyncio.sleep(0.5)

    # Find the PinEntryPopup in Window children (recursively)
    def find_popup(widget):
        if widget.__class__.__name__ == "PinEntryPopup":
            return widget
        if hasattr(widget, "children"):
            for child in widget.children:
                result = find_popup(child)
                if result:
                    return result
        return None

    pin_popup = find_popup(Window)

    if pin_popup:
        # Simulate entering PIN "1234" by calling on_number_pressed
        pin_popup.on_number_pressed(1)
        pin_popup.on_number_pressed(2)
        pin_popup.on_number_pressed(3)
        pin_popup.on_number_pressed(4)
        # Auto-verify is called after 4 digits, wait for it to process
        await asyncio.sleep(0.5)

    assert app_with_users.screenManager.current == "mainUserPage"
    assert (
        "User2FirstName"
        in app_with_users.screenManager.current_screen.ids.header.ids.welcomeTextLabel.text
    )


@pytest.mark.asyncio
async def test_login_from_splash_screen_with_card(app_with_users):
    assert app_with_users.screenManager.current == "splashScreen"

    app_with_users.screenManager.RFIDReader.triggerFakeRead(card_id=555555555)

    assert app_with_users.screenManager.current == "mainUserPage"
    assert (
        "User3FirstName"
        in app_with_users.screenManager.current_screen.ids.header.ids.welcomeTextLabel.text
    )


@pytest.mark.asyncio
async def test_login_from_login_screen_with_card(app_with_users):
    assert app_with_users.screenManager.current == "splashScreen"
    app_with_users.screenManager.current_screen.onPressed()

    await asyncio.sleep(0.5)
    app_with_users.screenManager.RFIDReader.triggerFakeRead(card_id=123456789)

    assert app_with_users.screenManager.current == "mainUserPage"
    assert (
        "User2FirstName"
        in app_with_users.screenManager.current_screen.ids.header.ids.welcomeTextLabel.text
    )
