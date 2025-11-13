import asyncio

import pytest

# Fixtures are counted as redefine-outer-name
# pylint: disable=redefined-outer-name

# Disable too-many-public-methods for test class
# pylint: disable=too-many-public-methods


class TestLogin:
    @pytest.mark.asyncio
    async def test_login_by_selecting_user(self, app_with_users):

        assert app_with_users.screenManager.current == "splashScreen"
        app_with_users.screenManager.current_screen.onPressed()
        assert app_with_users.screenManager.current == "loginScreen"

        usersOnScreen = app_with_users.screenManager.current_screen.ids[
            "LoginScreenUserGridLayout"
        ].children
        assert len(usersOnScreen) > 0

        for userButton in usersOnScreen:
            if userButton.ids.userNameLabel.text == "User2FirstName":
                userButton.ids.clickableLayout.dispatch("on_press")
                break

        assert app_with_users.screenManager.current == "mainUserPage"
        assert (
            "User2FirstName"
            in app_with_users.screenManager.current_screen.ids.header.ids.welcomeTextLabel.text
        )

    @pytest.mark.asyncio
    async def test_login_from_splash_screen_with_card(self, app_with_users):
        assert app_with_users.screenManager.current == "splashScreen"

        app_with_users.screenManager.RFIDReader.triggerFakeRead(card_id=555555555)

        assert app_with_users.screenManager.current == "mainUserPage"
        assert (
            "User3FirstName"
            in app_with_users.screenManager.current_screen.ids.header.ids.welcomeTextLabel.text
        )

    @pytest.mark.asyncio
    async def test_login_from_login_screen_with_card(self, app_with_users):
        assert app_with_users.screenManager.current == "splashScreen"
        app_with_users.screenManager.current_screen.onPressed()

        await asyncio.sleep(0.5)
        app_with_users.screenManager.RFIDReader.triggerFakeRead(card_id=123456789)

        assert app_with_users.screenManager.current == "mainUserPage"
        assert (
            "User2FirstName"
            in app_with_users.screenManager.current_screen.ids.header.ids.welcomeTextLabel.text
        )
