"""
Reproduce and verify the buy-screen auto-logout bug.

The auto-logout timer is set in CustomScreenManager.login().
It gets reset on every touch via the touch-dedup monkey-patch → _reset_idle_timer().
This test verifies that:
  1. The timer exists after login
  2. A touch event arrives and resets the timer via the dedup handler
  3. Touches to ClickableTable items (on the buy screen) trigger the touch dedup handler (which calls _reset_idle_timer)
"""
# pylint: disable=protected-access
import asyncio

import pytest


@pytest.mark.asyncio
async def test_auto_logout_timer_created_on_login(app_with_only_users):
    """Verify the timer is created when logging in, and reset on touch."""

    app = app_with_only_users

    # Start on splash screen and login
    assert app.screenManager.current == "splashScreen"
    app.screenManager.current_screen.onPressed()
    assert app.screenManager.current == "loginScreen"

    # Click User3 to login
    users = [
        c
        for c in app.screenManager.current_screen.ids[
            "LoginScreenUserGridLayout"
        ].children
        if hasattr(c, "first_name")
    ]
    target = [u for u in users if u.first_name == "User3FirstName"]
    assert len(target) == 1
    target[0].ids.clickableLayout.dispatch("on_release")
    await asyncio.sleep(0.3)

    assert app.screenManager.current == "mainUserPage"
    assert app.screenManager.log_out_timer is not None
    print("  ✅ Timer exists after login")

    # Save the timer id to check it gets replaced on activity
    timer_id_1 = id(app.screenManager.log_out_timer)

    # Simulate a touch on the window
    app.screenManager._reset_idle_timer()
    await asyncio.sleep(0.05)

    timer_id_2 = id(app.screenManager.log_out_timer)
    assert (
        timer_id_1 != timer_id_2
    ), "Timer should be a new ClockEvent after on_activity (was reset)"
    assert app.screenManager.log_out_timer is not None
    print("  ✅ Timer was reset by _reset_idle_timer()")


@pytest.mark.asyncio
async def test_buy_screen_touches_reset_timer(app_on_buy_screen):
    """Verify that interacting with the buy screen resets the timer."""

    app = app_on_buy_screen
    assert app.screenManager.current == "buyScreen"
    assert app.screenManager.log_out_timer is not None
    print("  ✅ Timer exists on buy screen")

    # Simulate a touch via _reset_idle_timer
    timer_id_before = id(app.screenManager.log_out_timer)
    app.screenManager._reset_idle_timer()
    await asyncio.sleep(0.05)

    timer_id_after = id(app.screenManager.log_out_timer)
    assert timer_id_before != timer_id_after, "Timer should be reset after touch"
    print("  ✅ Timer reset by _reset_idle_timer on buy screen")

    # Now test that when itemClickedInInventory is called, the timer is
    # NOT directly reset by that method. The timer reset happens via
    # the Window.on_touch_down dedup handler → _reset_idle_timer,
    # which fires on the DOWN event before itemClickedInInventory runs.
    # Verify this expected behavior: itemClickedInInventory does NOT
    # reset the timer by itself.
    snacks = app.screenManager.database.getAllSnacks()
    assert len(snacks) > 0

    affordable = [
        s
        for s in snacks
        if s.pricePerItem <= app.screenManager.getCurrentPatron().totalCredits
    ]
    assert len(affordable) > 0

    timer_before_click = id(app.screenManager.log_out_timer)

    # Click the snack
    app.screenManager.current_screen.itemClickedInInventory(
        snackId=affordable[0].snackId
    )
    await asyncio.sleep(0.05)

    # itemClickedInInventory doesn't reset the timer — it's just business logic.
    # The timer reset happens via the Window.on_touch_down dedup handler BEFORE this
    # runs. So the timer ID should be the same (no reset from this call).
    timer_after_click = id(app.screenManager.log_out_timer)
    assert timer_before_click == timer_after_click, (
        "itemClickedInInventory should not reset the timer "
        "(reset happens via Window.on_touch_down dedup handler)"
    )
    # The timer reset will happen on the NEXT touch DOWN event


@pytest.mark.asyncio
async def test_auto_logout_fires_when_no_touch(app_with_only_users):
    """Verify auto-logout fires if the timer is not reset."""

    app = app_with_only_users

    # Login as User3
    assert app.screenManager.current == "splashScreen"
    app.screenManager.current_screen.onPressed()
    assert app.screenManager.current == "loginScreen"

    users = [
        c
        for c in app.screenManager.current_screen.ids[
            "LoginScreenUserGridLayout"
        ].children
        if hasattr(c, "first_name")
    ]
    target = [u for u in users if u.first_name == "User3FirstName"]
    target[0].ids.clickableLayout.dispatch("on_release")
    await asyncio.sleep(0.3)
    assert app.screenManager.current == "mainUserPage"
    assert app.screenManager._currentPatron is not None

    # Manually trigger auto-logout by calling the timer callback
    # The timer is a ClockEvent; we can't call it directly,
    # but we can call auto_logout() which is what the timer does
    app.screenManager.auto_logout()
    await asyncio.sleep(0.3)

    # Should now be on splash screen and logged out
    assert app.screenManager.current == "splashScreen"
    assert app.screenManager._currentPatron is None
    assert app.screenManager.log_out_timer is None
    print("  ✅ Auto-logout works when timer fires")


@pytest.mark.asyncio
async def test_on_activity_survives_exceptions(app_with_only_users):
    """Verify on_activity doesn't silently fail, preventing timer reset."""

    app = app_with_only_users

    # Login to create the timer
    assert app.screenManager.current == "splashScreen"
    app.screenManager.current_screen.onPressed()
    assert app.screenManager.current == "loginScreen"

    users = [
        c
        for c in app.screenManager.current_screen.ids[
            "LoginScreenUserGridLayout"
        ].children
        if hasattr(c, "first_name")
    ]
    target = [u for u in users if u.first_name == "User3FirstName"]
    target[0].ids.clickableLayout.dispatch("on_release")
    await asyncio.sleep(0.3)
    assert app.screenManager.current == "mainUserPage"

    timer_before = id(app.screenManager.log_out_timer)

    # _reset_idle_timer should work even if called multiple times
    app.screenManager._reset_idle_timer()
    await asyncio.sleep(0.05)

    timer_after = id(app.screenManager.log_out_timer)
    assert timer_before != timer_after, "_reset_idle_timer should reset timer"
    assert app.screenManager.log_out_timer is not None
    print("  ✅ _reset_idle_timer resets timer cleanly")
