import asyncio

import pytest


@pytest.mark.asyncio
async def test_create_user_cancel(app):

    assert app.screenManager.current == "splashScreen"
    app.screenManager.current_screen.onPressed()

    assert app.screenManager.current == "loginScreen"
    app.screenManager.current_screen.createNewUserButtonClicked()

    assert app.screenManager.current == "createUserScreen"
    app.screenManager.current_screen.ids.cancelButton.dispatch("on_release")

    assert app.screenManager.current == "loginScreen"


@pytest.mark.asyncio
async def test_create_user_blank_first_and_last_name(app):

    number_of_patrons_before = len(app.screenManager.database.getAllPatrons())

    assert app.screenManager.current == "splashScreen"
    app.screenManager.current_screen.onPressed()

    assert app.screenManager.current == "loginScreen"
    app.screenManager.current_screen.createNewUserButtonClicked()

    assert app.screenManager.current == "createUserScreen"
    app.screenManager.current_screen.registerUser()

    assert app.screenManager.current == "createUserScreen"

    assert len(app.screenManager.database.getAllPatrons()) == number_of_patrons_before


@pytest.mark.asyncio
async def test_create_user_blank_first_name(app):

    number_of_patrons_before = len(app.screenManager.database.getAllPatrons())

    assert app.screenManager.current == "splashScreen"
    app.screenManager.current_screen.onPressed()

    assert app.screenManager.current == "loginScreen"
    app.screenManager.current_screen.createNewUserButtonClicked()

    assert app.screenManager.current == "createUserScreen"
    app.screenManager.current_screen.ids.lastNameInput.setText("LastName")
    app.screenManager.current_screen.registerUser()

    assert app.screenManager.current == "createUserScreen"

    assert len(app.screenManager.database.getAllPatrons()) == number_of_patrons_before


@pytest.mark.asyncio
async def test_create_user_blank_last_name(app):

    number_of_patrons_before = len(app.screenManager.database.getAllPatrons())

    assert app.screenManager.current == "splashScreen"
    app.screenManager.current_screen.onPressed()

    assert app.screenManager.current == "loginScreen"
    app.screenManager.current_screen.createNewUserButtonClicked()

    assert app.screenManager.current == "createUserScreen"

    app.screenManager.current_screen.ids.firstNameInput.setText("FirstName")
    app.screenManager.current_screen.registerUser()

    assert app.screenManager.current == "createUserScreen"

    assert len(app.screenManager.database.getAllPatrons()) == number_of_patrons_before


@pytest.mark.asyncio
async def test_create_user(app):

    number_of_patrons_before = len(app.screenManager.database.getAllPatrons())

    assert app.screenManager.current == "splashScreen"
    app.screenManager.current_screen.onPressed()

    assert app.screenManager.current == "loginScreen"
    app.screenManager.current_screen.createNewUserButtonClicked()

    assert app.screenManager.current == "createUserScreen"
    app.screenManager.current_screen.ids.firstNameInput.setText("User1FirstName")
    app.screenManager.current_screen.ids.lastNameInput.setText("User1LastName")
    app.screenManager.current_screen.registerUser()

    assert app.screenManager.current == "loginScreen"

    assert (
        len(app.screenManager.database.getAllPatrons()) == number_of_patrons_before + 1
    )


@pytest.mark.asyncio
async def test_create_user_with_card_id(app):

    number_of_patrons_before = len(app.screenManager.database.getAllPatrons())

    assert app.screenManager.current == "splashScreen"
    app.screenManager.current_screen.onPressed()

    assert app.screenManager.current == "loginScreen"
    app.screenManager.current_screen.createNewUserButtonClicked()

    assert app.screenManager.current == "createUserScreen"
    app.screenManager.current_screen.ids.firstNameInput.setText("User2FirstName")
    app.screenManager.current_screen.ids.lastNameInput.setText("User2LastName")
    app.screenManager.current_screen.cardRead(123456789)
    app.screenManager.current_screen.registerUser()

    assert app.screenManager.current == "loginScreen"

    assert (
        len(app.screenManager.database.getAllPatrons()) == number_of_patrons_before + 1
    )


@pytest.mark.asyncio
async def test_create_user_with_used_card(app_with_users):

    number_of_patrons_before = len(
        app_with_users.screenManager.database.getAllPatrons()
    )

    assert (
        app_with_users.screenManager.database.getPatronIdByCardId(123456789) is not None
    )

    assert app_with_users.screenManager.current == "splashScreen"
    app_with_users.screenManager.current_screen.onPressed()

    assert app_with_users.screenManager.current == "loginScreen"
    app_with_users.screenManager.current_screen.createNewUserButtonClicked()

    assert app_with_users.screenManager.current == "createUserScreen"
    app_with_users.screenManager.current_screen.ids.firstNameInput.setText(
        "User3FirstName"
    )
    app_with_users.screenManager.current_screen.ids.lastNameInput.setText(
        "User3LastName"
    )
    app_with_users.screenManager.current_screen.cardRead(123456789)
    app_with_users.screenManager.current_screen.registerUser()

    assert app_with_users.screenManager.current == "createUserScreen"

    assert (
        len(app_with_users.screenManager.database.getAllPatrons())
        == number_of_patrons_before
    )


@pytest.mark.asyncio
async def test_create_user_with_new_card_from_splash_screen(app):

    number_of_patrons_before = len(app.screenManager.database.getAllPatrons())

    assert app.screenManager.database.getPatronIdByCardId(5555555) is None
    app.screenManager.RFIDReader.triggerFakeRead(card_id=5555555)

    app.screenManager.current_screen.create_or_link_card_popup.ids.createUserButton.dispatch(
        "on_press"
    )

    assert app.screenManager.current == "createUserScreen"

    assert app.screenManager.current_screen.ids.cardIdInput.getText() == "5555555"
    app.screenManager.current_screen.ids.firstNameInput.setText("User4FirstName")
    app.screenManager.current_screen.ids.lastNameInput.setText("User4LastName")
    app.screenManager.current_screen.registerUser()

    assert app.screenManager.current == "loginScreen"

    assert (
        len(app.screenManager.database.getAllPatrons()) == number_of_patrons_before + 1
    )


@pytest.mark.asyncio
async def test_create_user_with_new_card_from_login_screen(app):

    number_of_patrons_before = len(app.screenManager.database.getAllPatrons())

    assert app.screenManager.current == "splashScreen"
    app.screenManager.current_screen.onPressed()

    assert app.screenManager.current == "loginScreen"
    assert app.screenManager.database.getPatronIdByCardId(4444444) is None
    await asyncio.sleep(0.5)
    app.screenManager.RFIDReader.triggerFakeRead(card_id=4444444)
    app.screenManager.current_screen.create_or_link_card_popup.ids.createUserButton.dispatch(
        "on_press"
    )

    assert app.screenManager.current == "createUserScreen"

    assert app.screenManager.current_screen.ids.cardIdInput.getText() == "4444444"
    app.screenManager.current_screen.ids.firstNameInput.setText("User5FirstName")
    app.screenManager.current_screen.ids.lastNameInput.setText("User5LastName")
    app.screenManager.current_screen.registerUser()

    assert (
        len(app.screenManager.database.getAllPatrons()) == number_of_patrons_before + 1
    )
