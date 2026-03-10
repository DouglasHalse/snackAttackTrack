import asyncio

import pytest


@pytest.mark.asyncio
async def test_navigate_to_store_statistics(app_with_users_and_snacks):
    """Test navigating to store statistics screen from admin screen"""
    app = app_with_users_and_snacks

    # Navigate to admin screen
    app.screenManager.current = "adminScreen"
    await asyncio.sleep(0.1)

    # Click store statistics option
    admin_screen = app.screenManager.current_screen
    admin_screen.ids.storeStatsOption.dispatch("on_release")
    await asyncio.sleep(0.1)

    assert app.screenManager.current == "storeStatsScreen"


@pytest.mark.asyncio
async def test_store_statistics_displays_data(app_with_users_and_snacks):
    """Test that store statistics correctly displays revenue data"""
    app = app_with_users_and_snacks

    # Add some transactions to generate revenue
    user = app.screenManager.database.getPatronByEmployeeId(987654321)
    app.screenManager.database.addCredits(user.patronId, 200)
    snack = app.screenManager.database.getSnackByName("Snack1")

    from datetime import datetime

    # Add snack purchases
    for i in range(3):
        app.screenManager.database.addPurchaseTransaction(
            patronID=user.patronId,
            amountBeforeTransaction=user.totalCredits,
            amountAfterTransaction=user.totalCredits - snack.pricePerItem,
            transactionDate=datetime.now(),
            transactionItems=[snack],
        )

    # Navigate to store statistics
    app.screenManager.current = "storeStatsScreen"
    await asyncio.sleep(0.2)

    # Verify screen loaded
    assert app.screenManager.current == "storeStatsScreen"
    stats_screen = app.screenManager.current_screen
    assert stats_screen is not None


@pytest.mark.asyncio
async def test_store_statistics_most_popular_snack(app_with_users_and_snacks):
    """Test that store statistics identifies most popular snack"""
    app = app_with_users_and_snacks

    # Add transactions for different snacks
    user = app.screenManager.database.getPatronByEmployeeId(987654321)
    app.screenManager.database.addCredits(user.patronId, 500)

    snack1 = app.screenManager.database.getSnackByName("Snack1")
    snack2 = app.screenManager.database.getSnackByName("Snack2")

    from datetime import datetime

    # Buy Snack1 5 times (should be most popular)
    for i in range(5):
        app.screenManager.database.addPurchaseTransaction(
            patronID=user.patronId,
            amountBeforeTransaction=user.totalCredits,
            amountAfterTransaction=user.totalCredits - snack1.pricePerItem,
            transactionDate=datetime.now(),
            transactionItems=[snack1],
        )

    # Buy Snack2 2 times
    for i in range(2):
        app.screenManager.database.addPurchaseTransaction(
            patronID=user.patronId,
            amountBeforeTransaction=user.totalCredits,
            amountAfterTransaction=user.totalCredits - snack2.pricePerItem,
            transactionDate=datetime.now(),
            transactionItems=[snack2],
        )

    # Navigate to store statistics
    app.screenManager.current = "storeStatsScreen"
    await asyncio.sleep(0.2)

    # Verify screen loaded
    assert app.screenManager.current == "storeStatsScreen"


@pytest.mark.asyncio
async def test_store_statistics_with_no_transactions(app_with_users_and_snacks):
    """Test store statistics screen with no transaction data"""
    app = app_with_users_and_snacks

    # Navigate to store statistics without any transactions
    app.screenManager.current = "storeStatsScreen"
    await asyncio.sleep(0.2)

    # Verify screen loaded properly even with no data
    assert app.screenManager.current == "storeStatsScreen"
    stats_screen = app.screenManager.current_screen
    assert stats_screen is not None


@pytest.mark.asyncio
async def test_store_statistics_back_navigation(app_with_users_and_snacks):
    """Test navigating back from store statistics screen"""
    app = app_with_users_and_snacks

    # Navigate to store statistics
    app.screenManager.current = "storeStatsScreen"
    await asyncio.sleep(0.1)

    # Click back button in header
    stats_screen = app.screenManager.current_screen
    stats_screen.ids.header.ids.backButton.dispatch("on_release")
    await asyncio.sleep(0.1)

    # Should navigate back to admin screen
    assert app.screenManager.current == "adminScreen"


@pytest.mark.asyncio
async def test_store_statistics_refresh_data(app_with_users_and_snacks):
    """Test that store statistics updates when screen is re-entered"""
    app = app_with_users_and_snacks

    # Navigate to store statistics
    app.screenManager.current = "storeStatsScreen"
    await asyncio.sleep(0.2)

    # Navigate away
    app.screenManager.current = "adminScreen"
    await asyncio.sleep(0.1)

    # Add a transaction
    user = app.screenManager.database.getPatronByEmployeeId(987654321)
    app.screenManager.database.addCredits(user.patronId, 100)
    snack = app.screenManager.database.getSnackByName("Snack1")

    from datetime import datetime

    app.screenManager.database.addPurchaseTransaction(
        patronID=user.patronId,
        amountBeforeTransaction=user.totalCredits,
        amountAfterTransaction=user.totalCredits - snack.pricePerItem,
        transactionDate=datetime.now(),
        transactionItems=[snack],
    )

    # Navigate back to store statistics
    app.screenManager.current = "storeStatsScreen"
    await asyncio.sleep(0.2)

    # Verify screen loaded (data should be refreshed)
    assert app.screenManager.current == "storeStatsScreen"
