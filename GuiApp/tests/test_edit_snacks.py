import asyncio

import pytest

from GuiApp.widgets.editSnacksScreen import EditSnacksScreen


@pytest.mark.asyncio
async def test_navigate_to_edit_snacks_screen(app):
    """Test navigating to edit snacks screen from admin screen"""

    # Navigate to admin screen
    app.screenManager.current = "adminScreen"
    await asyncio.sleep(0.1)

    # Click edit snacks option
    admin_screen = app.screenManager.current_screen
    admin_screen.ids.editSnacksOption.dispatch("on_release")
    await asyncio.sleep(0.1)

    assert app.screenManager.current == "editSnacksScreen"


@pytest.mark.asyncio
async def test_edit_snacks_screen_displays_snacks(app):
    """Test that edit snacks screen displays available snacks"""

    # Navigate to edit snacks screen
    app.screenManager.current = "editSnacksScreen"
    await asyncio.sleep(0.2)

    # Verify we're on edit snacks screen
    assert app.screenManager.current == "editSnacksScreen"

    # Get snacks from database
    snacks_in_db = app.screenManager.database.getAllSnacks()

    assert len(snacks_in_db) > 0

    for snack in snacks_in_db:
        assert app.screenManager.current_screen.ids.snacksTable.hasEntry(snack.snackId)


@pytest.mark.asyncio
async def test_edit_snacks_back_navigation(app):
    """Test navigating back from edit snacks screen"""

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
async def test_edit_snacks_screen_with_no_snacks(app_with_only_users):
    """Test edit snacks screen when there are no snacks"""

    # Navigate to edit snacks screen (no snacks exist)
    app_with_only_users.screenManager.current = "editSnacksScreen"
    await asyncio.sleep(0.2)

    # Verify we're on edit snacks screen
    assert app_with_only_users.screenManager.current == "editSnacksScreen"


@pytest.mark.asyncio
async def test_edit_snacks_screen_refresh(app):
    """Test that edit snacks screen refreshes when re-entered"""

    # Navigate to edit snacks screen
    app.screenManager.current = "editSnacksScreen"
    await asyncio.sleep(0.2)

    old_snacks = app.screenManager.database.getAllSnacks()

    assert len(old_snacks) > 0

    for snack in old_snacks:
        assert app.screenManager.current_screen.ids.snacksTable.hasEntry(snack.snackId)

    # Navigate away
    app.screenManager.current = "adminScreen"
    await asyncio.sleep(0.1)

    # Add a new snack
    app.screenManager.database.addSnack("NewSnack", 10, "test.png", 15)

    # Navigate back to edit snacks screen
    app.screenManager.current = "editSnacksScreen"
    await asyncio.sleep(0.2)

    new_snacks = app.screenManager.database.getAllSnacks()

    assert len(new_snacks) == len(old_snacks) + 1

    for snack in new_snacks:
        assert app.screenManager.current_screen.ids.snacksTable.hasEntry(snack.snackId)


@pytest.mark.asyncio
async def test_edit_snacks_click_add_snack_entry(app):
    """Test clicking add snack entry navigates to add snack screen"""

    # Navigate to edit snacks screen
    app.screenManager.current = "editSnacksScreen"
    await asyncio.sleep(0.1)

    # Click add snack entry
    edit_screen = app.screenManager.current_screen
    edit_screen.onEntryPressed(identifier=EditSnacksScreen.ADD_SNACK_ENTRY_IDENTIFIER)
    await asyncio.sleep(0.1)

    # Should navigate to add snack screen
    assert app.screenManager.current == "addSnackScreen"


@pytest.mark.asyncio
async def test_edit_snacks_click_snack_entry(app):
    """Test clicking a snack entry navigates to edit snack screen"""

    # Navigate to edit snacks screen
    app.screenManager.current = "editSnacksScreen"
    await asyncio.sleep(0.1)

    snacks = app.screenManager.database.getAllSnacks()
    assert len(snacks) > 0

    # Click add snack entry
    edit_screen = app.screenManager.current_screen
    edit_screen.onEntryPressed(identifier=snacks[0].snackId)
    await asyncio.sleep(0.1)

    # Should navigate to edit snack screen
    assert app.screenManager.current == "editSnackScreen"
