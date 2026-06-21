"""
Create User tests — validate registration form, RFID card scanning, and error
handling.

Mirrors the Kivy ``test_create_user.py`` patterns.
"""

# pylint: disable=unused-variable

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLineEdit, QPushButton


class TestCreateUser:
    """User registration validation tests."""

    def _get_inputs(self, screen):
        """Helper to get the three input fields."""
        first = screen.findChild(QLineEdit, "firstNameInput")
        last = screen.findChild(QLineEdit, "lastNameInput")
        card = screen.findChild(
            QLineEdit, "cardIdInput"
        )  # pylint: disable=unused-variable
        return first, last, card

    def _click_register(self, screen, qtbot):
        """Click the Register button and process events."""
        register_btn = screen.findChild(QPushButton, "registerButton")
        assert register_btn is not None, "registerButton not found"
        qtbot.mouseClick(register_btn, Qt.MouseButton.LeftButton)
        qtbot.wait(50)

    # ---- Success cases -------------------------------------------------------

    def test_create_user_success(self, app_on_create_user, qtbot):
        """Creating a valid user navigates to login and saves to database."""
        create_screen = app_on_create_user.stacked_widget.currentWidget()
        first, last, card = self._get_inputs(create_screen)

        qtbot.keyClicks(first, "Alice")
        qtbot.keyClicks(last, "Smith")

        self._click_register(create_screen, qtbot)

        qtbot.waitUntil(
            lambda: app_on_create_user.stacked_widget.currentWidget().objectName()
            == "loginScreen",
            timeout=2000,
        )

        patrons = app_on_create_user.state_manager.database.getAllPatrons()
        alice = [p for p in patrons if p.firstName == "Alice"]
        assert len(alice) == 1
        assert alice[0].lastName == "Smith"
        assert alice[0].employeeID == ""

    # ---- Validation: blank fields --------------------------------------------

    def test_create_user_blank_first_name(self, app_on_create_user, qtbot):
        """Empty first name shows an error and stays on createUserScreen."""
        create_screen = app_on_create_user.stacked_widget.currentWidget()
        first, last, card = self._get_inputs(create_screen)

        qtbot.keyClicks(last, "Smith")
        self._click_register(create_screen, qtbot)

        assert (
            app_on_create_user.stacked_widget.currentWidget().objectName()
            == "createUserScreen"
        )
        assert len(app_on_create_user.state_manager.database.getAllPatrons()) == 0

    def test_create_user_blank_last_name(self, app_on_create_user, qtbot):
        """Empty last name shows an error and stays on createUserScreen."""
        create_screen = app_on_create_user.stacked_widget.currentWidget()
        first, last, card = self._get_inputs(create_screen)

        qtbot.keyClicks(first, "Alice")
        self._click_register(create_screen, qtbot)

        assert (
            app_on_create_user.stacked_widget.currentWidget().objectName()
            == "createUserScreen"
        )
        assert len(app_on_create_user.state_manager.database.getAllPatrons()) == 0

    def test_create_user_blank_both_names(self, app_on_create_user, qtbot):
        """Both fields empty shows an error and stays on createUserScreen."""
        create_screen = app_on_create_user.stacked_widget.currentWidget()
        self._click_register(create_screen, qtbot)

        assert (
            app_on_create_user.stacked_widget.currentWidget().objectName()
            == "createUserScreen"
        )

    # ---- RFID / card --------------------------------------------------------

    def test_create_user_with_card(self, app_on_create_user, qtbot):
        """RFID card read populates the card ID field; user saved with card."""
        create_screen = app_on_create_user.stacked_widget.currentWidget()
        first, last, card = self._get_inputs(create_screen)

        # Simulate RFID scan
        app_on_create_user.state_manager.rfid_adapter.triggerFakeRead("123456789")
        qtbot.wait(100)

        assert card.text() == "123456789"

        qtbot.keyClicks(first, "Bob")
        qtbot.keyClicks(last, "Jones")
        self._click_register(create_screen, qtbot)

        qtbot.waitUntil(
            lambda: app_on_create_user.stacked_widget.currentWidget().objectName()
            == "loginScreen",
            timeout=2000,
        )

        patrons = app_on_create_user.state_manager.database.getAllPatrons()
        bob = [p for p in patrons if p.firstName == "Bob"]
        assert len(bob) == 1
        assert bob[0].employeeID == "123456789"

    def test_create_user_duplicate_card(self, app_with_users, qtbot):
        """Using an already-registered card shows an error."""
        app_with_users.state_manager.transition_to_screen("createUserScreen")
        qtbot.waitUntil(
            lambda: app_with_users.stacked_widget.currentWidget().objectName()
            == "createUserScreen",
            timeout=2000,
        )

        create_screen = app_with_users.stacked_widget.currentWidget()
        first, last, card = self._get_inputs(create_screen)

        app_with_users.state_manager.rfid_adapter.triggerFakeRead("111111111")
        qtbot.wait(100)
        assert card.text() == "111111111"

        qtbot.keyClicks(first, "Dupe")
        qtbot.keyClicks(last, "User")
        self._click_register(create_screen, qtbot)

        assert (
            app_with_users.stacked_widget.currentWidget().objectName()
            == "createUserScreen"
        )
        patrons = app_with_users.state_manager.database.getAllPatrons()
        assert len(patrons) == 3

    def test_create_user_empty_card_allowed(self, app_on_create_user, qtbot):
        """Creating a user without a card ID is allowed."""
        create_screen = app_on_create_user.stacked_widget.currentWidget()
        first, last, card = self._get_inputs(create_screen)

        qtbot.keyClicks(first, "Cardless")
        qtbot.keyClicks(last, "User")
        self._click_register(create_screen, qtbot)

        qtbot.waitUntil(
            lambda: app_on_create_user.stacked_widget.currentWidget().objectName()
            == "loginScreen",
            timeout=2000,
        )

        patrons = app_on_create_user.state_manager.database.getAllPatrons()
        cardless = [p for p in patrons if p.firstName == "Cardless"]
        assert len(cardless) == 1
        assert cardless[0].employeeID == ""

    def test_create_user_cancel(self, app_on_create_user, qtbot):
        """Clicking Cancel returns to login screen without creating a user."""
        create_screen = app_on_create_user.stacked_widget.currentWidget()
        first, last, card = self._get_inputs(create_screen)

        qtbot.keyClicks(first, "CancelMe")
        qtbot.keyClicks(last, "Test")

        cancel_btn = create_screen.findChild(QPushButton, "cancelButton")
        assert cancel_btn is not None, "cancelButton not found"
        qtbot.mouseClick(cancel_btn, Qt.MouseButton.LeftButton)

        qtbot.waitUntil(
            lambda: app_on_create_user.stacked_widget.currentWidget().objectName()
            == "loginScreen",
            timeout=2000,
        )
        assert len(app_on_create_user.state_manager.database.getAllPatrons()) == 0
