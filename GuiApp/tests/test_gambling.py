import asyncio

import pytest


@pytest.mark.asyncio
async def test_navigate_to_wheel_of_snacks(app_with_users_and_snacks):
    """Test navigating to wheel of snacks (gambling) screen"""
    app = app_with_users_and_snacks

    # Get user and set as current patron
    user = app.screenManager.database.getPatronByEmployeeId(987654321)
    app.screenManager.database.addCredits(user.patronId, 100)
    app.screenManager.setCurrentPatron(user)

    # Navigate to main user screen
    app.screenManager.current = "mainUserPage"
    await asyncio.sleep(0.1)

    # Click gamble option button
    main_screen = app.screenManager.current_screen
    main_screen.ids.gambleOption.dispatch("on_release")
    await asyncio.sleep(0.1)

    # Verify we're on the wheel of snacks screen
    assert app.screenManager.current == "wheelOfSnacksScreen"


@pytest.mark.asyncio
async def test_gambling_with_insufficient_credits(app_with_users_and_snacks):
    """Test that gambling works even with low credits"""
    app = app_with_users_and_snacks

    # Get user with low credits
    user = app.screenManager.database.getPatronByEmployeeId(987654321)
    app.screenManager.database.addCredits(user.patronId, 5)  # Low credits
    app.screenManager.setCurrentPatron(user)

    # Navigate to main user screen
    app.screenManager.current = "mainUserPage"
    await asyncio.sleep(0.1)

    # Click gamble option button
    main_screen = app.screenManager.current_screen
    main_screen.ids.gambleOption.dispatch("on_release")
    await asyncio.sleep(0.2)

    # Should navigate to wheel screen
    assert app.screenManager.current == "wheelOfSnacksScreen"


@pytest.mark.asyncio
async def test_gambling_with_no_snacks(app_with_users):
    """Test that gambling is blocked when there are no snacks"""
    app = app_with_users

    # Get user
    user = app.screenManager.database.getPatronByEmployeeId(987654321)
    app.screenManager.database.addCredits(user.patronId, 100)
    app.screenManager.setCurrentPatron(user)

    # Navigate to main user screen
    app.screenManager.current = "mainUserPage"
    await asyncio.sleep(0.1)

    # Try to click gamble option (no snacks exist)
    main_screen = app.screenManager.current_screen
    main_screen.ids.gambleOption.dispatch("on_release")
    await asyncio.sleep(0.2)

    # Should stay on main user screen because no snacks available
    assert app.screenManager.current == "mainUserPage"


@pytest.mark.asyncio
async def test_gambling_with_one_snack(app_with_users):
    """Test that gambling is blocked when there is only one snack"""
    app = app_with_users

    # Add only one snack
    app.screenManager.database.addSnack("OnlySnack", 1, "test.png", 10)

    # Get user
    user = app.screenManager.database.getPatronByEmployeeId(987654321)
    app.screenManager.database.addCredits(user.patronId, 100)
    app.screenManager.setCurrentPatron(user)

    # Navigate to main user screen
    app.screenManager.current = "mainUserPage"
    await asyncio.sleep(0.1)

    # Try to click gamble option (only one snack)
    main_screen = app.screenManager.current_screen
    main_screen.ids.gambleOption.dispatch("on_release")
    await asyncio.sleep(0.2)

    # Should stay on main user screen (need at least 2 snacks)
    assert app.screenManager.current == "mainUserPage"


@pytest.mark.asyncio
async def test_gambling_back_navigation(app_with_users_and_snacks):
    """Test navigating back from gambling screen"""
    app = app_with_users_and_snacks

    # Get user
    user = app.screenManager.database.getPatronByEmployeeId(987654321)
    app.screenManager.database.addCredits(user.patronId, 100)
    app.screenManager.setCurrentPatron(user)

    # Navigate to gambling screen
    app.screenManager.current = "mainUserPage"
    await asyncio.sleep(0.1)
    app.screenManager.current_screen.ids.gambleOption.dispatch("on_release")
    await asyncio.sleep(0.1)

    # Verify we're on wheel screen
    assert app.screenManager.current == "wheelOfSnacksScreen"

    # Click back button
    wheel_screen = app.screenManager.current_screen
    wheel_screen.ids.header.ids.backButton.dispatch("on_release")
    await asyncio.sleep(0.1)

    # Should navigate back to main user screen
    assert app.screenManager.current == "mainUserPage"


@pytest.mark.asyncio
async def test_gambling_screen_refresh(app_with_users_and_snacks):
    """Test that gambling screen refreshes correctly"""
    app = app_with_users_and_snacks

    # Get user
    user = app.screenManager.database.getPatronByEmployeeId(987654321)
    app.screenManager.database.addCredits(user.patronId, 100)
    app.screenManager.setCurrentPatron(user)

    # Navigate to gambling screen
    app.screenManager.current = "mainUserPage"
    await asyncio.sleep(0.1)
    app.screenManager.current_screen.ids.gambleOption.dispatch("on_release")
    await asyncio.sleep(0.1)

    # Navigate away and back
    app.screenManager.current = "mainUserPage"
    await asyncio.sleep(0.1)

    main_screen = app.screenManager.current_screen
    main_screen.ids.gambleOption.dispatch("on_release")
    await asyncio.sleep(0.1)

    # Should still be on wheel screen
    assert app.screenManager.current == "wheelOfSnacksScreen"


@pytest.mark.asyncio
async def test_gambling_screen_loads_snacks(app_with_users_and_snacks):
    """Test that gambling screen loads available snacks"""
    app = app_with_users_and_snacks

    # Get user
    user = app.screenManager.database.getPatronByEmployeeId(987654321)
    app.screenManager.database.addCredits(user.patronId, 100)
    app.screenManager.setCurrentPatron(user)

    # Navigate to gambling screen
    app.screenManager.current = "mainUserPage"
    await asyncio.sleep(0.1)
    app.screenManager.current_screen.ids.gambleOption.dispatch("on_release")
    await asyncio.sleep(0.2)

    # Verify screen loaded
    assert app.screenManager.current == "wheelOfSnacksScreen"

    # Verify screen loaded properly
    wheel_screen = app.screenManager.current_screen
    assert wheel_screen is not None


@pytest.mark.asyncio
async def test_gambling_with_multiple_users(app_with_users_and_snacks):
    """Test gambling with multiple different users"""
    app = app_with_users_and_snacks

    # First user
    user1 = app.screenManager.database.getPatronByEmployeeId(987654321)
    app.screenManager.database.addCredits(user1.patronId, 100)
    app.screenManager.setCurrentPatron(user1)

    # Navigate to gambling
    app.screenManager.current = "mainUserPage"
    await asyncio.sleep(0.1)
    app.screenManager.current_screen.ids.gambleOption.dispatch("on_release")
    await asyncio.sleep(0.1)
    assert app.screenManager.current == "wheelOfSnacksScreen"

    # Go back
    app.screenManager.current = "mainUserPage"
    await asyncio.sleep(0.1)

    # Switch to second user
    user2 = app.screenManager.database.getPatronByEmployeeId(123456789)
    app.screenManager.database.addCredits(user2.patronId, 100)
    app.screenManager.setCurrentPatron(user2)

    # Navigate to gambling as second user
    app.screenManager.current_screen.ids.gambleOption.dispatch("on_release")
    await asyncio.sleep(0.1)
    assert app.screenManager.current == "wheelOfSnacksScreen"
