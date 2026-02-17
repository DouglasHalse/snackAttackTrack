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

    edit_snack_screen = app.screenManager.current_screen
    assert edit_snack_screen.snack_to_edit.snackId == snacks[0].snackId

    assert edit_snack_screen.ids.snackNameInput.getText() == snacks[0].snackName
    assert edit_snack_screen.ids.snackQuantityInput.getText() == str(snacks[0].quantity)
    assert (
        edit_snack_screen.ids.snackPriceInput.getText()
        == f"{snacks[0].pricePerItem:.2f}"
    )


@pytest.mark.asyncio
async def test_edit_snack_back_navigation(app_on_edit_snack_screen):
    """Test navigating back from edit snack screen to edit snacks screen"""

    # Click back button
    edit_snack_screen = app_on_edit_snack_screen.screenManager.current_screen
    edit_snack_screen.ids.header.ids.backButton.dispatch("on_release")
    await asyncio.sleep(0.1)

    # Should navigate back to edit snacks screen
    assert app_on_edit_snack_screen.screenManager.current == "editSnacksScreen"

    await asyncio.sleep(1.1)


@pytest.mark.asyncio
async def test_edit_snack_logout_navigation(app_on_edit_snack_screen):
    """Test navigating back from edit snack screen to edit snacks screen"""

    # Click back button
    edit_snack_screen = app_on_edit_snack_screen.screenManager.current_screen
    edit_snack_screen.ids.header.logout_button_pressed()
    await asyncio.sleep(0.1)

    # Should navigate back to edit snacks screen
    assert app_on_edit_snack_screen.screenManager.current == "splashScreen"


@pytest.mark.asyncio
async def test_edit_snack_cancel_navigation(app_on_edit_snack_screen):
    """Test navigating back from edit snack screen to edit snacks screen"""

    # Click back button
    edit_snack_screen = app_on_edit_snack_screen.screenManager.current_screen
    edit_snack_screen.ids.cancelButton.dispatch("on_press")
    await asyncio.sleep(0.1)

    # Should navigate back to edit snacks screen
    assert app_on_edit_snack_screen.screenManager.current == "editSnacksScreen"


@pytest.mark.asyncio
async def test_edit_snack_change_to_empty_name_rejected(app_on_edit_snack_screen):
    """Test that changing snack name to empty string is rejected and does not update database"""

    snack_names_before = [
        entry.snackName
        for entry in app_on_edit_snack_screen.screenManager.database.getAllSnacks()
    ]

    # Click back button
    edit_snack_screen = app_on_edit_snack_screen.screenManager.current_screen
    edit_snack_screen.ids.snackNameInput.setText("")
    edit_snack_screen.ids.confirmButton.dispatch("on_press")
    await asyncio.sleep(0.1)

    snack_names_after = [
        entry.snackName
        for entry in app_on_edit_snack_screen.screenManager.database.getAllSnacks()
    ]

    assert snack_names_before == snack_names_after

    # Should navigate back to edit snacks screen
    assert app_on_edit_snack_screen.screenManager.current == "editSnackScreen"


@pytest.mark.asyncio
async def test_edit_snack_change_to_zero_quantity_rejected(app_on_edit_snack_screen):
    """Test that changing snack quantity to zero is rejected and does not update database"""

    snack_quantities_before = [
        entry.quantity
        for entry in app_on_edit_snack_screen.screenManager.database.getAllSnacks()
    ]

    # Click back button
    edit_snack_screen = app_on_edit_snack_screen.screenManager.current_screen
    edit_snack_screen.ids.snackQuantityInput.setText("0")
    edit_snack_screen.ids.confirmButton.dispatch("on_press")
    await asyncio.sleep(0.1)

    snack_quantities_after = [
        entry.quantity
        for entry in app_on_edit_snack_screen.screenManager.database.getAllSnacks()
    ]

    assert snack_quantities_before == snack_quantities_after

    # Should navigate back to edit snacks screen
    assert app_on_edit_snack_screen.screenManager.current == "editSnackScreen"


@pytest.mark.asyncio
async def test_edit_snack_change_to_negative_quantity_rejected(
    app_on_edit_snack_screen,
):
    """Test that changing snack quantity to negative is rejected and does not update database"""

    snack_quantities_before = [
        entry.quantity
        for entry in app_on_edit_snack_screen.screenManager.database.getAllSnacks()
    ]

    # Click back button
    edit_snack_screen = app_on_edit_snack_screen.screenManager.current_screen
    edit_snack_screen.ids.snackQuantityInput.setText("-1")
    edit_snack_screen.ids.confirmButton.dispatch("on_press")
    await asyncio.sleep(0.1)

    snack_quantities_after = [
        entry.quantity
        for entry in app_on_edit_snack_screen.screenManager.database.getAllSnacks()
    ]

    assert snack_quantities_before == snack_quantities_after

    # Should navigate back to edit snacks screen
    assert app_on_edit_snack_screen.screenManager.current == "editSnackScreen"


@pytest.mark.asyncio
async def test_edit_snack_change_to_empty_quantity_rejected(app_on_edit_snack_screen):
    """Test that changing snack quantity to empty string is rejected and does not update database"""

    snack_quantities_before = [
        entry.quantity
        for entry in app_on_edit_snack_screen.screenManager.database.getAllSnacks()
    ]

    # Click back button
    edit_snack_screen = app_on_edit_snack_screen.screenManager.current_screen
    edit_snack_screen.ids.snackQuantityInput.setText("")
    edit_snack_screen.ids.confirmButton.dispatch("on_press")
    await asyncio.sleep(0.1)

    snack_quantities_after = [
        entry.quantity
        for entry in app_on_edit_snack_screen.screenManager.database.getAllSnacks()
    ]

    assert snack_quantities_before == snack_quantities_after

    # Should navigate back to edit snacks screen
    assert app_on_edit_snack_screen.screenManager.current == "editSnackScreen"


@pytest.mark.asyncio
async def test_edit_snack_change_to_empty_price_rejected(
    app_on_edit_snack_screen,
):
    """Test that changing snack price to empty string is rejected and does not update database"""

    snack_prices_before = [
        entry.pricePerItem
        for entry in app_on_edit_snack_screen.screenManager.database.getAllSnacks()
    ]

    # Click back button
    edit_snack_screen = app_on_edit_snack_screen.screenManager.current_screen
    edit_snack_screen.ids.snackPriceInput.setText("")
    edit_snack_screen.ids.confirmButton.dispatch("on_press")
    await asyncio.sleep(0.1)

    snack_prices_after = [
        entry.pricePerItem
        for entry in app_on_edit_snack_screen.screenManager.database.getAllSnacks()
    ]

    assert snack_prices_before == snack_prices_after

    # Should navigate back to edit snacks screen
    assert app_on_edit_snack_screen.screenManager.current == "editSnackScreen"


@pytest.mark.asyncio
async def test_edit_snack_change_to_negative_price_rejected(
    app_on_edit_snack_screen,
):
    """Test that changing snack price to negative is rejected and does not update database"""

    snack_prices_before = [
        entry.pricePerItem
        for entry in app_on_edit_snack_screen.screenManager.database.getAllSnacks()
    ]

    # Click back button
    edit_snack_screen = app_on_edit_snack_screen.screenManager.current_screen
    edit_snack_screen.ids.snackPriceInput.setText("-2.44")
    edit_snack_screen.ids.confirmButton.dispatch("on_press")
    await asyncio.sleep(0.1)

    snack_prices_after = [
        entry.pricePerItem
        for entry in app_on_edit_snack_screen.screenManager.database.getAllSnacks()
    ]

    assert snack_prices_before == snack_prices_after

    # Should navigate back to edit snacks screen
    assert app_on_edit_snack_screen.screenManager.current == "editSnackScreen"


@pytest.mark.asyncio
async def test_edit_snack_change_name(
    app_on_edit_snack_screen,
):
    """Test that changing snack name is successful and updates database"""

    snack_names_before = [
        entry.snackName
        for entry in app_on_edit_snack_screen.screenManager.database.getAllSnacks()
    ]

    # Click back button
    edit_snack_screen = app_on_edit_snack_screen.screenManager.current_screen
    edit_snack_screen.ids.snackNameInput.setText("New Snack Name")
    edit_snack_screen.ids.confirmButton.dispatch("on_press")
    await asyncio.sleep(0.1)

    snack_names_after = [
        entry.snackName
        for entry in app_on_edit_snack_screen.screenManager.database.getAllSnacks()
    ]

    assert snack_names_before != snack_names_after
    assert "New Snack Name" in snack_names_after

    # Should navigate back to edit snacks screen
    assert app_on_edit_snack_screen.screenManager.current == "editSnacksScreen"


@pytest.mark.asyncio
async def test_edit_snack_change_quantity_increased(
    app_on_edit_snack_screen,
):
    """Test that increasing snack quantity is successful and updates database"""

    # Click back button
    edit_snack_screen = app_on_edit_snack_screen.screenManager.current_screen

    value_of_added_snacks_before = (
        edit_snack_screen.manager.database.get_value_of_added_snacks()
    )

    snack_quantities_before = edit_snack_screen.snack_to_edit.quantity
    snack_id_being_edited = edit_snack_screen.snack_to_edit.snackId

    edit_snack_screen.ids.snackQuantityInput.setText(str(snack_quantities_before + 5))
    edit_snack_screen.ids.confirmButton.dispatch("on_press")
    await asyncio.sleep(0.1)

    edit_snack_screen.added_snack_popup.ids.priceInput.setText("50.00")
    edit_snack_screen.added_snack_popup.ids.confirmButton.dispatch("on_press")
    await asyncio.sleep(0.1)

    snack_after_edit = app_on_edit_snack_screen.screenManager.database.getSnack(
        snack_id_being_edited
    )

    value_of_added_snacks_after = (
        edit_snack_screen.manager.database.get_value_of_added_snacks()
    )

    assert snack_after_edit.quantity == snack_quantities_before + 5
    assert value_of_added_snacks_after == value_of_added_snacks_before + 50.00

    # Should navigate back to edit snacks screen
    assert app_on_edit_snack_screen.screenManager.current == "editSnacksScreen"


@pytest.mark.asyncio
async def test_edit_snack_change_quantity_decreased(
    app_on_edit_snack_screen,
):
    """Test that decreasing snack quantity is successful and updates database"""

    # Click back button
    edit_snack_screen = app_on_edit_snack_screen.screenManager.current_screen

    value_of_lost_snacks_before = (
        edit_snack_screen.manager.database.get_value_of_lost_snacks()
    )

    number_of_snacks_lost_before = (
        edit_snack_screen.manager.database.get_total_snacks_lost()
    )

    snack_quantities_before = edit_snack_screen.snack_to_edit.quantity
    snack_id_being_edited = edit_snack_screen.snack_to_edit.snackId

    edit_snack_screen.ids.snackQuantityInput.setText(str(snack_quantities_before - 5))
    edit_snack_screen.ids.confirmButton.dispatch("on_press")
    await asyncio.sleep(0.1)

    edit_snack_screen.remove_snack_reason_popup.ids.stolenButton.dispatch("on_press")
    await asyncio.sleep(0.1)

    snack_after_edit = app_on_edit_snack_screen.screenManager.database.getSnack(
        snack_id_being_edited
    )

    value_of_lost_snacks_after = (
        edit_snack_screen.manager.database.get_value_of_lost_snacks()
    )

    number_of_snacks_lost_after = (
        edit_snack_screen.manager.database.get_total_snacks_lost()
    )

    assert snack_after_edit.quantity == snack_quantities_before - 5

    assert value_of_lost_snacks_after == value_of_lost_snacks_before + (
        5 * snack_after_edit.pricePerItem
    )

    assert number_of_snacks_lost_after == number_of_snacks_lost_before + 5

    # Should navigate back to edit snacks screen
    assert app_on_edit_snack_screen.screenManager.current == "editSnacksScreen"


@pytest.mark.asyncio
async def test_edit_snack_remove_snack(
    app_on_edit_snack_screen,
):
    """Test that removing snack with button is successful and updates database"""
    # Click back button
    edit_snack_screen = app_on_edit_snack_screen.screenManager.current_screen

    number_of_snacks_before = len(edit_snack_screen.manager.database.getAllSnacks())

    number_of_snacks_lost_before = (
        edit_snack_screen.manager.database.get_total_snacks_lost()
    )

    value_of_lost_snacks_before = (
        edit_snack_screen.manager.database.get_value_of_lost_snacks()
    )

    snack_to_be_removed = edit_snack_screen.snack_to_edit

    edit_snack_screen.ids.removeButton.dispatch("on_press")
    await asyncio.sleep(0.1)

    edit_snack_screen.remove_snack_confirmation_popup.ids.remove_button.dispatch(
        "on_press"
    )
    await asyncio.sleep(0.1)

    edit_snack_screen.remove_snack_reason_popup.ids.damagedButton.dispatch("on_press")
    await asyncio.sleep(0.1)

    number_of_snacks_after = len(edit_snack_screen.manager.database.getAllSnacks())

    number_of_snacks_lost_after = (
        edit_snack_screen.manager.database.get_total_snacks_lost()
    )

    value_of_lost_snacks_after = (
        edit_snack_screen.manager.database.get_value_of_lost_snacks()
    )

    assert number_of_snacks_after == number_of_snacks_before - 1

    assert (
        number_of_snacks_lost_after
        == number_of_snacks_lost_before + snack_to_be_removed.quantity
    )

    assert value_of_lost_snacks_after == value_of_lost_snacks_before + (
        snack_to_be_removed.pricePerItem * snack_to_be_removed.quantity
    )

    # Should navigate back to edit snacks screen
    assert app_on_edit_snack_screen.screenManager.current == "editSnacksScreen"
