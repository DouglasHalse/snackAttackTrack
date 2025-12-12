"""Tests for PIN security functionality"""

import pytest
from database import DatabaseConnector


class TestPinSecurity:
    """Test PIN creation and verification"""

    def test_create_user_with_pin(self, tmp_path):
        """Test creating a user with a PIN"""
        db_path = tmp_path / "test.db"
        db = DatabaseConnector(str(db_path))

        # Create user with PIN
        db.addPatron("John", "Doe", "12345", "1234")

        # Verify user was created
        patrons = db.getAllPatrons()
        assert len(patrons) == 1
        assert patrons[0].firstName == "John"
        assert patrons[0].pin is not None

        db.close()

    def test_verify_correct_pin(self, tmp_path):
        """Test PIN verification with correct PIN"""
        db_path = tmp_path / "test.db"
        db = DatabaseConnector(str(db_path))

        # Create user with PIN
        db.addPatron("Jane", "Smith", "54321", "5678")
        patrons = db.getAllPatrons()
        patron_id = patrons[0].patronId

        # Verify correct PIN
        assert db.verifyPatronPin(patron_id, "5678") is True

        db.close()

    def test_verify_incorrect_pin(self, tmp_path):
        """Test PIN verification with incorrect PIN"""
        db_path = tmp_path / "test.db"
        db = DatabaseConnector(str(db_path))

        # Create user with PIN
        db.addPatron("Bob", "Jones", "11111", "9999")
        patrons = db.getAllPatrons()
        patron_id = patrons[0].patronId

        # Verify incorrect PIN
        assert db.verifyPatronPin(patron_id, "0000") is False

        db.close()

    def test_backward_compatibility_no_pin(self, tmp_path):
        """Test that users without PINs can still log in"""
        db_path = tmp_path / "test.db"
        db = DatabaseConnector(str(db_path))

        # Create user without PIN (backward compatibility)
        db.addPatron("Alice", "Brown", "22222")
        patrons = db.getAllPatrons()
        patron_id = patrons[0].patronId

        # Should allow login even without PIN
        assert db.verifyPatronPin(patron_id, "") is True
        assert db.verifyPatronPin(patron_id, "1234") is True

        db.close()

    def test_pin_hashing(self, tmp_path):
        """Test that PINs are hashed and not stored in plaintext"""
        db_path = tmp_path / "test.db"
        db = DatabaseConnector(str(db_path))

        # Create user with PIN
        pin = "4321"
        db.addPatron("Charlie", "Davis", "33333", pin)
        patrons = db.getAllPatrons()

        # Verify PIN is hashed (not stored as plaintext)
        assert patrons[0].pin != pin
        assert len(patrons[0].pin) == 64  # SHA-256 hash length in hex

        db.close()
