import asyncio
from string import ascii_uppercase

import pytest


@pytest.mark.asyncio
async def test_login_by_selecting_user(app_with_only_users):

    assert app_with_only_users.screenManager.current == "splashScreen"
    app_with_only_users.screenManager.current_screen.onPressed()
    assert app_with_only_users.screenManager.current == "loginScreen"

    usersOnScreen = [
        c
        for c in app_with_only_users.screenManager.current_screen.ids[
            "LoginScreenUserGridLayout"
        ].children
        if hasattr(c, "first_name")
    ]
    assert len(usersOnScreen) > 0

    for userButton in usersOnScreen:
        if userButton.first_name == "User2FirstName":
            userButton.ids.clickableLayout.dispatch("on_release")
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
    """Verify tapping a letter scrolls the first matching user to center."""
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
    sv = screen.ids["scrollView"]
    grid = screen.ids["LoginScreenUserGridLayout"]

    target_letter = "M"
    target_widget = screen.get_user_widget_for_letter(target_letter)
    assert target_widget is not None

    content_w = max(0, grid.width - sv.width)
    assert content_w > 0, f"Content too narrow: grid={grid.width} sv={sv.width}"
    widget_center = target_widget.x + target_widget.width / 2
    expected = (widget_center - sv.width / 2) / content_w
    expected = max(0, min(expected, 1))

    screen.on_alphabet_letter_selected(target_letter)
    await asyncio.sleep(0.6)  # Let the deferred scroll + 300ms animation complete

    actual = sv.scroll_x
    assert abs(actual - expected) < 0.02, (
        f"Letter '{target_letter}' not centered: "
        f"expected={expected:.4f}, got {actual:.4f}"
    )


@pytest.mark.asyncio
async def test_alphabet_scroll_missing_letter_does_nothing(app_with_only_users):
    """Tapping a letter with no matching user should not crash."""
    app = app_with_only_users
    assert app.screenManager.current == "splashScreen"
    app.screenManager.current_screen.onPressed()
    assert app.screenManager.current == "loginScreen"
    await asyncio.sleep(0.3)

    screen = app.screenManager.current_screen
    initial = screen.ids["scrollView"].scroll_x

    # "Q" has no user in app_with_only_users fixture
    screen.on_alphabet_letter_selected("Q")
    await asyncio.sleep(0.5)

    assert screen.ids["scrollView"].scroll_x == initial


@pytest.mark.asyncio
async def test_get_user_widget_for_missing_letter_returns_none(app_with_only_users):
    """Public API should return None for letters with no matching user."""
    app = app_with_only_users
    assert app.screenManager.current == "splashScreen"
    app.screenManager.current_screen.onPressed()
    assert app.screenManager.current == "loginScreen"
    await asyncio.sleep(0.3)

    assert app.screenManager.current_screen.get_user_widget_for_letter("Q") is None


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
    widget = screen.get_user_widget_for_letter(
        "U"  # User1/2/3FirstName all start with U
    )
    assert widget is not None

    # Simulate screen leave
    screen._screen_active = False  # pylint: disable=protected-access

    # Should return silently — no crash
    screen._do_alphabet_scroll(widget)  # pylint: disable=protected-access
