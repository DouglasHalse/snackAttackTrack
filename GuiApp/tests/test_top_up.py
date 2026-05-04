import asyncio

import pytest

from app_types import Credits
from GuiApp.widgets.settingsManager import SettingName


@pytest.mark.asyncio
async def test_return_from_top_up_with_back_button(app_with_only_users):

    assert app_with_only_users.screenManager.current == "splashScreen"

    assert (
        app_with_only_users.screenManager.database.getPatronIdByCardId("123456789")
        is not None
    )

    app_with_only_users.screenManager.RFIDReader.triggerFakeRead(card_id="123456789")

    assert app_with_only_users.screenManager.current == "mainUserPage"

    app_with_only_users.screenManager.current_screen.ids.topUpOption.dispatch(
        "on_release"
    )

    await asyncio.sleep(0.5)

    assert app_with_only_users.screenManager.current == "topUpAmountScreen"

    app_with_only_users.screenManager.current_screen.ids.header.ids.backButton.dispatch(
        "on_release"
    )

    assert app_with_only_users.screenManager.current == "mainUserPage"


@pytest.mark.asyncio
async def test_return_from_top_up_with_cancel_button(app_with_only_users):

    assert app_with_only_users.screenManager.current == "splashScreen"

    assert (
        app_with_only_users.screenManager.database.getPatronIdByCardId("123456789")
        is not None
    )

    app_with_only_users.screenManager.RFIDReader.triggerFakeRead(card_id="123456789")

    assert app_with_only_users.screenManager.current == "mainUserPage"

    app_with_only_users.screenManager.current_screen.ids.topUpOption.dispatch(
        "on_release"
    )

    await asyncio.sleep(0.5)

    assert app_with_only_users.screenManager.current == "topUpAmountScreen"

    app_with_only_users.screenManager.current_screen.ids.cancelButton.dispatch(
        "on_press"
    )

    assert app_with_only_users.screenManager.current == "mainUserPage"


@pytest.mark.asyncio
async def test_no_amount_selected(app_with_only_users):

    assert app_with_only_users.screenManager.current == "splashScreen"

    assert (
        app_with_only_users.screenManager.database.getPatronIdByCardId("123456789")
        is not None
    )

    app_with_only_users.screenManager.RFIDReader.triggerFakeRead(card_id="123456789")

    assert app_with_only_users.screenManager.current == "mainUserPage"

    app_with_only_users.screenManager.current_screen.ids.topUpOption.dispatch(
        "on_release"
    )

    await asyncio.sleep(0.5)

    assert app_with_only_users.screenManager.current == "topUpAmountScreen"

    app_with_only_users.screenManager.current_screen.ids.continueButton.dispatch(
        "on_press"
    )

    assert app_with_only_users.screenManager.current == "topUpAmountScreen"


@pytest.mark.asyncio
async def test_less_than_one_amount_selected(app_with_only_users):

    assert app_with_only_users.screenManager.current == "splashScreen"

    assert (
        app_with_only_users.screenManager.database.getPatronIdByCardId("123456789")
        is not None
    )

    app_with_only_users.screenManager.RFIDReader.triggerFakeRead(card_id="123456789")

    assert app_with_only_users.screenManager.current == "mainUserPage"

    app_with_only_users.screenManager.current_screen.ids.topUpOption.dispatch(
        "on_release"
    )

    assert app_with_only_users.screenManager.current == "topUpAmountScreen"

    app_with_only_users.screenManager.current_screen.ids.creditsToAdd.focus = True

    assert (
        app_with_only_users.screenManager.current_screen.credit_input_popup is not None
    )

    await asyncio.sleep(1.5)

    app_with_only_users.screenManager.current_screen.credit_input_popup.ids.virtualKeyboard.dispatch(
        "on_key_up", "0", *[]
    )

    app_with_only_users.screenManager.current_screen.credit_input_popup.ids.virtualKeyboard.dispatch(
        "on_key_up", ".", *[]
    )

    app_with_only_users.screenManager.current_screen.credit_input_popup.ids.virtualKeyboard.dispatch(
        "on_key_up", "9", *[]
    )

    app_with_only_users.screenManager.current_screen.credit_input_popup.ids.virtualKeyboard.dispatch(
        "on_key_up", "9", *[]
    )

    await asyncio.sleep(0.5)

    assert (
        app_with_only_users.screenManager.current_screen.credit_input_popup.ids.textInput.getText()
        == "0.99"
    )

    app_with_only_users.screenManager.current_screen.credit_input_popup.ids.virtualKeyboard.dispatch(
        "on_key_up", "enter", *[]
    )

    await asyncio.sleep(0.5)

    assert (
        app_with_only_users.screenManager.current_screen.ids.creditsToAdd.text == "0.99"
    )

    assert (
        app_with_only_users.screenManager.current_screen.ids.creditsAfterwards.text
        == "0.99"
    )

    app_with_only_users.screenManager.current_screen.ids.continueButton.dispatch(
        "on_press"
    )

    await asyncio.sleep(0.5)

    # Does not proceed to payment screen
    assert app_with_only_users.screenManager.current == "topUpAmountScreen"


@pytest.mark.asyncio
async def test_negative_amount_selected(app_with_only_users):

    assert app_with_only_users.screenManager.current == "splashScreen"

    assert (
        app_with_only_users.screenManager.database.getPatronIdByCardId("123456789")
        is not None
    )

    app_with_only_users.screenManager.RFIDReader.triggerFakeRead(card_id="123456789")

    assert app_with_only_users.screenManager.current == "mainUserPage"

    app_with_only_users.screenManager.current_screen.ids.topUpOption.dispatch(
        "on_release"
    )

    assert app_with_only_users.screenManager.current == "topUpAmountScreen"

    app_with_only_users.screenManager.current_screen.ids.creditsToAdd.text = "-10.00"

    app_with_only_users.screenManager.current_screen.ids.continueButton.dispatch(
        "on_press"
    )

    assert app_with_only_users.screenManager.current == "topUpAmountScreen"


@pytest.mark.asyncio
async def test_return_from_payment_with_back_button(app_with_only_users):

    assert app_with_only_users.screenManager.current == "splashScreen"

    assert (
        app_with_only_users.screenManager.database.getPatronIdByCardId("123456789")
        is not None
    )

    app_with_only_users.screenManager.RFIDReader.triggerFakeRead(card_id="123456789")

    assert app_with_only_users.screenManager.current == "mainUserPage"

    app_with_only_users.screenManager.current_screen.ids.topUpOption.dispatch(
        "on_release"
    )

    assert app_with_only_users.screenManager.current == "topUpAmountScreen"

    app_with_only_users.screenManager.current_screen.ids.creditsToAdd.text = "10.00"

    app_with_only_users.screenManager.current_screen.ids.continueButton.dispatch(
        "on_press"
    )

    assert app_with_only_users.screenManager.current == "topUpPaymentScreen"

    app_with_only_users.screenManager.current_screen.ids.header.ids.backButton.dispatch(
        "on_release"
    )

    assert app_with_only_users.screenManager.current == "topUpAmountScreen"


@pytest.mark.asyncio
async def test_return_from_payment_with_cancel_button(app_with_only_users):

    assert app_with_only_users.screenManager.current == "splashScreen"

    assert (
        app_with_only_users.screenManager.database.getPatronIdByCardId("123456789")
        is not None
    )

    app_with_only_users.screenManager.RFIDReader.triggerFakeRead(card_id="123456789")

    assert app_with_only_users.screenManager.current == "mainUserPage"

    app_with_only_users.screenManager.current_screen.ids.topUpOption.dispatch(
        "on_release"
    )

    assert app_with_only_users.screenManager.current == "topUpAmountScreen"

    app_with_only_users.screenManager.current_screen.ids.creditsToAdd.text = "10.00"

    app_with_only_users.screenManager.current_screen.ids.continueButton.dispatch(
        "on_press"
    )

    assert app_with_only_users.screenManager.current == "topUpPaymentScreen"

    app_with_only_users.screenManager.current_screen.ids.cancelButton.dispatch(
        "on_press"
    )

    assert app_with_only_users.screenManager.current == "mainUserPage"


@pytest.mark.asyncio
async def test_add_hundred_credits(app_with_only_users):

    assert app_with_only_users.screenManager.current == "splashScreen"

    assert (
        app_with_only_users.screenManager.database.getPatronIdByCardId("123456789")
        is not None
    )

    patron_id = app_with_only_users.screenManager.database.getPatronIdByCardId(
        "123456789"
    )

    patron_data = app_with_only_users.screenManager.database.getPatronData(patron_id)

    initial_credits = patron_data.totalCredits

    app_with_only_users.screenManager.RFIDReader.triggerFakeRead(card_id="123456789")

    assert app_with_only_users.screenManager.current == "mainUserPage"

    app_with_only_users.screenManager.current_screen.ids.topUpOption.dispatch(
        "on_release"
    )

    assert app_with_only_users.screenManager.current == "topUpAmountScreen"

    app_with_only_users.screenManager.current_screen.ids.creditsToAdd.text = "100.00"

    app_with_only_users.screenManager.current_screen.ids.continueButton.dispatch(
        "on_press"
    )

    assert app_with_only_users.screenManager.current == "topUpPaymentScreen"

    app_with_only_users.screenManager.current_screen.ids.confirmButton.dispatch(
        "on_press"
    )

    assert app_with_only_users.screenManager.current == "mainUserPage"

    patron_data = app_with_only_users.screenManager.database.getPatronData(patron_id)

    assert patron_data.totalCredits == initial_credits + 100.0


@pytest.mark.asyncio
async def test_auto_logout_while_entering_amount(app_with_only_users):

    app_with_only_users.screenManager.settingsManager.set_setting_value(
        settingName=SettingName.AUTO_LOGOUT_ON_IDLE_ENABLE, value=True
    )

    app_with_only_users.screenManager.settingsManager.set_setting_value(
        settingName=SettingName.AUTO_LOGOUT_ON_IDLE_TIME, value=20
    )

    assert app_with_only_users.screenManager.current == "splashScreen"

    assert (
        app_with_only_users.screenManager.database.getPatronIdByCardId("123456789")
        is not None
    )

    app_with_only_users.screenManager.RFIDReader.triggerFakeRead(card_id="123456789")

    assert app_with_only_users.screenManager.current == "mainUserPage"

    app_with_only_users.screenManager.current_screen.ids.topUpOption.dispatch(
        "on_release"
    )

    assert app_with_only_users.screenManager.current == "topUpAmountScreen"

    app_with_only_users.screenManager.current_screen.ids.creditsToAdd.focus = True

    await asyncio.sleep(21)

    assert app_with_only_users.screenManager.current == "splashScreen"

    assert (
        app_with_only_users.screenManager.get_screen(
            "topUpAmountScreen"
        ).credit_input_popup
        is None
    )


@pytest.mark.asyncio
async def test_return_from_top_up_amount_with_back_button_with_buy_screen_as_referee(
    app,
):

    assert app.screenManager.current == "splashScreen"

    assert app.screenManager.database.getPatronIdByCardId("123456789") is not None

    app.screenManager.RFIDReader.triggerFakeRead(card_id="123456789")

    assert app.screenManager.current == "mainUserPage"

    app.screenManager.current_screen.ids.buyOption.dispatch("on_release")

    await asyncio.sleep(0.5)

    assert app.screenManager.current == "buyScreen"

    snacks = app.screenManager.database.getAllSnacks()

    assert len(snacks) == 3

    snack = snacks[2]

    app.screenManager.current_screen.ids.inventoryTable.onEntryPressed(snack.snackId)

    app.screenManager.current_screen.ids.buyButton.dispatch("on_release")

    await asyncio.sleep(0.5)

    app.screenManager.current_screen.insufficient_funds_popup.ids.topUpButton.dispatch(
        "on_press"
    )

    assert app.screenManager.current == "topUpAmountScreen"

    app.screenManager.current_screen.ids.header.ids.backButton.dispatch("on_release")

    assert app.screenManager.current == "buyScreen"


@pytest.mark.asyncio
async def test_return_from_top_up_amount_with_cancel_button_with_buy_screen_as_referee(
    app,
):

    assert app.screenManager.current == "splashScreen"

    assert app.screenManager.database.getPatronIdByCardId("123456789") is not None

    app.screenManager.RFIDReader.triggerFakeRead(card_id="123456789")

    assert app.screenManager.current == "mainUserPage"

    app.screenManager.current_screen.ids.buyOption.dispatch("on_release")

    await asyncio.sleep(0.5)

    assert app.screenManager.current == "buyScreen"

    snacks = app.screenManager.database.getAllSnacks()

    assert len(snacks) == 3

    snack = snacks[2]

    app.screenManager.current_screen.ids.inventoryTable.onEntryPressed(snack.snackId)

    app.screenManager.current_screen.ids.buyButton.dispatch("on_release")

    await asyncio.sleep(0.5)

    app.screenManager.current_screen.insufficient_funds_popup.ids.topUpButton.dispatch(
        "on_press"
    )

    assert app.screenManager.current == "topUpAmountScreen"

    app.screenManager.current_screen.ids.cancelButton.dispatch("on_press")

    assert app.screenManager.current == "buyScreen"


@pytest.mark.asyncio
async def test_top_up_with_buy_screen_as_referee(
    app,
):

    assert app.screenManager.current == "splashScreen"

    assert app.screenManager.database.getPatronIdByCardId("123456789") is not None

    app.screenManager.RFIDReader.triggerFakeRead(card_id="123456789")

    user_id = app.screenManager.database.getPatronIdByCardId("123456789")

    patron_data = app.screenManager.database.getPatronData(user_id)

    initial_credits = patron_data.totalCredits

    assert app.screenManager.current == "mainUserPage"

    app.screenManager.current_screen.ids.buyOption.dispatch("on_release")

    await asyncio.sleep(0.5)

    assert app.screenManager.current == "buyScreen"

    snacks = app.screenManager.database.getAllSnacks()

    assert len(snacks) == 3

    snack1 = snacks[0]
    snack2 = snacks[1]

    # We will buy two of snack1 and all of snack2, so calculate missing credits based on that
    missing_credits = Credits("0.00")
    missing_credits += snack1.pricePerItem * 2
    missing_credits += snack2.pricePerItem * snack2.quantity
    missing_credits -= patron_data.totalCredits

    # Add two of the first snack to the shopping cart
    assert snack1.quantity >= 2
    for _ in range(2):
        app.screenManager.current_screen.ids.inventoryTable.onEntryPressed(
            snack1.snackId
        )

    # Add all of snack2
    for _ in range(snack2.quantity):
        app.screenManager.current_screen.ids.inventoryTable.onEntryPressed(
            snack2.snackId
        )

    app.screenManager.current_screen.ids.buyButton.dispatch("on_release")

    await asyncio.sleep(0.5)

    app.screenManager.current_screen.insufficient_funds_popup.ids.topUpButton.dispatch(
        "on_press"
    )

    assert app.screenManager.current == "topUpAmountScreen"

    assert app.screenManager.current_screen.ids.creditsToAdd.text == str(
        f"{missing_credits:.2f}"
    )

    app.screenManager.current_screen.ids.continueButton.dispatch("on_press")

    assert app.screenManager.current == "topUpPaymentScreen"

    app.screenManager.current_screen.ids.confirmButton.dispatch("on_press")

    assert app.screenManager.current == "buyScreen"

    patron_data = app.screenManager.database.getPatronData(user_id)

    assert patron_data.totalCredits == initial_credits + missing_credits

    entries_in_shopping_cart_table = (
        app.screenManager.current_screen.ids.shoppingCartTable.ids.rw.data
    )

    # Originally added snacks should still be in shopping cart
    assert len(entries_in_shopping_cart_table) == 2
    assert entries_in_shopping_cart_table[0]["entryIdentifier"] == snack1.snackId
    assert entries_in_shopping_cart_table[0]["entryContents"][0] == snack1.snackName
    assert int(entries_in_shopping_cart_table[0]["entryContents"][1]) == 2

    assert entries_in_shopping_cart_table[1]["entryIdentifier"] == snack2.snackId
    assert entries_in_shopping_cart_table[1]["entryContents"][0] == snack2.snackName
    assert int(entries_in_shopping_cart_table[1]["entryContents"][1]) == snack2.quantity

    entries_in_inventory_table = (
        app.screenManager.current_screen.ids.inventoryTable.ids.rw.data
    )

    # Inventory should be updated correctly and remember reduced quantity
    assert app.screenManager.current_screen.ids.inventoryTable.hasEntry(snack1.snackId)
    assert not app.screenManager.current_screen.ids.inventoryTable.hasEntry(
        snack2.snackId
    )

    for entry in entries_in_inventory_table:
        if entry["entryIdentifier"] == snack1.snackId:
            assert int(entry["entryContents"][1]) == snack1.quantity - 2


@pytest.mark.asyncio
async def test_return_from_top_up_amount_with_back_button_with_wheel_of_snacks_screen_as_referee(
    app,
):

    assert app.screenManager.current == "splashScreen"

    assert app.screenManager.database.getPatronIdByCardId("123456789") is not None

    app.screenManager.RFIDReader.triggerFakeRead(card_id="123456789")

    assert app.screenManager.current == "mainUserPage"

    app.screenManager.current_screen.ids.gambleOption.dispatch("on_release")

    await asyncio.sleep(0.5)

    assert app.screenManager.current == "wheelOfSnacksScreen"

    app.screenManager.current_screen.ids.spin_button.dispatch("on_press")

    await asyncio.sleep(0.5)

    app.screenManager.current_screen.insufficient_funds_popup.ids.topUpButton.dispatch(
        "on_press"
    )

    assert app.screenManager.current == "topUpAmountScreen"

    app.screenManager.current_screen.ids.header.ids.backButton.dispatch("on_release")

    assert app.screenManager.current == "wheelOfSnacksScreen"


@pytest.mark.asyncio
async def test_return_from_top_up_amount_with_cancel_button_with_wheel_of_snacks_screen_as_referee(
    app,
):

    assert app.screenManager.current == "splashScreen"

    assert app.screenManager.database.getPatronIdByCardId("123456789") is not None

    app.screenManager.RFIDReader.triggerFakeRead(card_id="123456789")

    assert app.screenManager.current == "mainUserPage"

    app.screenManager.current_screen.ids.gambleOption.dispatch("on_release")

    await asyncio.sleep(0.5)

    assert app.screenManager.current == "wheelOfSnacksScreen"

    app.screenManager.current_screen.ids.spin_button.dispatch("on_press")

    await asyncio.sleep(0.5)

    app.screenManager.current_screen.insufficient_funds_popup.ids.topUpButton.dispatch(
        "on_press"
    )

    assert app.screenManager.current == "topUpAmountScreen"

    app.screenManager.current_screen.ids.cancelButton.dispatch("on_press")

    assert app.screenManager.current == "wheelOfSnacksScreen"


@pytest.mark.asyncio
async def test_top_up_with_wheel_of_snacks_screen_as_referee(
    app,
):

    assert app.screenManager.current == "splashScreen"

    assert app.screenManager.database.getPatronIdByCardId("123456789") is not None

    app.screenManager.RFIDReader.triggerFakeRead(card_id="123456789")

    assert app.screenManager.current == "mainUserPage"

    app.screenManager.current_screen.ids.gambleOption.dispatch("on_release")

    await asyncio.sleep(0.5)

    assert app.screenManager.current == "wheelOfSnacksScreen"

    snacks_in_inventory = app.screenManager.database.getAllSnacks()
    total_cost_of_snacks = sum(s.pricePerItem for s in snacks_in_inventory)
    cost_to_gamble = total_cost_of_snacks / len(snacks_in_inventory)

    current_patron = app.screenManager.getCurrentPatron()
    missing_credits = cost_to_gamble - current_patron.totalCredits
    assert missing_credits > 0  # Ensure some credits are missing

    app.screenManager.current_screen.ids.spin_button.dispatch("on_press")

    await asyncio.sleep(0.5)

    app.screenManager.current_screen.insufficient_funds_popup.ids.topUpButton.dispatch(
        "on_press"
    )

    assert app.screenManager.current == "topUpAmountScreen"

    assert app.screenManager.current_screen.ids.creditsToAdd.text == str(
        f"{missing_credits:.2f}"
    )

    app.screenManager.current_screen.ids.continueButton.dispatch("on_press")

    assert app.screenManager.current == "topUpPaymentScreen"

    app.screenManager.current_screen.ids.confirmButton.dispatch("on_press")

    assert app.screenManager.current == "wheelOfSnacksScreen"

    current_patron = app.screenManager.getCurrentPatron()
    assert current_patron.totalCredits >= cost_to_gamble
