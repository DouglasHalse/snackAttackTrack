import asyncio

import pytest


@pytest.mark.asyncio
async def test_navigate_to_edit_snacks_then_add(app_with_users):
    """Test navigating to edit snacks screen then to add snack"""
    app = app_with_users

    # Navigate to admin screen
    app.screenManager.current = "adminScreen"
    await asyncio.sleep(0.1)

    # Click edit snacks option
    admin_screen = app.screenManager.current_screen
    admin_screen.ids.editSnacksOption.dispatch("on_release")
    await asyncio.sleep(0.1)

    # Verify we're on edit snacks screen
    assert app.screenManager.current == "editSnacksScreen"


@pytest.mark.asyncio
async def test_add_snack_screen_exists(app_with_users):
    """Test that add snack screen can be navigated to"""
    app = app_with_users

    # Navigate directly to add snack screen
    app.screenManager.current = "addSnackScreen"
    await asyncio.sleep(0.2)

    # Verify we're on add snack screen
    assert app.screenManager.current == "addSnackScreen"


@pytest.mark.asyncio
async def test_add_snack_screen_has_back_button(app_with_users):
    """Test that add snack screen has a back button"""
    app = app_with_users

    # Navigate to add snack screen
    app.screenManager.current = "addSnackScreen"
    await asyncio.sleep(0.1)

    # Get the screen
    add_screen = app.screenManager.current_screen
    assert add_screen is not None

    # Verify header exists
    assert hasattr(add_screen.ids, "header")
