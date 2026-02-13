import asyncio

import pytest


@pytest.mark.asyncio
async def test_create_user_cancel(app_with_nothing):

    assert app_with_nothing.screenManager.current == "splashScreen"
    app_with_nothing.screenManager.current_screen.onPressed()

    assert app_with_nothing.screenManager.current == "loginScreen"
    app_with_nothing.screenManager.current_screen.createNewUserButtonClicked()

    assert app_with_nothing.screenManager.current == "createUserScreen"
    app_with_nothing.screenManager.current_screen.ids.cancelButton.dispatch(
        "on_release"
    )

    assert app_with_nothing.screenManager.current == "loginScreen"


@pytest.mark.asyncio
async def test_create_user_blank_first_and_last_name(app_with_nothing):

    number_of_patrons_before = len(
        app_with_nothing.screenManager.database.getAllPatrons()
    )

    assert app_with_nothing.screenManager.current == "splashScreen"
    app_with_nothing.screenManager.current_screen.onPressed()

    assert app_with_nothing.screenManager.current == "loginScreen"
    app_with_nothing.screenManager.current_screen.createNewUserButtonClicked()

    assert app_with_nothing.screenManager.current == "createUserScreen"
    app_with_nothing.screenManager.current_screen.registerUser()

    assert app_with_nothing.screenManager.current == "createUserScreen"

    assert (
        len(app_with_nothing.screenManager.database.getAllPatrons())
        == number_of_patrons_before
    )


@pytest.mark.asyncio
async def test_create_user_blank_first_name(app_with_nothing):

    number_of_patrons_before = len(
        app_with_nothing.screenManager.database.getAllPatrons()
    )

    assert app_with_nothing.screenManager.current == "splashScreen"
    app_with_nothing.screenManager.current_screen.onPressed()

    assert app_with_nothing.screenManager.current == "loginScreen"
    app_with_nothing.screenManager.current_screen.createNewUserButtonClicked()

    assert app_with_nothing.screenManager.current == "createUserScreen"
    app_with_nothing.screenManager.current_screen.ids.lastNameInput.setText("LastName")
    app_with_nothing.screenManager.current_screen.registerUser()

    assert app_with_nothing.screenManager.current == "createUserScreen"

    assert (
        len(app_with_nothing.screenManager.database.getAllPatrons())
        == number_of_patrons_before
    )


@pytest.mark.asyncio
async def test_create_user_blank_last_name(app_with_nothing):

    number_of_patrons_before = len(
        app_with_nothing.screenManager.database.getAllPatrons()
    )

    assert app_with_nothing.screenManager.current == "splashScreen"
    app_with_nothing.screenManager.current_screen.onPressed()

    assert app_with_nothing.screenManager.current == "loginScreen"
    app_with_nothing.screenManager.current_screen.createNewUserButtonClicked()

    assert app_with_nothing.screenManager.current == "createUserScreen"

    app_with_nothing.screenManager.current_screen.ids.firstNameInput.setText(
        "FirstName"
    )
    app_with_nothing.screenManager.current_screen.registerUser()

    assert app_with_nothing.screenManager.current == "createUserScreen"

    assert (
        len(app_with_nothing.screenManager.database.getAllPatrons())
        == number_of_patrons_before
    )


@pytest.mark.asyncio
async def test_create_user(app_with_nothing):

    number_of_patrons_before = len(
        app_with_nothing.screenManager.database.getAllPatrons()
    )

    assert app_with_nothing.screenManager.current == "splashScreen"
    app_with_nothing.screenManager.current_screen.onPressed()

    assert app_with_nothing.screenManager.current == "loginScreen"
    app_with_nothing.screenManager.current_screen.createNewUserButtonClicked()

    assert app_with_nothing.screenManager.current == "createUserScreen"
    app_with_nothing.screenManager.current_screen.ids.firstNameInput.setText(
        "User1FirstName"
    )
    app_with_nothing.screenManager.current_screen.ids.lastNameInput.setText(
        "User1LastName"
    )
    app_with_nothing.screenManager.current_screen.registerUser()

    assert app_with_nothing.screenManager.current == "loginScreen"

    assert (
        len(app_with_nothing.screenManager.database.getAllPatrons())
        == number_of_patrons_before + 1
    )


@pytest.mark.asyncio
async def test_create_user_with_card_id(app_with_nothing):

    number_of_patrons_before = len(
        app_with_nothing.screenManager.database.getAllPatrons()
    )

    assert app_with_nothing.screenManager.current == "splashScreen"
    app_with_nothing.screenManager.current_screen.onPressed()

    assert app_with_nothing.screenManager.current == "loginScreen"
    app_with_nothing.screenManager.current_screen.createNewUserButtonClicked()

    assert app_with_nothing.screenManager.current == "createUserScreen"
    app_with_nothing.screenManager.current_screen.ids.firstNameInput.setText(
        "User2FirstName"
    )
    app_with_nothing.screenManager.current_screen.ids.lastNameInput.setText(
        "User2LastName"
    )
    app_with_nothing.screenManager.current_screen.cardRead(123456789)
    app_with_nothing.screenManager.current_screen.registerUser()

    assert app_with_nothing.screenManager.current == "loginScreen"

    assert (
        len(app_with_nothing.screenManager.database.getAllPatrons())
        == number_of_patrons_before + 1
    )


@pytest.mark.asyncio
async def test_create_user_with_used_card(app_with_only_users):

    number_of_patrons_before = len(
        app_with_only_users.screenManager.database.getAllPatrons()
    )

    assert (
        app_with_only_users.screenManager.database.getPatronIdByCardId(123456789)
        is not None
    )

    assert app_with_only_users.screenManager.current == "splashScreen"
    app_with_only_users.screenManager.current_screen.onPressed()

    assert app_with_only_users.screenManager.current == "loginScreen"
    app_with_only_users.screenManager.current_screen.createNewUserButtonClicked()

    assert app_with_only_users.screenManager.current == "createUserScreen"
    app_with_only_users.screenManager.current_screen.ids.firstNameInput.setText(
        "User3FirstName"
    )
    app_with_only_users.screenManager.current_screen.ids.lastNameInput.setText(
        "User3LastName"
    )
    app_with_only_users.screenManager.current_screen.cardRead(123456789)
    app_with_only_users.screenManager.current_screen.registerUser()

    assert app_with_only_users.screenManager.current == "createUserScreen"

    assert (
        len(app_with_only_users.screenManager.database.getAllPatrons())
        == number_of_patrons_before
    )


@pytest.mark.asyncio
async def test_create_user_with_new_card_from_splash_screen(app_with_nothing):

    number_of_patrons_before = len(
        app_with_nothing.screenManager.database.getAllPatrons()
    )

    assert app_with_nothing.screenManager.database.getPatronIdByCardId(5555555) is None
    app_with_nothing.screenManager.RFIDReader.triggerFakeRead(card_id=5555555)

    app_with_nothing.screenManager.current_screen.create_or_link_card_popup.ids.createUserButton.dispatch(
        "on_press"
    )

    assert app_with_nothing.screenManager.current == "createUserScreen"

    assert (
        app_with_nothing.screenManager.current_screen.ids.cardIdInput.getText()
        == "5555555"
    )
    app_with_nothing.screenManager.current_screen.ids.firstNameInput.setText(
        "User4FirstName"
    )
    app_with_nothing.screenManager.current_screen.ids.lastNameInput.setText(
        "User4LastName"
    )
    app_with_nothing.screenManager.current_screen.registerUser()

    assert app_with_nothing.screenManager.current == "loginScreen"

    assert (
        len(app_with_nothing.screenManager.database.getAllPatrons())
        == number_of_patrons_before + 1
    )


@pytest.mark.asyncio
async def test_create_user_with_new_card_from_login_screen(app_with_nothing):

    number_of_patrons_before = len(
        app_with_nothing.screenManager.database.getAllPatrons()
    )

    assert app_with_nothing.screenManager.current == "splashScreen"
    app_with_nothing.screenManager.current_screen.onPressed()

    assert app_with_nothing.screenManager.current == "loginScreen"
    assert app_with_nothing.screenManager.database.getPatronIdByCardId(4444444) is None
    await asyncio.sleep(0.5)
    app_with_nothing.screenManager.RFIDReader.triggerFakeRead(card_id=4444444)
    app_with_nothing.screenManager.current_screen.create_or_link_card_popup.ids.createUserButton.dispatch(
        "on_press"
    )

    assert app_with_nothing.screenManager.current == "createUserScreen"

    assert (
        app_with_nothing.screenManager.current_screen.ids.cardIdInput.getText()
        == "4444444"
    )
    app_with_nothing.screenManager.current_screen.ids.firstNameInput.setText(
        "User5FirstName"
    )
    app_with_nothing.screenManager.current_screen.ids.lastNameInput.setText(
        "User5LastName"
    )
    app_with_nothing.screenManager.current_screen.registerUser()

    assert (
        len(app_with_nothing.screenManager.database.getAllPatrons())
        == number_of_patrons_before + 1
    )
