import pytest


@pytest.mark.asyncio
async def test_return_from_add_snack_with_back_button(app_on_add_snack_screen):
    assert app_on_add_snack_screen.screenManager.current == "addSnackScreen"

    app_on_add_snack_screen.screenManager.current_screen.ids.header.ids.backButton.dispatch(
        "on_release"
    )

    assert app_on_add_snack_screen.screenManager.current == "editSnacksScreen"


@pytest.mark.asyncio
async def test_return_from_add_snack_with_cancel_button(app_on_add_snack_screen):
    assert app_on_add_snack_screen.screenManager.current == "addSnackScreen"

    app_on_add_snack_screen.screenManager.current_screen.ids.cancelButton.dispatch(
        "on_press"
    )
    assert app_on_add_snack_screen.screenManager.current == "editSnacksScreen"


@pytest.mark.asyncio
async def test_add_snack(app_on_add_snack_screen):

    snack_ids_before_adding = [
        snack.snackId
        for snack in app_on_add_snack_screen.screenManager.database.getAllSnacks()
    ]

    app_on_add_snack_screen.screenManager.current_screen.ids.snackNameInput.setText(
        "Chips"
    )
    app_on_add_snack_screen.screenManager.current_screen.ids.snackQuantityInput.setText(
        "10"
    )
    app_on_add_snack_screen.screenManager.current_screen.ids.snackPriceInput.setText(
        "15.00"
    )
    app_on_add_snack_screen.screenManager.current_screen.ids.snackFeeInput.setText(
        "0.05"
    )

    app_on_add_snack_screen.screenManager.current_screen.ids.confirmButton.dispatch(
        "on_press"
    )

    assert app_on_add_snack_screen.screenManager.current == "editSnacksScreen"

    snack_ids_after_adding = [
        snack.snackId
        for snack in app_on_add_snack_screen.screenManager.database.getAllSnacks()
    ]

    new_snacks = [
        snack_id
        for snack_id in snack_ids_after_adding
        if snack_id not in snack_ids_before_adding
    ]

    assert len(new_snacks) == 1
    added_snack_id = new_snacks[0]
    added_snack = app_on_add_snack_screen.screenManager.database.getSnack(
        added_snack_id
    )
    assert added_snack.snackName == "Chips"
    assert added_snack.quantity == 10
    assert added_snack.pricePerItem == round((15.00 * 1.05) / 10.0, 2)
    assert added_snack.imageID == "None"


@pytest.mark.asyncio
async def test_try_add_empty_name(app_on_add_snack_screen):

    snack_ids_before_adding = [
        snack.snackId
        for snack in app_on_add_snack_screen.screenManager.database.getAllSnacks()
    ]

    app_on_add_snack_screen.screenManager.current_screen.ids.snackNameInput.setText("")
    app_on_add_snack_screen.screenManager.current_screen.ids.snackQuantityInput.setText(
        "10"
    )
    app_on_add_snack_screen.screenManager.current_screen.ids.snackPriceInput.setText(
        "15.00"
    )
    app_on_add_snack_screen.screenManager.current_screen.ids.snackFeeInput.setText(
        "0.05"
    )

    app_on_add_snack_screen.screenManager.current_screen.ids.confirmButton.dispatch(
        "on_press"
    )

    assert app_on_add_snack_screen.screenManager.current == "addSnackScreen"

    snack_ids_after_adding = [
        snack.snackId
        for snack in app_on_add_snack_screen.screenManager.database.getAllSnacks()
    ]

    assert snack_ids_before_adding == snack_ids_after_adding


@pytest.mark.asyncio
async def test_try_add_zero_price(app_on_add_snack_screen):

    snack_ids_before_adding = [
        snack.snackId
        for snack in app_on_add_snack_screen.screenManager.database.getAllSnacks()
    ]

    app_on_add_snack_screen.screenManager.current_screen.ids.snackNameInput.setText(
        "Chips"
    )
    app_on_add_snack_screen.screenManager.current_screen.ids.snackQuantityInput.setText(
        "10"
    )
    app_on_add_snack_screen.screenManager.current_screen.ids.snackPriceInput.setText(
        "0.00"
    )
    app_on_add_snack_screen.screenManager.current_screen.ids.snackFeeInput.setText(
        "0.05"
    )

    app_on_add_snack_screen.screenManager.current_screen.ids.confirmButton.dispatch(
        "on_press"
    )

    assert app_on_add_snack_screen.screenManager.current == "addSnackScreen"

    snack_ids_after_adding = [
        snack.snackId
        for snack in app_on_add_snack_screen.screenManager.database.getAllSnacks()
    ]

    assert snack_ids_before_adding == snack_ids_after_adding


@pytest.mark.asyncio
async def test_try_add_negative_price(app_on_add_snack_screen):

    snack_ids_before_adding = [
        snack.snackId
        for snack in app_on_add_snack_screen.screenManager.database.getAllSnacks()
    ]

    app_on_add_snack_screen.screenManager.current_screen.ids.snackNameInput.setText(
        "Chips"
    )
    app_on_add_snack_screen.screenManager.current_screen.ids.snackQuantityInput.setText(
        "10"
    )
    app_on_add_snack_screen.screenManager.current_screen.ids.snackPriceInput.setText(
        "-10.00"
    )
    app_on_add_snack_screen.screenManager.current_screen.ids.snackFeeInput.setText(
        "0.05"
    )

    app_on_add_snack_screen.screenManager.current_screen.ids.confirmButton.dispatch(
        "on_press"
    )

    assert app_on_add_snack_screen.screenManager.current == "addSnackScreen"

    snack_ids_after_adding = [
        snack.snackId
        for snack in app_on_add_snack_screen.screenManager.database.getAllSnacks()
    ]

    assert snack_ids_before_adding == snack_ids_after_adding


@pytest.mark.asyncio
async def test_try_add_negative_fee(app_on_add_snack_screen):

    snack_ids_before_adding = [
        snack.snackId
        for snack in app_on_add_snack_screen.screenManager.database.getAllSnacks()
    ]

    app_on_add_snack_screen.screenManager.current_screen.ids.snackNameInput.setText(
        "Chips"
    )
    app_on_add_snack_screen.screenManager.current_screen.ids.snackQuantityInput.setText(
        "10"
    )
    app_on_add_snack_screen.screenManager.current_screen.ids.snackPriceInput.setText(
        "10.00"
    )
    app_on_add_snack_screen.screenManager.current_screen.ids.snackFeeInput.setText(
        "-0.05"
    )

    app_on_add_snack_screen.screenManager.current_screen.ids.confirmButton.dispatch(
        "on_press"
    )

    assert app_on_add_snack_screen.screenManager.current == "addSnackScreen"

    snack_ids_after_adding = [
        snack.snackId
        for snack in app_on_add_snack_screen.screenManager.database.getAllSnacks()
    ]

    assert snack_ids_before_adding == snack_ids_after_adding


@pytest.mark.asyncio
async def test_try_add_zero_quantity(app_on_add_snack_screen):

    snack_ids_before_adding = [
        snack.snackId
        for snack in app_on_add_snack_screen.screenManager.database.getAllSnacks()
    ]

    app_on_add_snack_screen.screenManager.current_screen.ids.snackNameInput.setText(
        "Chips"
    )
    app_on_add_snack_screen.screenManager.current_screen.ids.snackQuantityInput.setText(
        "0"
    )
    app_on_add_snack_screen.screenManager.current_screen.ids.snackPriceInput.setText(
        "15.00"
    )
    app_on_add_snack_screen.screenManager.current_screen.ids.snackFeeInput.setText(
        "0.05"
    )

    app_on_add_snack_screen.screenManager.current_screen.ids.confirmButton.dispatch(
        "on_press"
    )

    assert app_on_add_snack_screen.screenManager.current == "addSnackScreen"

    snack_ids_after_adding = [
        snack.snackId
        for snack in app_on_add_snack_screen.screenManager.database.getAllSnacks()
    ]

    assert snack_ids_before_adding == snack_ids_after_adding


@pytest.mark.asyncio
async def test_try_add_negative_quantity(app_on_add_snack_screen):

    snack_ids_before_adding = [
        snack.snackId
        for snack in app_on_add_snack_screen.screenManager.database.getAllSnacks()
    ]

    app_on_add_snack_screen.screenManager.current_screen.ids.snackNameInput.setText(
        "Chips"
    )
    app_on_add_snack_screen.screenManager.current_screen.ids.snackQuantityInput.setText(
        "-10"
    )
    app_on_add_snack_screen.screenManager.current_screen.ids.snackPriceInput.setText(
        "15.00"
    )
    app_on_add_snack_screen.screenManager.current_screen.ids.snackFeeInput.setText(
        "0.05"
    )

    app_on_add_snack_screen.screenManager.current_screen.ids.confirmButton.dispatch(
        "on_press"
    )

    assert app_on_add_snack_screen.screenManager.current == "addSnackScreen"

    snack_ids_after_adding = [
        snack.snackId
        for snack in app_on_add_snack_screen.screenManager.database.getAllSnacks()
    ]

    assert snack_ids_before_adding == snack_ids_after_adding
