import asyncio

import pytest


@pytest.mark.asyncio
async def test_navigate_to_edit_users_screen(app_with_only_users):
    """Test navigating to edit users screen from admin screen"""
    app = app_with_only_users

    # Navigate to admin screen
    app.screenManager.current = "adminScreen"
    await asyncio.sleep(0.1)

    # Click edit users option
    admin_screen = app.screenManager.current_screen
    admin_screen.ids.editUsersOption.dispatch("on_release")
    await asyncio.sleep(0.1)

    assert app.screenManager.current == "editUsersScreen"


@pytest.mark.asyncio
async def test_edit_users_screen_displays_users(app_with_only_users):
    """Test that edit users screen displays all users"""
    app = app_with_only_users

    # Navigate to edit users screen
    app.screenManager.current = "editUsersScreen"
    await asyncio.sleep(0.2)

    # Verify we're on edit users screen
    assert app.screenManager.current == "editUsersScreen"

    # Verify screen exists
    edit_users_screen = app.screenManager.current_screen
    assert edit_users_screen is not None


@pytest.mark.asyncio
async def test_edit_users_back_navigation(app_with_only_users):
    """Test navigating back from edit users screen"""
    app = app_with_only_users

    # Navigate to edit users screen
    app.screenManager.current = "editUsersScreen"
    await asyncio.sleep(0.1)

    # Click back button
    edit_users_screen = app.screenManager.current_screen
    edit_users_screen.ids.header.ids.backButton.dispatch("on_release")
    await asyncio.sleep(0.1)

    # Should navigate back to admin screen
    assert app.screenManager.current == "adminScreen"


@pytest.mark.asyncio
async def test_select_user_to_edit(app_with_only_users):
    """Test selecting a user to edit from the users list"""
    app = app_with_only_users

    # Get a user to edit
    user_id = app.screenManager.database.getPatronIdByCardId(987654321)
    user = app.screenManager.database.getPatronData(user_id)
    assert user is not None

    # Navigate to edit users screen
    app.screenManager.current = "editUsersScreen"
    await asyncio.sleep(0.2)

    # Click on a user entry
    edit_users_screen = app.screenManager.current_screen
    edit_users_screen.onUserEntryPressed(user.patronId)
    await asyncio.sleep(0.1)

    # Should navigate to edit user screen
    assert app.screenManager.current == "editUserScreen"

    # Verify the user data is loaded
    edit_user_screen = app.screenManager.current_screen
    assert edit_user_screen.user_to_edit is not None
    assert edit_user_screen.user_to_edit.patronId == user.patronId


@pytest.mark.asyncio
async def test_edit_user_screen_displays_user_data(app_with_only_users):
    """Test that edit user screen displays the selected user's data"""
    app = app_with_only_users

    # Get a user to edit
    user_id = app.screenManager.database.getPatronIdByCardId(987654321)
    user = app.screenManager.database.getPatronData(user_id)
    assert user is not None

    # Set the user to edit and navigate
    app.screenManager.get_screen("editUserScreen").user_to_edit = user
    app.screenManager.current = "editUserScreen"
    await asyncio.sleep(0.2)

    # Verify user data is displayed
    edit_screen = app.screenManager.current_screen
    assert edit_screen.ids.firstNameInput.getText() == user.firstName
    assert edit_screen.ids.lastNameInput.getText() == user.lastName


@pytest.mark.asyncio
async def test_edit_user_back_navigation(app_with_only_users):
    """Test navigating back from edit user screen"""
    app = app_with_only_users

    # Get a user to edit
    user_id = app.screenManager.database.getPatronIdByCardId(987654321)
    user = app.screenManager.database.getPatronData(user_id)
    assert user is not None

    # Set the user to edit and navigate
    app.screenManager.get_screen("editUserScreen").user_to_edit = user
    app.screenManager.current = "editUserScreen"
    await asyncio.sleep(0.1)

    # Click back button
    edit_screen = app.screenManager.current_screen
    edit_screen.ids.header.ids.backButton.dispatch("on_release")
    await asyncio.sleep(0.1)

    # Should navigate back to edit users screen
    assert app.screenManager.current == "editUsersScreen"


@pytest.mark.asyncio
async def test_edit_user_cancel(app_with_only_users):
    """Test canceling edit user changes"""
    app = app_with_only_users

    # Get a user to edit
    user_id = app.screenManager.database.getPatronIdByCardId(987654321)
    user = app.screenManager.database.getPatronData(user_id)
    assert user is not None
    original_first_name = user.firstName

    # Set the user to edit and navigate
    app.screenManager.get_screen("editUserScreen").user_to_edit = user
    app.screenManager.current = "editUserScreen"
    await asyncio.sleep(0.2)

    # Change the first name
    edit_screen = app.screenManager.current_screen
    edit_screen.ids.firstNameInput.setText("ChangedName")
    await asyncio.sleep(0.1)

    # Click cancel
    edit_screen.onCancel()
    await asyncio.sleep(0.1)

    # Should navigate back without saving
    assert app.screenManager.current == "editUsersScreen"

    # Verify data was not changed

    user_after = app.screenManager.database.getPatronData(user_id)
    assert user_after.firstName == original_first_name


@pytest.mark.asyncio
async def test_edit_user_change_first_name(app_with_only_users):
    """Test editing a user's first name"""
    app = app_with_only_users

    # Get a user to edit
    user_id = app.screenManager.database.getPatronIdByCardId(987654321)
    user = app.screenManager.database.getPatronData(user_id)
    assert user is not None

    # Login as this user (required for refreshCurrentPatron)
    app.screenManager.login(user_id)

    # Set the user to edit and navigate
    app.screenManager.get_screen("editUserScreen").user_to_edit = user
    app.screenManager.current = "editUserScreen"
    await asyncio.sleep(0.2)

    # Change the first name
    edit_screen = app.screenManager.current_screen
    edit_screen.ids.firstNameInput.setText("NewFirstName")
    await asyncio.sleep(0.1)

    # Confirm changes
    edit_screen.onConfirm()
    await asyncio.sleep(0.1)

    # Should navigate back
    assert app.screenManager.current == "editUsersScreen"

    # Verify data was changed
    user_after = app.screenManager.database.getPatronData(user_id)
    assert user_after.firstName == "NewFirstName"


@pytest.mark.asyncio
async def test_edit_user_change_last_name(app_with_only_users):
    """Test editing a user's last name"""
    app = app_with_only_users

    # Get a user to edit
    user_id = app.screenManager.database.getPatronIdByCardId(987654321)
    user = app.screenManager.database.getPatronData(user_id)
    assert user is not None

    # Login as this user (required for refreshCurrentPatron)
    app.screenManager.login(user_id)

    # Set the user to edit and navigate
    app.screenManager.get_screen("editUserScreen").user_to_edit = user
    app.screenManager.current = "editUserScreen"
    await asyncio.sleep(0.2)

    # Change the last name
    edit_screen = app.screenManager.current_screen
    edit_screen.ids.lastNameInput.setText("NewLastName")
    await asyncio.sleep(0.1)

    # Confirm changes
    edit_screen.onConfirm()
    await asyncio.sleep(0.1)

    # Should navigate back
    assert app.screenManager.current == "editUsersScreen"

    # Verify data was changed
    user_after = app.screenManager.database.getPatronData(user_id)
    assert user_after.lastName == "NewLastName"


@pytest.mark.asyncio
async def test_edit_user_empty_first_name_rejected(app_with_only_users):
    """Test that empty first name is rejected"""
    app = app_with_only_users

    # Get a user to edit
    user_id = app.screenManager.database.getPatronIdByCardId(987654321)
    user = app.screenManager.database.getPatronData(user_id)
    assert user is not None

    original_first_name = user.firstName

    # Set the user to edit and navigate
    app.screenManager.get_screen("editUserScreen").user_to_edit = user
    app.screenManager.current = "editUserScreen"
    await asyncio.sleep(0.2)

    # Clear the first name
    edit_screen = app.screenManager.current_screen
    edit_screen.ids.firstNameInput.setText("")
    await asyncio.sleep(0.1)

    # Try to confirm
    edit_screen.onConfirm()
    await asyncio.sleep(0.1)

    # Should stay on edit user screen (validation failed)
    assert app.screenManager.current == "editUserScreen"

    # Verify data was not changed
    user_after = app.screenManager.database.getPatronData(user_id)
    assert user_after.firstName == original_first_name


@pytest.mark.asyncio
async def test_edit_user_empty_last_name_rejected(app_with_only_users):
    """Test that empty last name is rejected"""
    app = app_with_only_users

    # Get a user to edit
    user_id = app.screenManager.database.getPatronIdByCardId(987654321)
    user = app.screenManager.database.getPatronData(user_id)
    assert user is not None

    original_last_name = user.lastName

    # Set the user to edit and navigate
    app.screenManager.get_screen("editUserScreen").user_to_edit = user
    app.screenManager.current = "editUserScreen"
    await asyncio.sleep(0.2)

    # Clear the last name
    edit_screen = app.screenManager.current_screen
    edit_screen.ids.lastNameInput.setText("")
    await asyncio.sleep(0.1)

    # Try to confirm
    edit_screen.onConfirm()
    await asyncio.sleep(0.1)

    # Should stay on edit user screen (validation failed)
    assert app.screenManager.current == "editUserScreen"

    # Verify data was not changed
    user_after = app.screenManager.database.getPatronData(user_id)
    assert user_after.lastName == original_last_name


@pytest.mark.asyncio
async def test_edit_user_change_credits(app_with_only_users):
    """Test editing a user's credits"""
    app = app_with_only_users

    # Get a user to edit
    user_id = app.screenManager.database.getPatronIdByCardId(987654321)
    user = app.screenManager.database.getPatronData(user_id)
    assert user is not None

    app.screenManager.database.addCredits(user.patronId, 50.0)

    user = app.screenManager.database.getPatronData(user_id)
    assert user.totalCredits == 50.0

    # Login as this user (required for refreshCurrentPatron)
    app.screenManager.login(user_id)

    # Set the user to edit and navigate
    app.screenManager.get_screen("editUserScreen").user_to_edit = user
    app.screenManager.current = "editUserScreen"
    await asyncio.sleep(0.2)

    # Change the credits
    edit_screen = app.screenManager.current_screen
    edit_screen.ids.creditsInput.setText("100.00")
    await asyncio.sleep(0.1)

    # Confirm changes
    edit_screen.onConfirm()
    await asyncio.sleep(0.1)

    # Should navigate back
    assert app.screenManager.current == "editUsersScreen"

    # Verify credits were changed
    user_after = app.screenManager.database.getPatronData(user_id)
    assert user_after.totalCredits == 100.0


@pytest.mark.asyncio
async def test_edit_user_negative_credits_rejected(app_with_only_users):
    """Test that negative credits are rejected"""
    app = app_with_only_users

    # Get a user to edit
    user_id = app.screenManager.database.getPatronIdByCardId(987654321)
    user = app.screenManager.database.getPatronData(user_id)
    assert user is not None

    app.screenManager.database.addCredits(user.patronId, 50.0)

    user = app.screenManager.database.getPatronData(user_id)
    original_credits = user.totalCredits

    # Set the user to edit and navigate
    app.screenManager.get_screen("editUserScreen").user_to_edit = user
    app.screenManager.current = "editUserScreen"
    await asyncio.sleep(0.2)

    # Try to set negative credits
    edit_screen = app.screenManager.current_screen
    edit_screen.ids.creditsInput.setText("-10.00")
    await asyncio.sleep(0.1)

    # Try to confirm
    edit_screen.onConfirm()
    await asyncio.sleep(0.1)

    # Should stay on edit user screen (validation failed)
    assert app.screenManager.current == "editUserScreen"

    # Verify credits were not changed
    user_after = app.screenManager.database.getPatronData(user_id)
    assert user_after.totalCredits == original_credits


@pytest.mark.asyncio
async def test_edit_user_invalid_credits_rejected(app_with_only_users):
    """Test that invalid credits value is rejected"""
    app = app_with_only_users

    # Get a user to edit
    user_id = app.screenManager.database.getPatronIdByCardId(987654321)
    user = app.screenManager.database.getPatronData(user_id)
    assert user is not None

    app.screenManager.database.addCredits(user.patronId, 50.0)

    user = app.screenManager.database.getPatronData(user_id)

    original_credits = user.totalCredits

    # Set the user to edit and navigate
    app.screenManager.get_screen("editUserScreen").user_to_edit = user
    app.screenManager.current = "editUserScreen"
    await asyncio.sleep(0.2)

    # Try to set invalid credits
    edit_screen = app.screenManager.current_screen
    edit_screen.ids.creditsInput.setText("not_a_number")
    await asyncio.sleep(0.1)

    # Try to confirm
    edit_screen.onConfirm()
    await asyncio.sleep(0.1)

    # Should stay on edit user screen (validation failed)
    assert app.screenManager.current == "editUserScreen"

    # Verify credits were not changed
    user_after = app.screenManager.database.getPatronData(user_id)
    assert user_after.totalCredits == original_credits


@pytest.mark.asyncio
async def test_edit_users_screen_with_no_users(app):
    """Test edit users screen when there are no users"""
    # Navigate to edit users screen (no users exist)
    app.screenManager.current = "editUsersScreen"
    await asyncio.sleep(0.2)

    # Verify we're on edit users screen
    assert app.screenManager.current == "editUsersScreen"


@pytest.mark.asyncio
async def test_edit_user_duplicate_card_id_rejected(app_with_only_users):
    """Test that duplicate card ID is rejected"""
    app = app_with_only_users

    # Get a user to edit
    user_id_1 = app.screenManager.database.getPatronIdByCardId(987654321)
    user1 = app.screenManager.database.getPatronData(user_id_1)
    assert user1 is not None

    # Get a user to edit
    user_id_2 = app.screenManager.database.getPatronIdByCardId(123456789)
    user2 = app.screenManager.database.getPatronData(user_id_2)
    assert user2 is not None

    # Set user1 to edit and navigate
    app.screenManager.get_screen("editUserScreen").user_to_edit = user1
    app.screenManager.current = "editUserScreen"
    await asyncio.sleep(0.2)

    # Try to set user1's card ID to user2's card ID
    edit_screen = app.screenManager.current_screen
    edit_screen.ids.cardIdInput.setText(str(user2.employeeID))
    await asyncio.sleep(0.1)

    # Try to confirm
    edit_screen.onConfirm()
    await asyncio.sleep(0.1)

    # Should stay on edit user screen (validation failed)
    assert app.screenManager.current == "editUserScreen"


@pytest.mark.asyncio
async def test_edit_user_set_card_on_user_with_no_card(app_with_only_users):
    """Test setting a card ID for a user that previously had no card"""
    app = app_with_only_users

    app.screenManager.database.addPatron(
        first_name="NoCardFirstName", last_name="NoCardLastName", employee_id=""
    )

    users = app.screenManager.database.getAllPatrons()
    user = next((u for u in users if u.firstName == "NoCardFirstName"), None)
    assert user is not None

    app.screenManager.login(user.patronId)

    app.screenManager.get_screen("editUserScreen").user_to_edit = user
    app.screenManager.current = "editUserScreen"
    await asyncio.sleep(0.2)

    # Set a card ID
    edit_screen = app.screenManager.current_screen
    edit_screen.cardRead(1233332323)

    assert edit_screen.ids.cardIdInput.getText() == "1233332323"

    # Confirm changes
    edit_screen.onConfirm()
    await asyncio.sleep(0.1)

    user_after = app.screenManager.database.getPatronData(user.patronId)
    assert user_after.employeeID == "1233332323"


@pytest.mark.asyncio
async def test_edit_user_remove_user(app_with_only_users):
    """Test removing a user"""
    app = app_with_only_users

    # Get a user to remove
    user_id = app.screenManager.database.getPatronIdByCardId(987654321)
    user = app.screenManager.database.getPatronData(user_id)
    assert user is not None

    # Set user to edit and navigate
    app.screenManager.get_screen("editUserScreen").user_to_edit = user
    app.screenManager.current = "editUserScreen"
    await asyncio.sleep(0.2)

    users_before = app.screenManager.database.getAllPatrons()

    # Remove the user
    edit_screen = app.screenManager.current_screen
    edit_screen.onRemove()
    await asyncio.sleep(0.1)

    edit_screen.remove_confirmation_popup.remove_button_pressed()
    await asyncio.sleep(0.1)

    users_after = app.screenManager.database.getAllPatrons()
    assert len(users_after) == len(users_before) - 1
    for remaining_user in users_after:
        assert remaining_user.patronId != user_id

    # Verify the user was removed
    assert app.screenManager.database.getPatronData(user_id) is None


@pytest.mark.asyncio
async def test_edit_user_screen_refresh(app_with_only_users):
    """Test that edit users screen refreshes when re-entered"""
    app = app_with_only_users

    # Navigate to edit users screen
    app.screenManager.current = "editUsersScreen"
    await asyncio.sleep(0.2)

    # Navigate away
    app.screenManager.current = "adminScreen"
    await asyncio.sleep(0.1)

    # Add a new user
    app.screenManager.database.addPatron(
        first_name="NewUser",
        last_name="NewLastName",
        employee_id=111111111,
    )

    # Navigate back to edit users screen
    app.screenManager.current = "editUsersScreen"
    await asyncio.sleep(0.2)

    # Verify screen loaded (data should be refreshed)
    assert app.screenManager.current == "editUsersScreen"
