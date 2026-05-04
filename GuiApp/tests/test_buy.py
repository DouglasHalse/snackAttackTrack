import pytest

from app_types import Credits
from widgets.settingsManager import SettingName


@pytest.mark.asyncio
async def test_return_from_buy_screen_with_back_button(app_on_buy_screen):
    app = app_on_buy_screen

    assert app.screenManager.current == "buyScreen"

    app.screenManager.current_screen.ids.header.ids.backButton.dispatch("on_release")

    assert app.screenManager.current == "mainUserPage"


@pytest.mark.asyncio
async def test_return_from_buy_screen_with_cancel_button(app_on_buy_screen):
    app = app_on_buy_screen

    assert app.screenManager.current == "buyScreen"

    app.screenManager.current_screen.ids.cancelButton.dispatch("on_release")

    assert app.screenManager.current == "mainUserPage"


@pytest.mark.asyncio
async def test_inventory_contains_all_available_snacks(app_on_buy_screen):
    app = app_on_buy_screen

    all_snacks_in_db = app.screenManager.database.getAllSnacks()
    assert len(all_snacks_in_db) > 0

    for snack in all_snacks_in_db:
        assert app.screenManager.current_screen.ids.inventoryTable.hasEntry(
            snack.snackId
        )


@pytest.mark.asyncio
async def test_try_buying_with_empty_cart(app_on_buy_screen):
    app = app_on_buy_screen

    assert app.screenManager.current == "buyScreen"

    app.screenManager.current_screen.ids.buyButton.dispatch("on_release")

    # Assert that we are still on the buy screen
    assert app.screenManager.current == "buyScreen"


@pytest.mark.asyncio
async def test_clicking_widget_in_inventory_adds_to_cart(app_on_buy_screen):
    app = app_on_buy_screen

    snacks_in_cart_before = len(
        app.screenManager.current_screen.ids.shoppingCartTable.getEntries()
    )

    app.screenManager.current_screen.ids.inventoryTable.ids.rw.children[0].children[
        0
    ].onPress()

    snacks_in_cart_after = len(
        app.screenManager.current_screen.ids.shoppingCartTable.getEntries()
    )

    assert snacks_in_cart_after == snacks_in_cart_before + 1


@pytest.mark.asyncio
async def test_buy_add_two_snacks_then_regret_one(app_on_buy_screen):
    app = app_on_buy_screen

    snacks = app.screenManager.database.getAllSnacks()
    user = app.screenManager.getCurrentPatron()

    assert len(snacks) >= 2

    snack1 = snacks[0]
    snack2 = snacks[1]

    assert app.screenManager.current_screen.ids.inventoryTable.hasEntry(snack1.snackId)
    assert app.screenManager.current_screen.ids.inventoryTable.hasEntry(snack2.snackId)
    assert not app.screenManager.current_screen.ids.shoppingCartTable.hasEntry(
        snack1.snackId
    )
    assert not app.screenManager.current_screen.ids.shoppingCartTable.hasEntry(
        snack2.snackId
    )

    app.screenManager.current_screen.itemClickedInInventory(snackId=snack1.snackId)
    app.screenManager.current_screen.itemClickedInInventory(snackId=snack2.snackId)

    assert app.screenManager.current_screen.ids.inventoryTable.hasEntry(snack1.snackId)
    assert app.screenManager.current_screen.ids.inventoryTable.hasEntry(snack2.snackId)
    assert app.screenManager.current_screen.ids.shoppingCartTable.hasEntry(
        snack1.snackId
    )
    assert app.screenManager.current_screen.ids.shoppingCartTable.hasEntry(
        snack2.snackId
    )

    app.screenManager.current_screen.itemClickedInShoppingCart(snackId=snack2.snackId)

    assert app.screenManager.current_screen.ids.inventoryTable.hasEntry(snack2.snackId)
    assert not app.screenManager.current_screen.ids.shoppingCartTable.hasEntry(
        snack2.snackId
    )

    assert user.totalCredits >= snack1.pricePerItem

    app.screenManager.current_screen.ids.buyButton.dispatch("on_release")

    assert app.screenManager.current == "mainUserPage"

    assert (
        app.screenManager.database.getPatronData(user.patronId).totalCredits
        == user.totalCredits - snack1.pricePerItem
    )


@pytest.mark.asyncio
async def test_moving_all_of_one_snack_to_cart_and_back(app_on_buy_screen):
    app = app_on_buy_screen

    snacks = app.screenManager.database.getAllSnacks()
    assert len(snacks) >= 1

    snack = app.screenManager.database.getAllSnacks()[0]

    snacks_in_inventory_before = len(
        app.screenManager.current_screen.ids.inventoryTable.getEntries()
    )
    snacks_in_cart_before = len(
        app.screenManager.current_screen.ids.shoppingCartTable.getEntries()
    )
    assert app.screenManager.current_screen.ids.inventoryTable.hasEntry(snack.snackId)
    assert not app.screenManager.current_screen.ids.shoppingCartTable.hasEntry(
        snack.snackId
    )

    for _ in range(snack.quantity):
        app.screenManager.current_screen.itemClickedInInventory(snackId=snack.snackId)

    snacks_in_inventory_after = len(
        app.screenManager.current_screen.ids.inventoryTable.getEntries()
    )
    snacks_in_cart_after = len(
        app.screenManager.current_screen.ids.shoppingCartTable.getEntries()
    )

    assert snacks_in_inventory_after == snacks_in_inventory_before - 1
    assert snacks_in_cart_after == snacks_in_cart_before + 1
    assert not app.screenManager.current_screen.ids.inventoryTable.hasEntry(
        snack.snackId
    )
    assert app.screenManager.current_screen.ids.shoppingCartTable.hasEntry(
        snack.snackId
    )

    for _ in range(snack.quantity):
        app.screenManager.current_screen.itemClickedInShoppingCart(
            snackId=snack.snackId
        )

    snacks_in_inventory_final = len(
        app.screenManager.current_screen.ids.inventoryTable.getEntries()
    )
    snacks_in_cart_final = len(
        app.screenManager.current_screen.ids.shoppingCartTable.getEntries()
    )
    assert snacks_in_inventory_final == snacks_in_inventory_before
    assert snacks_in_cart_final == snacks_in_cart_before
    assert app.screenManager.current_screen.ids.inventoryTable.hasEntry(snack.snackId)
    assert not app.screenManager.current_screen.ids.shoppingCartTable.hasEntry(
        snack.snackId
    )


@pytest.mark.asyncio
async def test_not_enough_credits(app_on_buy_screen):
    app = app_on_buy_screen

    snacks = app.screenManager.database.getAllSnacks()
    assert len(snacks) == 3

    snack3 = app.screenManager.database.getAllSnacks()[2]

    users_credits_before = app.screenManager.getCurrentPatron().totalCredits

    assert snack3.pricePerItem > users_credits_before

    app.screenManager.current_screen.itemClickedInInventory(snackId=snack3.snackId)
    app.screenManager.current_screen.ids.buyButton.dispatch("on_release")

    # Assert that we are still on the buy screen
    assert app.screenManager.current == "buyScreen"

    # Assert that the user still has the same amount of credits
    assert (
        app.screenManager.database.getPatronData(
            app.screenManager.getCurrentPatron().patronId
        ).totalCredits
        == users_credits_before
    )

    # Assert that no snack quantity has been changed in the database
    snack3_after = app.screenManager.database.getSnack(snack3.snackId)
    assert snack3_after.quantity == snack3.quantity


@pytest.mark.asyncio
async def test_buy_one_cheap_snack(app_on_buy_screen):
    app = app_on_buy_screen

    snacks = app.screenManager.database.getAllSnacks()
    assert len(snacks) == 3

    snack1 = app.screenManager.database.getAllSnacks()[0]

    users_credits_before = app.screenManager.getCurrentPatron().totalCredits

    assert snack1.pricePerItem < users_credits_before

    app.screenManager.current_screen.itemClickedInInventory(snackId=snack1.snackId)
    app.screenManager.current_screen.ids.buyButton.dispatch("on_release")

    # Assert that we are back on the main user page
    assert app.screenManager.current == "mainUserPage"

    # Assert that the user has the correct amount of credits after the purchase
    assert (
        app.screenManager.database.getPatronData(
            app.screenManager.getCurrentPatron().patronId
        ).totalCredits
        == users_credits_before - snack1.pricePerItem
    )

    # Assert that the snack quantity has been updated correctly in the database
    snack1_after = app.screenManager.database.getSnack(snack1.snackId)
    assert snack1_after.quantity == snack1.quantity - 1


@pytest.mark.asyncio
async def test_buy_all_of_one_snack(app_on_buy_screen):
    app = app_on_buy_screen

    # Add credits to the user so that they can buy snacks
    app.screenManager.database.addCredits(
        userId=app.screenManager.getCurrentPatron().patronId, amount=Credits("10000.00")
    )

    app.screenManager.refreshCurrentPatron()

    snacks = app.screenManager.database.getAllSnacks()
    assert len(snacks) == 3

    snack1 = app.screenManager.database.getAllSnacks()[0]

    users_credits_before = app.screenManager.getCurrentPatron().totalCredits

    total_price = snack1.pricePerItem * snack1.quantity

    assert total_price < users_credits_before

    for _ in range(snack1.quantity):
        app.screenManager.current_screen.itemClickedInInventory(snackId=snack1.snackId)

    app.screenManager.current_screen.ids.buyButton.dispatch("on_release")

    # Assert that we are back on the main user page
    assert app.screenManager.current == "mainUserPage"

    # Assert that the user has the correct amount of credits after the purchase
    assert (
        app.screenManager.database.getPatronData(
            app.screenManager.getCurrentPatron().patronId
        ).totalCredits
        == users_credits_before - total_price
    )

    # Assert that the snack has been removed from the database since all of it was bought
    assert app.screenManager.database.getSnack(snack1.snackId) is None


@pytest.mark.asyncio
async def test_buy_five_of_each_snack(app_on_buy_screen):
    app = app_on_buy_screen

    # Add credits to the user so that they can buy snacks
    app.screenManager.database.addCredits(
        userId=app.screenManager.getCurrentPatron().patronId, amount=Credits("10000.00")
    )

    app.screenManager.refreshCurrentPatron()

    snacks = app.screenManager.database.getAllSnacks()
    assert len(snacks) == 3

    for snack in snacks:
        assert snack.quantity >= 5

    total_price = sum(snack.pricePerItem * 5 for snack in snacks)

    users_credits_before = app.screenManager.getCurrentPatron().totalCredits

    assert total_price <= users_credits_before

    for snack in snacks:
        for _ in range(5):
            app.screenManager.current_screen.itemClickedInInventory(
                snackId=snack.snackId
            )

    app.screenManager.current_screen.ids.buyButton.dispatch("on_release")

    # Assert that we are back on the main user page
    assert app.screenManager.current == "mainUserPage"

    # Assert that the user has the correct amount of credits after the purchase
    assert (
        app.screenManager.database.getPatronData(
            app.screenManager.getCurrentPatron().patronId
        ).totalCredits
        == users_credits_before - total_price
    )

    # Assert that the snack quantities have been updated correctly in the database
    for snack in snacks:
        if snack.quantity > 5:
            snack_after = app.screenManager.database.getSnack(snack.snackId)
            assert snack_after.quantity == snack.quantity - 5
        else:
            assert app.screenManager.database.getSnack(snack.snackId) is None


@pytest.mark.asyncio
async def test_auto_logout_after_purchase(app_on_buy_screen):
    app = app_on_buy_screen

    app.screenManager.settingsManager.set_setting_value(
        SettingName.AUTO_LOGOUT_AFTER_PURCHASE, True
    )

    user = app.screenManager.getCurrentPatron()

    snacks = app.screenManager.database.getAllSnacks()
    assert len(snacks) == 3

    snack1 = app.screenManager.database.getAllSnacks()[0]

    users_credits_before = app.screenManager.getCurrentPatron().totalCredits

    assert snack1.pricePerItem < users_credits_before

    app.screenManager.current_screen.itemClickedInInventory(snackId=snack1.snackId)
    app.screenManager.current_screen.ids.buyButton.dispatch("on_release")

    # Assert that we are back on the main user page
    assert app.screenManager.current == "splashScreen"

    # Assert that the user has the correct amount of credits after the purchase
    assert (
        app.screenManager.database.getPatronData(user.patronId).totalCredits
        == users_credits_before - snack1.pricePerItem
    )

    snack1_after = app.screenManager.database.getSnack(snack1.snackId)
    assert snack1_after.quantity == snack1.quantity - 1


@pytest.mark.asyncio
async def test_order_is_changed_after_purchase(app_on_buy_screen):
    app = app_on_buy_screen

    # Add credits to the user so that they can buy snacks
    app.screenManager.database.addCredits(
        userId=app.screenManager.getCurrentPatron().patronId, amount=Credits("10000.00")
    )

    app.screenManager.refreshCurrentPatron()

    snacks = app.screenManager.database.getAllSnacks()
    assert len(snacks) == 3

    snack1 = app.screenManager.database.getAllSnacks()[0]
    snack2 = app.screenManager.database.getAllSnacks()[1]
    snack3 = app.screenManager.database.getAllSnacks()[2]

    entries_in_inventory_table_before = (
        app.screenManager.current_screen.ids.inventoryTable.ids.rw.data
    )

    entry1 = entries_in_inventory_table_before[0]
    entry2 = entries_in_inventory_table_before[1]
    entry3 = entries_in_inventory_table_before[2]

    assert entry1["entryIdentifier"] == snack1.snackId
    assert entry2["entryIdentifier"] == snack2.snackId
    assert entry3["entryIdentifier"] == snack3.snackId

    app.screenManager.current_screen.itemClickedInInventory(snackId=snack3.snackId)

    app.screenManager.current_screen.ids.buyButton.dispatch("on_release")

    assert app.screenManager.current == "mainUserPage"

    app.screenManager.current_screen.ids.buyOption.dispatch("on_release")

    assert app.screenManager.current == "buyScreen"

    entries_in_inventory_table_after = (
        app.screenManager.current_screen.ids.inventoryTable.ids.rw.data
    )

    entry1 = entries_in_inventory_table_after[0]
    entry2 = entries_in_inventory_table_after[1]
    entry3 = entries_in_inventory_table_after[2]

    # Snack 3 should now be in the first position in the inventory table since its the most purchased snack for this user
    assert entry1["entryIdentifier"] == snack3.snackId
    assert entry2["entryIdentifier"] == snack1.snackId
    assert entry3["entryIdentifier"] == snack2.snackId


@pytest.mark.asyncio
async def test_order_is_not_changed_after_purchase(app_on_buy_screen):
    app = app_on_buy_screen

    # Add credits to the user so that they can buy snacks
    app.screenManager.database.addCredits(
        userId=app.screenManager.getCurrentPatron().patronId, amount=Credits("10000.00")
    )

    app.screenManager.refreshCurrentPatron()

    app.screenManager.settingsManager.set_setting_value(
        SettingName.ORDER_INVENTORY_BY_MOST_PURCHASED, False
    )

    snacks = app.screenManager.database.getAllSnacks()
    assert len(snacks) == 3

    snack1 = app.screenManager.database.getAllSnacks()[0]
    snack2 = app.screenManager.database.getAllSnacks()[1]
    snack3 = app.screenManager.database.getAllSnacks()[2]

    entries_in_inventory_table_before = (
        app.screenManager.current_screen.ids.inventoryTable.ids.rw.data
    )

    entry1 = entries_in_inventory_table_before[0]
    entry2 = entries_in_inventory_table_before[1]
    entry3 = entries_in_inventory_table_before[2]

    assert entry1["entryIdentifier"] == snack1.snackId
    assert entry2["entryIdentifier"] == snack2.snackId
    assert entry3["entryIdentifier"] == snack3.snackId

    app.screenManager.current_screen.itemClickedInInventory(snackId=snack3.snackId)

    app.screenManager.current_screen.ids.buyButton.dispatch("on_release")

    assert app.screenManager.current == "mainUserPage"

    app.screenManager.current_screen.ids.buyOption.dispatch("on_release")

    assert app.screenManager.current == "buyScreen"

    entries_in_inventory_table_after = (
        app.screenManager.current_screen.ids.inventoryTable.ids.rw.data
    )

    entry1 = entries_in_inventory_table_after[0]
    entry2 = entries_in_inventory_table_after[1]
    entry3 = entries_in_inventory_table_after[2]

    # The order of the snacks in the inventory table should not have changed since the setting to order by most purchased is disabled
    assert entry1["entryIdentifier"] == snack1.snackId
    assert entry2["entryIdentifier"] == snack2.snackId
    assert entry3["entryIdentifier"] == snack3.snackId
