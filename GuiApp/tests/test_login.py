import asyncio

import pytest


@pytest.mark.asyncio
async def test_login_by_selecting_user(app_with_only_users):

    assert app_with_only_users.screenManager.current == "splashScreen"
    app_with_only_users.screenManager.current_screen.onPressed()
    assert app_with_only_users.screenManager.current == "loginScreen"

    usersOnScreen = app_with_only_users.screenManager.current_screen.ids[
        "LoginScreenUserGridLayout"
    ].children
    assert len(usersOnScreen) > 0

    for userButton in usersOnScreen:
        if userButton.first_name == "User2FirstName":
            userButton.ids.clickableLayout.dispatch("on_press")
            break

    assert app_with_only_users.screenManager.current == "mainUserPage"
    assert (
        "User2FirstName"
        in app_with_only_users.screenManager.current_screen.ids.header.ids.welcomeTextLabel.text
    )


@pytest.mark.asyncio
async def test_login_from_splash_screen_with_card(app_with_only_users):
    assert app_with_only_users.screenManager.current == "splashScreen"

    app_with_only_users.screenManager.RFIDReader.triggerFakeRead(card_id=555555555)

    assert app_with_only_users.screenManager.current == "mainUserPage"
    assert (
        "User3FirstName"
        in app_with_only_users.screenManager.current_screen.ids.header.ids.welcomeTextLabel.text
    )


@pytest.mark.asyncio
async def test_login_from_login_screen_with_card(app_with_only_users):
    assert app_with_only_users.screenManager.current == "splashScreen"
    app_with_only_users.screenManager.current_screen.onPressed()

    await asyncio.sleep(0.5)
    app_with_only_users.screenManager.RFIDReader.triggerFakeRead(card_id=123456789)

    assert app_with_only_users.screenManager.current == "mainUserPage"
    assert (
        "User2FirstName"
        in app_with_only_users.screenManager.current_screen.ids.header.ids.welcomeTextLabel.text
    )
