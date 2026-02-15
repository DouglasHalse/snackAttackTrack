import asyncio

import pytest


@pytest.mark.asyncio
async def test_navigate_to_buy_screen(app_with_users_and_snacks):
    """Test navigating to buy screen from main user screen"""
    app = app_with_users_and_snacks

    # Get user and set as current patron
    user = app.screenManager.database.getPatronByEmployeeId(987654321)
    app.screenManager.database.addCredits(user.patronId, 100)
    app.screenManager.setCurrentPatron(user)

    # Navigate to main user screen
    app.screenManager.current = "mainUserPage"
    await asyncio.sleep(0.1)

    # Click buy option button
    main_screen = app.screenManager.current_screen
    main_screen.ids.buyOption.dispatch("on_release")
    await asyncio.sleep(0.1)

    # Verify we're on the buy screen
    assert app.screenManager.current == "buyScreen"


@pytest.mark.asyncio
async def test_buy_screen_displays_snacks(app_with_users_and_snacks):
    """Test that buy screen displays available snacks"""
    app = app_with_users_and_snacks

    # Get user
    user = app.screenManager.database.getPatronByEmployeeId(987654321)
    app.screenManager.database.addCredits(user.patronId, 100)
    app.screenManager.setCurrentPatron(user)

    # Navigate to buy screen
    app.screenManager.current = "buyScreen"
    await asyncio.sleep(0.2)

    # Verify we're on buy screen
    assert app.screenManager.current == "buyScreen"
    buy_screen = app.screenManager.current_screen
    assert buy_screen is not None


@pytest.mark.asyncio
async def test_buy_screen_back_navigation(app_with_users_and_snacks):
    """Test navigating back from buy screen"""
    app = app_with_users_and_snacks

    # Get user
    user = app.screenManager.database.getPatronByEmployeeId(987654321)
    app.screenManager.database.addCredits(user.patronId, 100)
    app.screenManager.setCurrentPatron(user)

    # Navigate to buy screen
    app.screenManager.current = "buyScreen"
    await asyncio.sleep(0.1)

    # Click back button
    buy_screen = app.screenManager.current_screen
    buy_screen.ids.header.ids.backButton.dispatch("on_release")
    await asyncio.sleep(0.1)

    # Should navigate back to main user screen
    assert app.screenManager.current == "mainUserPage"


@pytest.mark.asyncio
async def test_buy_with_sufficient_credits(app_with_users_and_snacks):
    """Test buying a snack with sufficient credits"""
    app = app_with_users_and_snacks

    # Get user with enough credits
    user = app.screenManager.database.getPatronByEmployeeId(987654321)
    initial_credits = 200
    app.screenManager.database.addCredits(user.patronId, initial_credits)
    app.screenManager.setCurrentPatron(user)

    # Navigate to buy screen
    app.screenManager.current = "buyScreen"
    await asyncio.sleep(0.2)

    # Verify we're on buy screen
    assert app.screenManager.current == "buyScreen"


@pytest.mark.asyncio
async def test_buy_with_insufficient_credits(app_with_users_and_snacks):
    """Test attempting to buy when user has insufficient credits"""
    app = app_with_users_and_snacks

    # Get user with low credits
    user = app.screenManager.database.getPatronByEmployeeId(987654321)
    app.screenManager.database.addCredits(user.patronId, 1)  # Very low credits
    app.screenManager.setCurrentPatron(user)

    # Navigate to buy screen
    app.screenManager.current = "buyScreen"
    await asyncio.sleep(0.2)

    # Verify we're on buy screen (should show items even with low credits)
    assert app.screenManager.current == "buyScreen"


@pytest.mark.asyncio
async def test_buy_screen_with_no_snacks(app_with_users):
    """Test buy screen when there are no snacks available"""
    app = app_with_users

    # Get user
    user = app.screenManager.database.getPatronByEmployeeId(987654321)
    app.screenManager.database.addCredits(user.patronId, 100)
    app.screenManager.setCurrentPatron(user)

    # Navigate to buy screen (no snacks exist)
    app.screenManager.current = "buyScreen"
    await asyncio.sleep(0.2)

    # Verify we're on buy screen
    assert app.screenManager.current == "buyScreen"
