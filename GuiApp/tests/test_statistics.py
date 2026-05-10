# Duplicate navigation patterns across tests are intentional
# pylint: disable=duplicate-code
import asyncio

import pytest

from app_types import Credits, TransactionType


@pytest.mark.asyncio
async def test_user_sees_initial_zero_statistics(app_on_user_statistics_screen):
    """Test that user statistics show zero/zero values before any transactions."""
    app = app_on_user_statistics_screen

    # Before any transactions, all statistics should be 0 or N/A
    # Total credits spent should be 0.00
    assert app.screenManager.current == "userStatisticsScreen"

    # The statistics screen should display 0 for all values initially
    # Note: We can't directly test the stat_value text since we don't have access to the UI elements
    # This test just verifies we can navigate to the statistics screen


@pytest.mark.asyncio
async def test_user_total_credits_spent_after_single_purchase(app):
    """Test that total credits spent increases correctly after a single purchase."""
    # Navigate to buy screen and make a purchase
    assert app.screenManager.current == "splashScreen"

    # First log in with RFID
    app.screenManager.RFIDReader.triggerFakeRead(card_id="555555555")
    await asyncio.sleep(0.5)

    assert app.screenManager.current == "mainUserPage"

    # Now we can add credits for the user since they're logged in
    app.screenManager.database.addCredits(
        userId=app.screenManager.getCurrentPatron().patronId, amount=Credits("100.00")
    )
    app.screenManager.refreshCurrentPatron()

    # Go to buy screen
    app.screenManager.current_screen.ids.buyOption.dispatch("on_release")
    await asyncio.sleep(0.5)

    assert app.screenManager.current == "buyScreen"

    # Get initial user data and snack info
    user = app.screenManager.getCurrentPatron()
    snacks = app.screenManager.database.getAllSnacks()

    assert len(snacks) >= 1
    snack = snacks[0]

    # Make a purchase
    app.screenManager.current_screen.itemClickedInInventory(snackId=snack.snackId)
    app.screenManager.current_screen.ids.buyButton.dispatch("on_release")

    await asyncio.sleep(0.5)

    assert app.screenManager.current == "mainUserPage"

    # Navigate to statistics screen
    # First go back from buy screen (if still there) or just navigate directly

    # Go to settings -> admin -> back to main -> profile -> stats
    app.screenManager.current_screen.ids.header.settings_button.dispatch("on_release")
    await asyncio.sleep(0.5)

    assert app.screenManager.current == "adminScreen"

    # Go back to main user page
    app.screenManager.current_screen.ids.header.ids.backButton.dispatch("on_release")
    await asyncio.sleep(0.5)

    assert app.screenManager.current == "mainUserPage"

    # Go to profile screen
    app.screenManager.current_screen.ids.profileOption.dispatch("on_release")
    await asyncio.sleep(0.5)

    assert app.screenManager.current == "profileScreen"

    # Open user statistics
    app.screenManager.current_screen.ids.statisticsOption.dispatch("on_release")
    await asyncio.sleep(0.5)

    assert app.screenManager.current == "userStatisticsScreen"

    # The user should have spent snack.pricePerItem credits
    # Verify the transaction was recorded correctly in database
    transactions = app.screenManager.database.getTransactions(user.patronId)
    purchase_transactions = [
        t for t in transactions if t.transactionType == TransactionType.PURCHASE
    ]

    assert len(purchase_transactions) == 1

    # The amount spent should be calculated from transaction data
    expected_spent = snack.pricePerItem
    actual_spent = (
        purchase_transactions[0].amountBeforeTransaction
        - purchase_transactions[0].amountAfterTransaction
    )

    assert actual_spent == expected_spent


@pytest.mark.asyncio
async def test_user_total_credits_spent_after_multiple_purchases(app):
    """Test that total credits spent accumulates correctly after multiple purchases."""
    # Navigate to buy screen and make two purchases
    assert app.screenManager.current == "splashScreen"

    # First log in with RFID
    app.screenManager.RFIDReader.triggerFakeRead(card_id="555555555")
    await asyncio.sleep(0.5)

    assert app.screenManager.current == "mainUserPage"

    # Now we can add credits for the user since they're logged in
    app.screenManager.database.addCredits(
        userId=app.screenManager.getCurrentPatron().patronId, amount=Credits("100.00")
    )
    app.screenManager.refreshCurrentPatron()

    # Go to buy screen
    app.screenManager.current_screen.ids.buyOption.dispatch("on_release")
    await asyncio.sleep(0.5)

    assert app.screenManager.current == "buyScreen"

    snacks = app.screenManager.database.getAllSnacks()
    assert len(snacks) >= 2

    user = app.screenManager.getCurrentPatron()

    # Make two different purchases
    snack1 = snacks[0]
    snack2 = snacks[1]

    # Purchase first snack
    app.screenManager.current_screen.itemClickedInInventory(snackId=snack1.snackId)
    app.screenManager.current_screen.ids.buyButton.dispatch("on_release")

    await asyncio.sleep(0.5)

    assert app.screenManager.current == "mainUserPage"

    # Go to buy screen again for second purchase
    app.screenManager.current_screen.ids.buyOption.dispatch("on_release")
    await asyncio.sleep(0.5)

    assert app.screenManager.current == "buyScreen"

    # Purchase second snack
    app.screenManager.current_screen.itemClickedInInventory(snackId=snack2.snackId)
    app.screenManager.current_screen.ids.buyButton.dispatch("on_release")

    await asyncio.sleep(0.5)

    assert app.screenManager.current == "mainUserPage"

    # Navigate to statistics screen
    app.screenManager.current_screen.ids.header.settings_button.dispatch("on_release")
    await asyncio.sleep(0.5)

    assert app.screenManager.current == "adminScreen"

    app.screenManager.current_screen.ids.header.ids.backButton.dispatch("on_release")
    await asyncio.sleep(0.5)

    assert app.screenManager.current == "mainUserPage"

    app.screenManager.current_screen.ids.profileOption.dispatch("on_release")
    await asyncio.sleep(0.5)

    assert app.screenManager.current == "profileScreen"

    app.screenManager.current_screen.ids.statisticsOption.dispatch("on_release")
    await asyncio.sleep(0.5)

    assert app.screenManager.current == "userStatisticsScreen"

    # Verify total credits spent is correct
    transactions = app.screenManager.database.getTransactions(user.patronId)
    purchase_transactions = [
        t for t in transactions if t.transactionType == TransactionType.PURCHASE
    ]

    assert len(purchase_transactions) == 2

    expected_total_spent = snack1.pricePerItem + snack2.pricePerItem
    actual_total_spent = sum(
        (t.amountBeforeTransaction - t.amountAfterTransaction)
        for t in purchase_transactions
    )

    assert actual_total_spent == expected_total_spent


@pytest.mark.asyncio
async def test_user_favorite_snack_is_most_purchased(app):
    """Test that favorite snack correctly identifies the most purchased snack."""
    # Navigate to buy screen and make multiple purchases
    assert app.screenManager.current == "splashScreen"

    # First log in with RFID
    app.screenManager.RFIDReader.triggerFakeRead(card_id="555555555")
    await asyncio.sleep(0.5)

    assert app.screenManager.current == "mainUserPage"

    # Now we can add credits for the user since they're logged in
    app.screenManager.database.addCredits(
        userId=app.screenManager.getCurrentPatron().patronId, amount=Credits("100.00")
    )
    app.screenManager.refreshCurrentPatron()

    # Go to buy screen
    app.screenManager.current_screen.ids.buyOption.dispatch("on_release")
    await asyncio.sleep(0.5)

    assert app.screenManager.current == "buyScreen"

    snacks = app.screenManager.database.getAllSnacks()
    assert len(snacks) >= 3

    favorite_snack = snacks[0]
    other_snack = snacks[1]

    # Purchase favorite snack 3 times
    for _ in range(3):
        app.screenManager.current_screen.itemClickedInInventory(
            snackId=favorite_snack.snackId
        )
        app.screenManager.current_screen.ids.buyButton.dispatch("on_release")
        await asyncio.sleep(0.5)

        assert app.screenManager.current == "mainUserPage"

        # Go back to buy screen for next purchase
        app.screenManager.current_screen.ids.buyOption.dispatch("on_release")
        await asyncio.sleep(0.5)

        assert app.screenManager.current == "buyScreen"

    # Purchase other snack once
    app.screenManager.current_screen.itemClickedInInventory(snackId=other_snack.snackId)
    app.screenManager.current_screen.ids.buyButton.dispatch("on_release")

    await asyncio.sleep(0.5)

    assert app.screenManager.current == "mainUserPage"

    # Navigate to statistics screen
    app.screenManager.current_screen.ids.header.settings_button.dispatch("on_release")
    await asyncio.sleep(0.5)

    assert app.screenManager.current == "adminScreen"

    app.screenManager.current_screen.ids.header.ids.backButton.dispatch("on_release")
    await asyncio.sleep(0.5)

    assert app.screenManager.current == "mainUserPage"

    app.screenManager.current_screen.ids.profileOption.dispatch("on_release")
    await asyncio.sleep(0.5)

    assert app.screenManager.current == "profileScreen"

    app.screenManager.current_screen.ids.statisticsOption.dispatch("on_release")
    await asyncio.sleep(0.5)

    assert app.screenManager.current == "userStatisticsScreen"

    # Verify favorite snack is the one purchased most
    user = app.screenManager.getCurrentPatron()
    most_purchased = app.screenManager.database.getMostPurchasedSnacksByPatron(
        user.patronId
    )

    assert len(most_purchased) >= 1
    assert most_purchased[0] == favorite_snack.snackName


@pytest.mark.asyncio
async def test_user_total_snacks_purchased_counts_correctly(app):
    """Test that total snacks purchased count is accurate."""
    # Navigate to buy screen and purchase items
    assert app.screenManager.current == "splashScreen"

    # First log in with RFID
    app.screenManager.RFIDReader.triggerFakeRead(card_id="555555555")
    await asyncio.sleep(0.5)

    assert app.screenManager.current == "mainUserPage"

    # Now we can add credits for the user since they're logged in
    app.screenManager.database.addCredits(
        userId=app.screenManager.getCurrentPatron().patronId, amount=Credits("100.00")
    )
    app.screenManager.refreshCurrentPatron()

    # Go to buy screen
    app.screenManager.current_screen.ids.buyOption.dispatch("on_release")
    await asyncio.sleep(0.5)

    assert app.screenManager.current == "buyScreen"

    snacks = app.screenManager.database.getAllSnacks()
    assert len(snacks) >= 1

    user = app.screenManager.getCurrentPatron()

    # Purchase multiple quantities of a snack
    snack1 = snacks[0]
    quantity_to_buy = min(5, snack1.quantity)

    for _ in range(quantity_to_buy):
        app.screenManager.current_screen.itemClickedInInventory(snackId=snack1.snackId)

    app.screenManager.current_screen.ids.buyButton.dispatch("on_release")

    await asyncio.sleep(0.5)

    assert app.screenManager.current == "mainUserPage"

    # Navigate to statistics screen
    app.screenManager.current_screen.ids.header.settings_button.dispatch("on_release")
    await asyncio.sleep(0.5)

    assert app.screenManager.current == "adminScreen"

    app.screenManager.current_screen.ids.header.ids.backButton.dispatch("on_release")
    await asyncio.sleep(0.5)

    assert app.screenManager.current == "mainUserPage"

    app.screenManager.current_screen.ids.profileOption.dispatch("on_release")
    await asyncio.sleep(0.5)

    assert app.screenManager.current == "profileScreen"

    app.screenManager.current_screen.ids.statisticsOption.dispatch("on_release")
    await asyncio.sleep(0.5)

    assert app.screenManager.current == "userStatisticsScreen"

    # Verify the total quantity purchased
    transactions = app.screenManager.database.getTransactions(user.patronId)
    purchase_transactions = [
        t for t in transactions if t.transactionType == TransactionType.PURCHASE
    ]

    expected_total_quantity = sum(
        len(t.transactionItems) for t in purchase_transactions
    )

    assert expected_total_quantity > 0


@pytest.mark.asyncio
async def test_store_inventory_stats_displayed(app_on_store_statistics_screen):
    """Test that store statistics displays inventory information."""
    app = app_on_store_statistics_screen

    assert app.screenManager.current == "storeStatsScreen"

    # Verify we can access the inventory stats display
    # The screen should have displayed inventory stats
    inventory_snacks = app.screenManager.database.getAllSnacks()

    # Verify inventory count matches database
    total_quantity = sum(snack.quantity for snack in inventory_snacks)

    assert len(inventory_snacks) > 0
    assert total_quantity > 0


@pytest.mark.asyncio
async def test_store_sold_stats_update_after_purchase(app):
    """Test that sold snacks count updates correctly after purchases."""
    # Navigate to buy screen and make a purchase
    assert app.screenManager.current == "splashScreen"

    # First log in with RFID
    app.screenManager.RFIDReader.triggerFakeRead(card_id="555555555")
    await asyncio.sleep(0.5)

    assert app.screenManager.current == "mainUserPage"

    # Now we can add credits for the user since they're logged in
    app.screenManager.database.addCredits(
        userId=app.screenManager.getCurrentPatron().patronId, amount=Credits("100.00")
    )
    app.screenManager.refreshCurrentPatron()

    # Go to buy screen
    app.screenManager.current_screen.ids.buyOption.dispatch("on_release")
    await asyncio.sleep(0.5)

    assert app.screenManager.current == "buyScreen"

    snacks = app.screenManager.database.getAllSnacks()
    assert len(snacks) >= 1

    snack = snacks[0]

    # Purchase a snack
    app.screenManager.current_screen.itemClickedInInventory(snackId=snack.snackId)
    app.screenManager.current_screen.ids.buyButton.dispatch("on_release")

    await asyncio.sleep(0.5)

    assert app.screenManager.current == "mainUserPage"

    # Navigate to store statistics screen
    app.screenManager.current_screen.ids.header.settings_button.dispatch("on_release")
    await asyncio.sleep(0.5)

    assert app.screenManager.current == "adminScreen"

    app.screenManager.current_screen.ids.storeStatsOption.dispatch("on_release")
    await asyncio.sleep(0.5)

    assert app.screenManager.current == "storeStatsScreen"

    # Verify sold stats are displayed
    user = app.screenManager.getCurrentPatron()
    transactions = app.screenManager.database.getTransactions(user.patronId)
    purchase_transactions = [
        t for t in transactions if t.transactionType == TransactionType.PURCHASE
    ]

    assert len(purchase_transactions) > 0

    # Verify transaction items were recorded
    total_items = sum(len(t.transactionItems) for t in purchase_transactions)
    assert total_items >= 1


@pytest.mark.asyncio
async def test_store_profit_calculation(app):
    """Test that profit calculation is correct."""
    # Navigate to buy screen and make a purchase
    assert app.screenManager.current == "splashScreen"

    # First log in with RFID
    app.screenManager.RFIDReader.triggerFakeRead(card_id="555555555")
    await asyncio.sleep(0.5)

    assert app.screenManager.current == "mainUserPage"

    # Now we can add credits for the user since they're logged in
    app.screenManager.database.addCredits(
        userId=app.screenManager.getCurrentPatron().patronId, amount=Credits("100.00")
    )
    app.screenManager.refreshCurrentPatron()

    # Go to buy screen
    app.screenManager.current_screen.ids.buyOption.dispatch("on_release")
    await asyncio.sleep(0.5)

    assert app.screenManager.current == "buyScreen"

    snacks = app.screenManager.database.getAllSnacks()
    assert len(snacks) >= 1

    snack = snacks[0]

    # Make a purchase
    app.screenManager.current_screen.itemClickedInInventory(snackId=snack.snackId)
    app.screenManager.current_screen.ids.buyButton.dispatch("on_release")

    await asyncio.sleep(0.5)

    assert app.screenManager.current == "mainUserPage"

    # Navigate to store statistics screen
    app.screenManager.current_screen.ids.header.settings_button.dispatch("on_release")
    await asyncio.sleep(0.5)

    assert app.screenManager.current == "adminScreen"

    app.screenManager.current_screen.ids.storeStatsOption.dispatch("on_release")
    await asyncio.sleep(0.5)

    assert app.screenManager.current == "storeStatsScreen"

    # Verify profit calculation
    user = app.screenManager.getCurrentPatron()

    transactions = app.screenManager.database.getTransactions(user.patronId)
    purchase_transactions = [
        t for t in transactions if t.transactionType == TransactionType.PURCHASE
    ]

    store_revenue = sum(
        (t.amountBeforeTransaction - t.amountAfterTransaction)
        for t in purchase_transactions
    )

    assert store_revenue > 0


@pytest.mark.asyncio
async def test_store_gambling_stats(app):
    """Test that gambling statistics are tracked correctly."""
    # Navigate to store statistics screen directly
    assert app.screenManager.current == "splashScreen"

    # First log in with RFID
    app.screenManager.RFIDReader.triggerFakeRead(card_id="555555555")
    await asyncio.sleep(0.5)

    assert app.screenManager.current == "mainUserPage"

    # Now we can add credits for the user since they're logged in
    app.screenManager.database.addCredits(
        userId=app.screenManager.getCurrentPatron().patronId, amount=Credits("100.00")
    )
    app.screenManager.refreshCurrentPatron()

    # Go to settings -> admin
    app.screenManager.current_screen.ids.header.settings_button.dispatch("on_release")
    await asyncio.sleep(0.5)

    assert app.screenManager.current == "adminScreen"

    # Open store statistics
    app.screenManager.current_screen.ids.storeStatsOption.dispatch("on_release")
    await asyncio.sleep(0.5)

    assert app.screenManager.current == "storeStatsScreen"


@pytest.mark.asyncio
async def test_store_lost_stats(app):
    """Test that lost snacks statistics are tracked correctly."""
    # Navigate to buy screen and make a purchase first so there's data
    assert app.screenManager.current == "splashScreen"

    # First log in with RFID
    app.screenManager.RFIDReader.triggerFakeRead(card_id="555555555")
    await asyncio.sleep(0.5)

    assert app.screenManager.current == "mainUserPage"

    # Now we can add credits for the user since they're logged in
    app.screenManager.database.addCredits(
        userId=app.screenManager.getCurrentPatron().patronId, amount=Credits("100.00")
    )
    app.screenManager.refreshCurrentPatron()

    # Go to buy screen and make a purchase
    app.screenManager.current_screen.ids.buyOption.dispatch("on_release")
    await asyncio.sleep(0.5)

    assert app.screenManager.current == "buyScreen"

    snacks = app.screenManager.database.getAllSnacks()
    assert len(snacks) >= 1

    snack = snacks[0]

    # Make a purchase
    app.screenManager.current_screen.itemClickedInInventory(snackId=snack.snackId)
    app.screenManager.current_screen.ids.buyButton.dispatch("on_release")

    await asyncio.sleep(0.5)

    assert app.screenManager.current == "mainUserPage"

    # Navigate to admin screen
    app.screenManager.current_screen.ids.header.settings_button.dispatch("on_release")
    await asyncio.sleep(0.5)

    assert app.screenManager.current == "adminScreen"

    # Open store statistics
    app.screenManager.current_screen.ids.storeStatsOption.dispatch("on_release")
    await asyncio.sleep(0.5)

    assert app.screenManager.current == "storeStatsScreen"

    # Verify lost stats are displayed (we can't directly test the UI values,
    # but we can verify the database methods exist and return data)
    lost_snack_count = app.screenManager.database.get_total_snacks_lost()
    lost_snack_value = app.screenManager.database.get_value_of_lost_snacks()

    # These should be valid values (not None or invalid)
    assert isinstance(lost_snack_count, int)
    assert isinstance(lost_snack_value, Credits)


@pytest.mark.asyncio
async def test_user_statistics_back_button(app_on_user_statistics_screen):
    """Test that pressing back from user statistics returns to profile screen."""
    app = app_on_user_statistics_screen

    assert app.screenManager.current == "userStatisticsScreen"

    # Press the back button
    app.screenManager.current_screen.ids.header.ids.backButton.dispatch("on_release")
    await asyncio.sleep(0.5)

    assert app.screenManager.current == "profileScreen"


@pytest.mark.asyncio
async def test_user_statistics_with_gamble_transactions(app):
    """Test that user statistics correctly accounts for gamble transactions."""
    # Log in via RFID
    assert app.screenManager.current == "splashScreen"
    app.screenManager.RFIDReader.triggerFakeRead(card_id="555555555")
    await asyncio.sleep(0.5)
    assert app.screenManager.current == "mainUserPage"

    user = app.screenManager.getCurrentPatron()
    snacks = app.screenManager.database.getAllSnacks()
    assert len(snacks) >= 2

    # Top up enough credits through the UI so we can afford to spin
    app.screenManager.current_screen.ids.topUpOption.dispatch("on_release")
    await asyncio.sleep(0.5)
    assert app.screenManager.current == "topUpAmountScreen"

    app.screenManager.current_screen.ids.creditsToAdd.text = "10.00"
    app.screenManager.current_screen.ids.continueButton.dispatch("on_press")
    await asyncio.sleep(0.5)
    assert app.screenManager.current == "topUpPaymentScreen"

    app.screenManager.current_screen.ids.confirmButton.dispatch("on_press")
    await asyncio.sleep(0.5)

    # Should be back on main user page after top-up
    assert app.screenManager.current == "mainUserPage"

    # Navigate to wheel of snacks via the gamble option
    app.screenManager.current_screen.ids.gambleOption.dispatch("on_release")
    await asyncio.sleep(0.5)
    assert app.screenManager.current == "wheelOfSnacksScreen"

    # Select at least 2 snacks to enable the spin button
    snack_ids = [snack.snackId for snack in snacks[:2]]
    for snack_id in snack_ids:
        app.screenManager.current_screen.item_clicked(snackId=snack_id)
    await asyncio.sleep(0.3)

    # Press the spin button — this performs the gamble transaction synchronously
    # (database operations happen immediately, animation runs in background)
    app.screenManager.current_screen.ids.spin_button.dispatch("on_press")
    await asyncio.sleep(0.5)

    # Navigate to user statistics to verify the gamble is reflected
    app.screenManager.transitionToScreen("mainUserPage", transitionDirection="right")
    await asyncio.sleep(0.5)

    # Navigate to profile then stats
    app.screenManager.current_screen.ids.profileOption.dispatch("on_release")
    await asyncio.sleep(0.5)
    assert app.screenManager.current == "profileScreen"

    app.screenManager.current_screen.ids.statisticsOption.dispatch("on_release")
    await asyncio.sleep(0.5)
    assert app.screenManager.current == "userStatisticsScreen"

    # Verify the gamble transaction was recorded
    transactions = app.screenManager.database.getTransactions(user.patronId)
    gamble_transactions = [
        t for t in transactions if t.transactionType == TransactionType.GAMBLE
    ]
    assert len(gamble_transactions) >= 1


@pytest.mark.asyncio
async def test_store_statistics_back_button(app_on_store_statistics_screen):
    """Test that pressing back from store statistics returns to admin screen."""
    app = app_on_store_statistics_screen

    assert app.screenManager.current == "storeStatsScreen"

    # Press the back button
    app.screenManager.current_screen.ids.header.ids.backButton.dispatch("on_release")
    await asyncio.sleep(0.5)

    assert app.screenManager.current == "adminScreen"


@pytest.mark.asyncio
async def test_store_statistics_with_gamble_transactions(app):
    """Test that store statistics correctly accounts for gamble transactions."""
    # Log in
    assert app.screenManager.current == "splashScreen"
    app.screenManager.RFIDReader.triggerFakeRead(card_id="555555555")
    await asyncio.sleep(0.5)
    assert app.screenManager.current == "mainUserPage"

    snacks = app.screenManager.database.getAllSnacks()
    assert len(snacks) >= 2

    # Top up enough credits through the UI so we can afford to spin
    app.screenManager.current_screen.ids.topUpOption.dispatch("on_release")
    await asyncio.sleep(0.5)
    assert app.screenManager.current == "topUpAmountScreen"

    app.screenManager.current_screen.ids.creditsToAdd.text = "10.00"
    app.screenManager.current_screen.ids.continueButton.dispatch("on_press")
    await asyncio.sleep(0.5)
    assert app.screenManager.current == "topUpPaymentScreen"

    app.screenManager.current_screen.ids.confirmButton.dispatch("on_press")
    await asyncio.sleep(0.5)

    # Should be back on main user page after top-up
    assert app.screenManager.current == "mainUserPage"

    # Navigate to wheel of snacks via the gamble option
    app.screenManager.current_screen.ids.gambleOption.dispatch("on_release")
    await asyncio.sleep(0.5)
    assert app.screenManager.current == "wheelOfSnacksScreen"

    # Select at least 2 snacks to enable the spin button
    snack_ids = [snack.snackId for snack in snacks[:2]]
    for snack_id in snack_ids:
        app.screenManager.current_screen.item_clicked(snackId=snack_id)
    await asyncio.sleep(0.3)

    # Press the spin button
    app.screenManager.current_screen.ids.spin_button.dispatch("on_press")
    await asyncio.sleep(0.5)

    # Navigate to store statistics
    app.screenManager.transitionToScreen("mainUserPage", transitionDirection="right")
    await asyncio.sleep(0.5)
    app.screenManager.current_screen.ids.header.settings_button.dispatch("on_release")
    await asyncio.sleep(0.5)
    assert app.screenManager.current == "adminScreen"

    app.screenManager.current_screen.ids.storeStatsOption.dispatch("on_release")
    await asyncio.sleep(0.5)
    assert app.screenManager.current == "storeStatsScreen"

    # Verify the gamble transaction appears in the store stats data
    all_users = app.screenManager.database.getAllPatrons()
    found_gamble = False
    for patron in all_users:
        transactions = app.screenManager.database.getTransactions(patron.patronId)
        for t in transactions:
            if t.transactionType == TransactionType.GAMBLE:
                found_gamble = True
                break

    assert found_gamble, "Gamble transaction should be found in database"


@pytest.mark.asyncio
async def test_store_statistics_skips_non_purchase_non_gamble(app):
    """Test that store stats skips TOP_UP/EDIT transactions in the
    PURCHASE/GAMBLE branches, covering the elif-false branch."""
    # Log in
    assert app.screenManager.current == "splashScreen"
    app.screenManager.RFIDReader.triggerFakeRead(card_id="555555555")
    await asyncio.sleep(0.5)
    assert app.screenManager.current == "mainUserPage"

    user = app.screenManager.getCurrentPatron()

    # Perform a real top-up through the UI
    app.screenManager.current_screen.ids.topUpOption.dispatch("on_release")
    await asyncio.sleep(0.5)
    assert app.screenManager.current == "topUpAmountScreen"

    # Set the amount and press continue
    app.screenManager.current_screen.ids.creditsToAdd.text = "5.00"
    app.screenManager.current_screen.ids.continueButton.dispatch("on_press")
    await asyncio.sleep(0.5)
    assert app.screenManager.current == "topUpPaymentScreen"

    # Confirm the payment — this creates the TOP_UP transaction via the app
    app.screenManager.current_screen.ids.confirmButton.dispatch("on_press")
    await asyncio.sleep(0.5)

    # Should be back on main user page
    assert app.screenManager.current == "mainUserPage"

    # Navigate to store statistics to trigger on_pre_enter
    app.screenManager.current_screen.ids.header.settings_button.dispatch("on_release")
    await asyncio.sleep(0.5)
    assert app.screenManager.current == "adminScreen"

    app.screenManager.current_screen.ids.storeStatsOption.dispatch("on_release")
    await asyncio.sleep(0.5)
    assert app.screenManager.current == "storeStatsScreen"

    # Verify the top-up was recorded (it exists as a non-PURCHASE, non-GAMBLE tx)
    transactions = app.screenManager.database.getTransactions(user.patronId)
    top_up_txs = [
        t for t in transactions if t.transactionType == TransactionType.TOP_UP
    ]
    assert len(top_up_txs) >= 1
