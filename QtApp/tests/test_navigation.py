"""
Navigation tests — verify screen transitions between all 4 screens.

Mirrors the Kivy navigation test patterns.
"""

# pylint: disable=duplicate-code

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QPushButton


class TestNavigation:
    """Smoke tests for screen transitions."""

    def test_splash_to_login(self, app_with_nothing, qtbot):
        """Clicking the splash screen navigates to the login screen."""
        splash = app_with_nothing.stacked_widget.currentWidget()
        assert splash.objectName() == "splashScreen"

        qtbot.mouseClick(splash, Qt.MouseButton.LeftButton)

        qtbot.waitUntil(
            lambda: app_with_nothing.stacked_widget.currentWidget().objectName()
            == "loginScreen",
            timeout=2000,
        )

    def test_login_to_create_user(self, app_with_nothing, qtbot):
        """Clicking 'Create new user' on login navigates to createUserScreen."""
        app_with_nothing.state_manager.transition_to_screen("loginScreen")
        qtbot.waitUntil(
            lambda: app_with_nothing.stacked_widget.currentWidget().objectName()
            == "loginScreen",
            timeout=2000,
        )

        login = app_with_nothing.stacked_widget.currentWidget()
        create_btn = login.findChild(QPushButton, "createNewUserButton")
        assert create_btn is not None, "createNewUserButton not found"
        qtbot.mouseClick(create_btn, Qt.MouseButton.LeftButton)

        qtbot.waitUntil(
            lambda: app_with_nothing.stacked_widget.currentWidget().objectName()
            == "createUserScreen",
            timeout=2000,
        )

    def test_create_user_to_login(self, app_on_create_user, qtbot):
        """Clicking Cancel on create user navigates back to login."""
        create_screen = app_on_create_user.stacked_widget.currentWidget()
        cancel_btn = create_screen.findChild(QPushButton, "cancelButton")
        assert cancel_btn is not None, "cancelButton not found"
        qtbot.mouseClick(cancel_btn, Qt.MouseButton.LeftButton)

        qtbot.waitUntil(
            lambda: app_on_create_user.stacked_widget.currentWidget().objectName()
            == "loginScreen",
            timeout=2000,
        )

    def test_login_back_to_splash(self, app_with_users_on_login, qtbot):
        """Clicking the back button on login returns to splash."""
        login = app_with_users_on_login.stacked_widget.currentWidget()
        back_btn = login.findChild(QPushButton, "backButton")
        assert back_btn is not None, "backButton not found"
        qtbot.mouseClick(back_btn, Qt.MouseButton.LeftButton)

        qtbot.waitUntil(
            lambda: app_with_users_on_login.stacked_widget.currentWidget().objectName()
            == "splashScreen",
            timeout=2000,
        )

    def test_main_user_logout(self, app_with_users, qtbot):
        """Logging out from main user screen returns to login."""
        patrons = app_with_users.state_manager.database.getAllPatrons()
        user2 = [p for p in patrons if p.firstName == "User2FirstName"][0]
        app_with_users.state_manager.login(user2.patronId)

        app_with_users.state_manager.transition_to_screen("mainUserPage")
        qtbot.waitUntil(
            lambda: app_with_users.stacked_widget.currentWidget().objectName()
            == "mainUserPage",
            timeout=2000,
        )

        main_screen = app_with_users.stacked_widget.currentWidget()
        logout_btn = main_screen.findChild(QPushButton, "logoutButton")
        assert logout_btn is not None, "logoutButton not found"
        qtbot.mouseClick(logout_btn, Qt.MouseButton.LeftButton)

        qtbot.waitUntil(
            lambda: app_with_users.stacked_widget.currentWidget().objectName()
            == "loginScreen",
            timeout=2000,
        )
        assert app_with_users.state_manager.get_current_patron() is None
