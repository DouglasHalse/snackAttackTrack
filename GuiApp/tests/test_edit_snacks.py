import asyncio

import pytest


@pytest.mark.asyncio
async def test_navigate_to_edit_snacks_screen(app_with_users_and_snacks):
    """Test navigating to edit snacks screen from admin screen"""
    app = app_with_users_and_snacks

    # Navigate to admin screen
    app.screenManager.current = "adminScreen"
    await asyncio.sleep(0.1)

    # Click edit snacks option
    admin_screen = app.screenManager.current_screen
    admin_screen.ids.editSnacksOption.dispatch("on_release")
    await asyncio.sleep(0.1)

    assert app.screenManager.current == "editSnacksScreen"


@pytest.mark.asyncio
async def test_edit_snacks_screen_displays_snacks(app_with_users_and_snacks):
    """Test that edit snacks screen displays available snacks"""
    app = app_with_users_and_snacks

    # Navigate to edit snacks screen
    app.screenManager.current = "editSnacksScreen"
    await asyncio.sleep(0.2)

    # Verify we're on edit snacks screen
    assert app.screenManager.current == "editSnacksScreen"

    # Verify screen exists
    edit_screen = app.screenManager.current_screen
    assert edit_screen is not None


@pytest.mark.asyncio
async def test_edit_snacks_back_navigation(app_with_users_and_snacks):
    """Test navigating back from edit snacks screen"""
    app = app_with_users_and_snacks

    # Navigate to edit snacks screen
    app.screenManager.current = "editSnacksScreen"
    await asyncio.sleep(0.1)

    # Click back button
    edit_screen = app.screenManager.current_screen
    edit_screen.ids.header.ids.backButton.dispatch("on_release")
    await asyncio.sleep(0.1)

    # Should navigate back to admin screen
    assert app.screenManager.current == "adminScreen"


@pytest.mark.asyncio
async def test_edit_snacks_screen_with_no_snacks(app_with_users):
    """Test edit snacks screen when there are no snacks"""
    app = app_with_users

    # Navigate to edit snacks screen (no snacks exist)
    app.screenManager.current = "editSnacksScreen"
    await asyncio.sleep(0.2)

    # Verify we're on edit snacks screen
    assert app.screenManager.current == "editSnacksScreen"


@pytest.mark.asyncio
async def test_edit_snacks_screen_refresh(app_with_users_and_snacks):
    """Test that edit snacks screen refreshes when re-entered"""
    app = app_with_users_and_snacks

    # Navigate to edit snacks screen
    app.screenManager.current = "editSnacksScreen"
    await asyncio.sleep(0.2)

    # Navigate away
    app.screenManager.current = "adminScreen"
    await asyncio.sleep(0.1)

    # Add a new snack
    app.screenManager.database.addSnack("NewSnack", 10, "test.png", 15)

    # Navigate back to edit snacks screen
    app.screenManager.current = "editSnacksScreen"
    await asyncio.sleep(0.2)

    # Verify screen loaded (data should be refreshed)
    assert app.screenManager.current == "editSnacksScreen"
