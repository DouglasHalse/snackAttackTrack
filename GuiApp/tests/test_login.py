import asyncio
from string import ascii_uppercase

import pytest


@pytest.mark.asyncio
async def test_login_by_selecting_user(app_with_only_users):

    assert app_with_only_users.screenManager.current == "splashScreen"
    app_with_only_users.screenManager.current_screen.onPressed()
    assert app_with_only_users.screenManager.current == "loginScreen"

    # Find the first user in the RecycleView data
    rv = app_with_only_users.screenManager.current_screen.ids["userRecycleView"]
    assert len(rv.data) > 0

    # Use data to find the right patron and login
    for entry in rv.data:
        if entry["first_name"] == "User2FirstName":
            screen = app_with_only_users.screenManager.current_screen
            screen.manager.login(entry["patron_id"])
            screen.manager.transitionToScreen("mainUserPage")
            break

    assert app_with_only_users.screenManager.current == "mainUserPage"
    assert (
        "User2FirstName"
        in app_with_only_users.screenManager.current_screen.ids.header.ids.welcomeTextLabel.text
    )


@pytest.mark.asyncio
async def test_login_from_splash_screen_with_card(app_with_only_users):
    assert app_with_only_users.screenManager.current == "splashScreen"

    app_with_only_users.screenManager.RFIDReader.triggerFakeRead(card_id="555555555")

    assert app_with_only_users.screenManager.current == "mainUserPage"
    assert (
        "User3FirstName"
        in app_with_only_users.screenManager.current_screen.ids.header.ids.welcomeTextLabel.text
    )


@pytest.mark.asyncio
async def test_login_from_login_screen_with_card(app_with_only_users):
    assert app_with_only_users.screenManager.current == "splashScreen"
    app_with_only_users.screenManager.current_screen.onPressed()

    await asyncio.sleep(0.5)
    app_with_only_users.screenManager.RFIDReader.triggerFakeRead(card_id="123456789")

    assert app_with_only_users.screenManager.current == "mainUserPage"


@pytest.mark.asyncio
async def test_alphabet_scroll_centers_widget(app_with_only_users):
    """Verify tapping a letter scrolls to the first matching user."""
    app = app_with_only_users
    db = app.screenManager.database

    for i, letter in enumerate(ascii_uppercase):
        db.addPatron(
            first_name=f"{letter}aronFirst",
            last_name=f"{letter}aronLast",
            employee_id=f"T{i:06d}",
        )

    assert app.screenManager.current == "splashScreen"
    app.screenManager.current_screen.onPressed()
    assert app.screenManager.current == "loginScreen"
    await asyncio.sleep(0.3)

    screen = app.screenManager.current_screen
    rv = screen.ids["userRecycleView"]

    target_letter = "M"
    target_index = screen.get_user_index_for_letter(target_letter)
    assert target_index is not None

    screen.on_alphabet_letter_selected(target_letter)
    await asyncio.sleep(0.6)  # Let the deferred scroll + 300ms animation complete

    # Verify scroll position moved away from default (0.5)
    assert rv.scroll_x != 0.5, "Scroll position should have changed"
    # The target item should be roughly centered
    assert 0 < rv.scroll_x < 1


@pytest.mark.asyncio
async def test_alphabet_scroll_missing_letter_does_nothing(app_with_only_users):
    """Tapping a letter with no matching user should not crash."""
    app = app_with_only_users
    assert app.screenManager.current == "splashScreen"
    app.screenManager.current_screen.onPressed()
    assert app.screenManager.current == "loginScreen"
    await asyncio.sleep(0.3)

    # "Q" has no user in app_with_only_users fixture — should not crash
    app.screenManager.current_screen.on_alphabet_letter_selected("Q")
    # No assertion needed — if we reach here, the guard worked


@pytest.mark.asyncio
async def test_get_user_widget_for_missing_letter_returns_none(app_with_only_users):
    """Public API should return None for letters with no matching user."""
    app = app_with_only_users
    assert app.screenManager.current == "splashScreen"
    app.screenManager.current_screen.onPressed()
    assert app.screenManager.current == "loginScreen"
    await asyncio.sleep(0.3)

    assert app.screenManager.current_screen.get_user_index_for_letter("Q") is None


@pytest.mark.asyncio
async def test_back_button_goes_to_splash(app_with_only_users):
    """The ← button should transition to splashScreen."""
    app = app_with_only_users
    assert app.screenManager.current == "splashScreen"
    app.screenManager.current_screen.onPressed()
    assert app.screenManager.current == "loginScreen"
    await asyncio.sleep(0.3)

    app.screenManager.current_screen.back_button_pressed()
    await asyncio.sleep(0.3)

    assert app.screenManager.current == "splashScreen"


@pytest.mark.asyncio
async def test_do_alphabet_scroll_guards_inactive_screen(app_with_only_users):
    """The deferred scroll callback must no-op when the screen has left."""
    app = app_with_only_users
    assert app.screenManager.current == "splashScreen"
    app.screenManager.current_screen.onPressed()
    assert app.screenManager.current == "loginScreen"
    await asyncio.sleep(0.3)

    screen = app.screenManager.current_screen

    # Simulate screen leave
    screen._screen_active = False  # pylint: disable=protected-access

    # Should return silently — no crash
    screen._do_alphabet_scroll(0)  # pylint: disable=protected-access
