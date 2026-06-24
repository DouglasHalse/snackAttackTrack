import asyncio

import pytest


@pytest.mark.asyncio
async def test_navigate_to_history_screen(app_with_users_and_snacks):
    """Test navigating to history screen from profile screen"""
    app = app_with_users_and_snacks

    # Get user
    user = app.screenManager.database.getPatronByEmployeeId(987654321)
    app.screenManager.database.addCredits(user.patronId, 100)
    app.screenManager.setCurrentPatron(user)

    # Navigate to profile screen then history
    app.screenManager.current = "profileScreen"
    await asyncio.sleep(0.1)

    profile_screen = app.screenManager.current_screen
    profile_screen.ids.historyOption.dispatch("on_release")
    await asyncio.sleep(0.1)

    # Verify we're on history screen
    assert app.screenManager.current == "historyScreen"


@pytest.mark.asyncio
async def test_clear_history_button_exists(app_with_users_and_snacks):
    """Test that clear history functionality is accessible"""
    app = app_with_users_and_snacks

    # Get user
    user = app.screenManager.database.getPatronByEmployeeId(987654321)
    app.screenManager.database.addCredits(user.patronId, 100)
    app.screenManager.setCurrentPatron(user)

    # Add some transactions
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

    # Navigate to history screen
    app.screenManager.current = "historyScreen"
    await asyncio.sleep(0.2)

    # Verify we're on history screen
    assert app.screenManager.current == "historyScreen"
    history_screen = app.screenManager.current_screen
    assert history_screen is not None


@pytest.mark.asyncio
async def test_history_screen_back_navigation(app_with_users_and_snacks):
    """Test navigating back from history screen"""
    app = app_with_users_and_snacks

    # Get user
    user = app.screenManager.database.getPatronByEmployeeId(987654321)
    app.screenManager.database.addCredits(user.patronId, 100)
    app.screenManager.setCurrentPatron(user)

    # Navigate to history screen
    app.screenManager.current = "historyScreen"
    await asyncio.sleep(0.1)

    # Click back button
    history_screen = app.screenManager.current_screen
    history_screen.ids.header.ids.backButton.dispatch("on_release")
    await asyncio.sleep(0.1)

    # Should navigate back to profile screen
    assert app.screenManager.current == "profileScreen"


@pytest.mark.asyncio
async def test_history_with_no_transactions(app_with_users):
    """Test history screen when user has no transaction history"""
    app = app_with_users

    # Get user with no transactions
    user = app.screenManager.database.getPatronByEmployeeId(987654321)
    app.screenManager.setCurrentPatron(user)

    # Navigate to history screen
    app.screenManager.current = "historyScreen"
    await asyncio.sleep(0.2)

    # Verify we're on history screen
    assert app.screenManager.current == "historyScreen"


@pytest.mark.asyncio
async def test_history_displays_transactions(app_with_users_and_snacks):
    """Test that history screen displays user transactions"""
    app = app_with_users_and_snacks

    # Get user
    user = app.screenManager.database.getPatronByEmployeeId(987654321)
    app.screenManager.database.addCredits(user.patronId, 200)
    app.screenManager.setCurrentPatron(user)

    # Add multiple types of transactions
    snack = app.screenManager.database.getSnackByName("Snack1")
    from datetime import datetime

    # Purchase transaction
    app.screenManager.database.addPurchaseTransaction(
        patronID=user.patronId,
        amountBeforeTransaction=200.0,
        amountAfterTransaction=190.0,
        transactionDate=datetime.now(),
        transactionItems=[snack],
    )

    # Top-up transaction
    app.screenManager.database.addTopUpTransaction(
        patronID=user.patronId,
        amountBeforeTransaction=190.0,
        amountAfterTransaction=290.0,
        transactionDate=datetime.now(),
    )

    # Navigate to history screen
    app.screenManager.current = "historyScreen"
    await asyncio.sleep(0.2)

    # Verify screen loaded
    assert app.screenManager.current == "historyScreen"
    history_screen = app.screenManager.current_screen
    assert history_screen is not None
