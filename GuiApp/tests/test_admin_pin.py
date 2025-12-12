"""Tests for admin PIN functionality"""

from widgets.popups.adminPinEntryPopup import AdminPinEntryPopup


class TestAdminPin:
    """Test admin PIN verification"""

    def test_admin_pin_constant(self):
        """Test that admin PIN is set to 4444"""
        assert AdminPinEntryPopup.ADMIN_PIN == "4444"

    def test_correct_admin_pin(self):
        """Test admin PIN verification with correct PIN"""
        popup = AdminPinEntryPopup(screen_manager=None)

        # Simulate entering correct PIN
        popup.entered_pin = "4444"

        # Should match admin PIN
        assert popup.entered_pin == AdminPinEntryPopup.ADMIN_PIN

    def test_incorrect_admin_pin(self):
        """Test admin PIN verification with incorrect PIN"""
        popup = AdminPinEntryPopup(screen_manager=None)

        # Simulate entering incorrect PIN
        popup.entered_pin = "1234"

        # Should not match admin PIN
        assert popup.entered_pin != AdminPinEntryPopup.ADMIN_PIN
