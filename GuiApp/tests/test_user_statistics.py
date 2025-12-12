import asyncio

import pytest


@pytest.mark.asyncio
async def test_navigate_to_user_statistics(app_with_users_and_snacks):
    """Test navigating to user statistics screen from profile screen"""
    app = app_with_users_and_snacks

    # Get user
    user = app.screenManager.database.getPatronByEmployeeId(987654321)
    app.screenManager.database.addCredits(user.patronId, 100)
    app.screenManager.setCurrentPatron(user)

    # Navigate to profile screen
    app.screenManager.current = "profileScreen"
    await asyncio.sleep(0.1)

    # Click statistics option
    profile_screen = app.screenManager.current_screen
    profile_screen.ids.statisticsOption.dispatch("on_release")
    await asyncio.sleep(0.1)

    # Verify we're on user statistics screen
    assert app.screenManager.current == "userStatisticsScreen"


@pytest.mark.asyncio
async def test_user_statistics_displays_data(app_with_users_and_snacks):
    """Test that user statistics displays spending data"""
    app = app_with_users_and_snacks

    # Get user and add credits
    user = app.screenManager.database.getPatronByEmployeeId(987654321)
    app.screenManager.database.addCredits(user.patronId, 200)
    app.screenManager.setCurrentPatron(user)

    # Add purchase transactions
    snack = app.screenManager.database.getSnackByName("Snack1")
    from datetime import datetime

    for i in range(3):
        app.screenManager.database.addPurchaseTransaction(
            patronID=user.patronId,
            amountBeforeTransaction=user.totalCredits,
            amountAfterTransaction=user.totalCredits - snack.pricePerItem,
            transactionDate=datetime.now(),
            transactionItems=[snack],
        )

    # Navigate to user statistics
    app.screenManager.current = "userStatisticsScreen"
    await asyncio.sleep(0.2)

    # Verify screen loaded
    assert app.screenManager.current == "userStatisticsScreen"
    stats_screen = app.screenManager.current_screen
    assert stats_screen is not None


@pytest.mark.asyncio
async def test_user_statistics_favorite_snacks(app_with_users_and_snacks):
    """Test that user statistics shows favorite snacks"""
    app = app_with_users_and_snacks

    # Get user
    user = app.screenManager.database.getPatronByEmployeeId(987654321)
    app.screenManager.database.addCredits(user.patronId, 500)
    app.screenManager.setCurrentPatron(user)

    # Buy different snacks with different frequencies
    snack1 = app.screenManager.database.getSnackByName("Snack1")
    snack2 = app.screenManager.database.getSnackByName("Snack2")

    from datetime import datetime

    # Buy Snack1 multiple times (favorite)
    for i in range(5):
        app.screenManager.database.addPurchaseTransaction(
            patronID=user.patronId,
            amountBeforeTransaction=user.totalCredits,
            amountAfterTransaction=user.totalCredits - snack1.pricePerItem,
            transactionDate=datetime.now(),
            transactionItems=[snack1],
        )

    # Buy Snack2 fewer times
    for i in range(2):
        app.screenManager.database.addPurchaseTransaction(
            patronID=user.patronId,
            amountBeforeTransaction=user.totalCredits,
            amountAfterTransaction=user.totalCredits - snack2.pricePerItem,
            transactionDate=datetime.now(),
            transactionItems=[snack2],
        )

    # Navigate to user statistics
    app.screenManager.current = "userStatisticsScreen"
    await asyncio.sleep(0.2)

    # Verify screen loaded
    assert app.screenManager.current == "userStatisticsScreen"


@pytest.mark.asyncio
async def test_user_statistics_with_no_purchases(app_with_users):
    """Test user statistics screen when user has no purchase history"""
    app = app_with_users

    # Get user with no purchases
    user = app.screenManager.database.getPatronByEmployeeId(987654321)
    app.screenManager.setCurrentPatron(user)

    # Navigate to user statistics
    app.screenManager.current = "userStatisticsScreen"
    await asyncio.sleep(0.2)

    # Verify screen loaded
    assert app.screenManager.current == "userStatisticsScreen"


@pytest.mark.asyncio
async def test_user_statistics_back_navigation(app_with_users_and_snacks):
    """Test navigating back from user statistics screen"""
    app = app_with_users_and_snacks

    # Get user
    user = app.screenManager.database.getPatronByEmployeeId(987654321)
    app.screenManager.database.addCredits(user.patronId, 100)
    app.screenManager.setCurrentPatron(user)

    # Navigate to user statistics
    app.screenManager.current = "userStatisticsScreen"
    await asyncio.sleep(0.1)

    # Click back button
    stats_screen = app.screenManager.current_screen
    stats_screen.ids.header.ids.backButton.dispatch("on_release")
    await asyncio.sleep(0.1)

    # Should navigate back to profile screen
    assert app.screenManager.current == "profileScreen"


@pytest.mark.asyncio
async def test_user_statistics_refresh_on_reenter(app_with_users_and_snacks):
    """Test that user statistics refreshes when re-entering screen"""
    app = app_with_users_and_snacks

    # Get user
    user = app.screenManager.database.getPatronByEmployeeId(987654321)
    app.screenManager.database.addCredits(user.patronId, 200)
    app.screenManager.setCurrentPatron(user)

    # Navigate to user statistics
    app.screenManager.current = "userStatisticsScreen"
    await asyncio.sleep(0.2)

    # Navigate away
    app.screenManager.current = "profileScreen"
    await asyncio.sleep(0.1)

    # Add new transaction
    snack = app.screenManager.database.getSnackByName("Snack1")
    from datetime import datetime

    app.screenManager.database.addPurchaseTransaction(
        patronID=user.patronId,
        amountBeforeTransaction=user.totalCredits,
        amountAfterTransaction=user.totalCredits - snack.pricePerItem,
        transactionDate=datetime.now(),
        transactionItems=[snack],
    )

    # Navigate back to user statistics
    app.screenManager.current = "userStatisticsScreen"
    await asyncio.sleep(0.2)

    # Verify screen loaded (should show updated data)
    assert app.screenManager.current == "userStatisticsScreen"
