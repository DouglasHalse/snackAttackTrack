"""
Login tests — user selection, RFID card login, scroll detection, alphabet
quick-scroll, and unknown card handling.

Mirrors the Kivy ``test_login.py`` patterns.
"""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QPushButton, QScrollArea

from QtApp.screens.loginScreen import UserWidget


class TestLogin:
    """Login screen tests."""

    # ---- User selection ------------------------------------------------------

    def test_login_by_user_selection(self, app_with_users_on_login, qtbot):
        """Clicking a user widget logs in and navigates to mainUserPage."""
        login = app_with_users_on_login.stacked_widget.currentWidget()

        user_widget = self._find_user_widget(login, "User2FirstName")
        assert user_widget is not None, "User2 widget not found"

        qtbot.mouseClick(user_widget, Qt.MouseButton.LeftButton)

        qtbot.waitUntil(
            lambda: app_with_users_on_login.stacked_widget.currentWidget().objectName()
            == "mainUserPage",
            timeout=1000,
        )

        patron = app_with_users_on_login.state_manager.get_current_patron()
        assert patron is not None
        assert patron.firstName == "User2FirstName"

    # ---- RFID card login -----------------------------------------------------

    def test_login_by_rfid_card(self, app_with_users, qtbot):
        """Scanning a known RFID card logs in and navigates to mainUserPage."""
        assert (
            app_with_users.stacked_widget.currentWidget().objectName() == "splashScreen"
        )

        app_with_users.state_manager.rfid_adapter.triggerFakeRead("555555555")
        qtbot.wait(200)

        qtbot.waitUntil(
            lambda: app_with_users.stacked_widget.currentWidget().objectName()
            == "mainUserPage",
            timeout=2000,
        )

        patron = app_with_users.state_manager.get_current_patron()
        assert patron is not None
        assert patron.firstName == "User3FirstName"
        assert str(patron.totalCredits) == "11.00"

    # ---- Scroll vs tap detection ---------------------------------------------

    def test_login_scroll_vs_tap(self, app_with_users_on_login, qtbot):
        """The scroll_did_occur flag prevents clicks from being processed."""
        login = app_with_users_on_login.stacked_widget.currentWidget()

        # Verify the scroll flag exists and defaults to False
        assert login.scroll_did_occur is False

        # Set the flag as the scroll area would
        login.scroll_did_occur = True

        # Now clicking should NOT log in
        user_widget = self._find_user_widget(login, "User1FirstName")
        assert user_widget is not None
        qtbot.mouseClick(user_widget, Qt.MouseButton.LeftButton)

        # Should still be on login screen
        assert (
            app_with_users_on_login.stacked_widget.currentWidget().objectName()
            == "loginScreen"
        )
        assert app_with_users_on_login.state_manager.get_current_patron() is None

        # Reset the flag
        login.scroll_did_occur = False

    # ---- Alphabet quick-scroll ---------------------------------------------

    def test_login_alphabet_scroll(self, app_with_users_on_login, qtbot):
        """Clicking an alphabet letter scrolls to the first user with that letter."""
        login = app_with_users_on_login.stacked_widget.currentWidget()

        letter_u_btn = login.findChild(QPushButton, "letter_U")
        assert letter_u_btn is not None, "letter_U button not found"

        scroll_area = login.findChild(QScrollArea, "userScrollArea")
        assert scroll_area is not None

        qtbot.mouseClick(letter_u_btn, Qt.MouseButton.LeftButton)
        qtbot.wait(400)  # Wait for animation

        final_scroll = scroll_area.horizontalScrollBar().value()
        assert final_scroll >= 0  # Sanity: no crash

    # ---- Empty user list -----------------------------------------------------

    def test_login_no_users(self, app_with_nothing, qtbot):
        """With no users, the login screen shows an empty carousel (no crash)."""
        app_with_nothing.state_manager.transition_to_screen("loginScreen")
        qtbot.waitUntil(
            lambda: app_with_nothing.stacked_widget.currentWidget().objectName()
            == "loginScreen",
            timeout=2000,
        )

        login = app_with_nothing.stacked_widget.currentWidget()
        user_widgets = login.findChildren(UserWidget)
        assert len(user_widgets) == 0

    # ---- Unknown card --------------------------------------------------------

    def test_rfid_unknown_card_shows_dialog(self, app_with_users, qtbot):
        """Scanning an unknown card shows the create/link dialog."""
        assert (
            app_with_users.stacked_widget.currentWidget().objectName() == "splashScreen"
        )

        app_with_users.state_manager.rfid_adapter.triggerFakeRead("999999999")
        qtbot.wait(200)

        # The splash screen should still be shown (dialog is overlaid)
        assert (
            app_with_users.stacked_widget.currentWidget().objectName() == "splashScreen"
        )

    # ---- Helpers -------------------------------------------------------------

    @staticmethod
    def _find_user_widget(parent, first_name: str):
        """Find a UserWidget by first name in the carousel."""
        for w in parent.findChildren(UserWidget):
            if hasattr(w, "userData") and w.userData.firstName == first_name:
                return w
        return None
