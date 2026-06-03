"""
Tests for the fix_database_version_1_migration.py standalone script.

Verifies the script correctly:
  - Adds DEFAULT 0 to Patrons.TotalCredits when missing
  - Fixes NULL values in all credit columns
  - Creates backups before making changes
  - Does nothing when the database is already clean
  - Respects --dry-run mode
"""

import gc
import glob
import os
import sqlite3
import time

import pytest

from scripts.fix_database_version_1_migration import (
    check_patrons_totalcredits_needs_fix,
    create_backup,
    fix_database,
    fix_null_credits,
    fix_patrons_totalcredits_default,
)

# Disable too-many-public-methods for test class
# pylint: disable=too-many-public-methods

# Disable redefined-outer-name since fixtures use the same parameter names
# pylint: disable=redefined-outer-name


def _remove_if_exists(path, retries=5, delay=0.5):
    """Try to remove a file, retrying on PermissionError (Windows SQLite)."""
    attempt = 0
    while attempt < retries:
        try:
            if os.path.exists(path):
                gc.collect()
                os.remove(path)
            return
        except OSError:
            attempt += 1
            if attempt < retries:
                time.sleep(delay)


def _cleanup_artifacts():
    """Clean up all database artifacts left by this test module."""
    for pattern in (
        "database_backup_fix_*.db",
        "test_missing_default_*.db",
        "test_clean_*.db",
        "test_has_nulls_*.db",
    ):
        for f in glob.glob(pattern):
            _remove_if_exists(f)


def teardown_module(module=None):
    """Module-level cleanup of any leftover test artifacts."""
    _cleanup_artifacts()


_COUNTER = 0


def _next_path(prefix):
    """Return a unique database path to avoid cross-test file conflicts."""
    global _COUNTER  # pylint: disable=global-statement
    _COUNTER += 1
    return f"{prefix}_{_COUNTER}.db"


def _count_nulls(cursor, table, column):
    """Count NULL values in a specific column."""
    cursor.execute(f"SELECT COUNT(*) FROM [{table}] WHERE [{column}] IS NULL")
    return cursor.fetchone()[0]


def _get_column_default(cursor, table, column):
    """Get the default value of a column via PRAGMA table_info."""
    cursor.execute(f"PRAGMA table_info('{table}')")
    for col in cursor.fetchall():
        if col[1] == column:
            return col[4]  # dflt_value
    return None


# ── Fixtures ──────────────────────────────────────────────


@pytest.fixture(autouse=True)
def cleanup_artifacts():
    """Ensure test database and backup files are cleaned before and after each test."""
    _cleanup_artifacts()
    yield
    _cleanup_artifacts()


def _build_missing_default_db(db_path):
    """Create a database simulating the old buggy migration state."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.executescript(
        "CREATE TABLE Patrons (PatronID INTEGER PRIMARY KEY AUTOINCREMENT, "
        "FirstName TEXT NOT NULL, LastName TEXT NOT NULL, EmployeeID TEXT NOT NULL, "
        "TotalCredits INTEGER); "
        "CREATE TABLE Snacks (ItemID INTEGER PRIMARY KEY AUTOINCREMENT, "
        "ItemName TEXT NOT NULL, Quantity INTEGER NOT NULL, ImageID TEXT NOT NULL, "
        "PricePerItem INTEGER); "
        "CREATE TABLE AddedSnacks (AddedID INTEGER PRIMARY KEY AUTOINCREMENT, "
        "SnackName TEXT NOT NULL, AddedDate TEXT NOT NULL, Quantity INTEGER NOT NULL, "
        "Value INTEGER); "
        "CREATE TABLE LostSnacks (LostID INTEGER PRIMARY KEY AUTOINCREMENT, "
        "SnackName TEXT NOT NULL, Reason INTEGER NOT NULL, LostDate TEXT NOT NULL, "
        "Quantity INTEGER NOT NULL, Value INTEGER); "
        "CREATE TABLE Transactions (TransactionID INTEGER PRIMARY KEY AUTOINCREMENT, "
        "TransactionType TEXT NOT NULL, PatronID INTEGER NOT NULL, "
        "TransactionDate TEXT NOT NULL, AmountBeforeTransaction INTEGER NOT NULL, "
        "AmountAfterTransaction INTEGER NOT NULL, "
        "FOREIGN KEY(PatronID) REFERENCES Patrons(PatronID)); "
        "CREATE TABLE TransactionItems (TransactionItemId INTEGER PRIMARY KEY AUTOINCREMENT, "
        "TransactionID INTEGER NOT NULL, ItemName TEXT NOT NULL, Quantity INTEGER NOT NULL, "
        "PricePerItem INTEGER, FOREIGN KEY(TransactionID) REFERENCES Transactions(TransactionID)); "
        "INSERT INTO Patrons (FirstName, LastName, EmployeeID, TotalCredits) "
        "VALUES ('Alice', 'Smith', 'A001', 1000); "
        "INSERT INTO Patrons (FirstName, LastName, EmployeeID, TotalCredits) "
        "VALUES ('Bob', 'Jones', 'B002', 2000); "
        "INSERT INTO Patrons (FirstName, LastName, EmployeeID, TotalCredits) "
        "VALUES ('Charlie', 'Brown', 'C003', NULL); "
        "INSERT INTO Snacks (ItemName, Quantity, ImageID, PricePerItem) "
        "VALUES ('Apple', 10, 'img1', NULL); "
        "INSERT INTO Snacks (ItemName, Quantity, ImageID, PricePerItem) "
        "VALUES ('Orange', 5, 'img2', 100); "
        "INSERT INTO Transactions (TransactionType, PatronID, TransactionDate, "
        "AmountBeforeTransaction, AmountAfterTransaction) "
        "VALUES ('TOP_UP', 1, '2026-01-01 12:00:00.000000', 0, 1000);"
    )

    conn.commit()
    conn.close()
    return db_path


def _build_clean_db(db_path):
    """Create a fully correct v2 database (DEFAULT 0, no NULLs)."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.executescript(
        "CREATE TABLE Patrons (PatronID INTEGER PRIMARY KEY AUTOINCREMENT, "
        "FirstName TEXT NOT NULL, LastName TEXT NOT NULL, EmployeeID TEXT NOT NULL, "
        "TotalCredits INTEGER NOT NULL DEFAULT 0); "
        "CREATE TABLE Snacks (ItemID INTEGER PRIMARY KEY AUTOINCREMENT, "
        "ItemName TEXT NOT NULL, Quantity INTEGER NOT NULL, ImageID TEXT NOT NULL, "
        "PricePerItem INTEGER NOT NULL DEFAULT 0); "
        "CREATE TABLE AddedSnacks (AddedID INTEGER PRIMARY KEY AUTOINCREMENT, "
        "SnackName TEXT NOT NULL, AddedDate TEXT NOT NULL, Quantity INTEGER NOT NULL, "
        "Value INTEGER NOT NULL DEFAULT 0); "
        "CREATE TABLE LostSnacks (LostID INTEGER PRIMARY KEY AUTOINCREMENT, "
        "SnackName TEXT NOT NULL, Reason INTEGER NOT NULL, LostDate TEXT NOT NULL, "
        "Quantity INTEGER NOT NULL, Value INTEGER NOT NULL DEFAULT 0); "
        "CREATE TABLE Transactions (TransactionID INTEGER PRIMARY KEY AUTOINCREMENT, "
        "TransactionType TEXT NOT NULL, PatronID INTEGER NOT NULL, "
        "TransactionDate TEXT NOT NULL, AmountBeforeTransaction INTEGER NOT NULL DEFAULT 0, "
        "AmountAfterTransaction INTEGER NOT NULL DEFAULT 0); "
        "CREATE TABLE TransactionItems (TransactionItemId INTEGER PRIMARY KEY AUTOINCREMENT, "
        "TransactionID INTEGER NOT NULL, ItemName TEXT NOT NULL, Quantity INTEGER NOT NULL, "
        "PricePerItem INTEGER NOT NULL DEFAULT 0, "
        "FOREIGN KEY(TransactionID) REFERENCES Transactions(TransactionID)); "
        "INSERT INTO Patrons (FirstName, LastName, EmployeeID, TotalCredits) "
        "VALUES ('Alice', 'Smith', 'A001', 1000); "
        "INSERT INTO Patrons (FirstName, LastName, EmployeeID, TotalCredits) "
        "VALUES ('Bob', 'Jones', 'B002', 500);"
    )

    conn.commit()
    conn.close()
    return db_path


@pytest.fixture
def db_with_default_missing():
    db_path = _next_path("test_missing_default")
    _remove_if_exists(db_path)
    _build_missing_default_db(db_path)
    yield db_path
    _remove_if_exists(db_path)


@pytest.fixture
def db_clean():
    db_path = _next_path("test_clean")
    _remove_if_exists(db_path)
    _build_clean_db(db_path)
    yield db_path
    _remove_if_exists(db_path)


# ── Tests ─────────────────────────────────────────────────


class TestCheckPatronsTotalCreditsNeedsFix:
    """Tests for check_patrons_totalcredits_needs_fix()."""

    def test_detects_missing_default(self, db_with_default_missing):
        conn = sqlite3.connect(db_with_default_missing)
        cursor = conn.cursor()
        assert check_patrons_totalcredits_needs_fix(cursor) is True
        conn.close()

    def test_no_fix_needed_when_default_exists(self, db_clean):
        conn = sqlite3.connect(db_clean)
        cursor = conn.cursor()
        assert check_patrons_totalcredits_needs_fix(cursor) is False
        conn.close()


class TestFixPatronsTotalCreditsDefault:
    """Tests for fix_patrons_totalcredits_default()."""

    def test_adds_default(self, db_with_default_missing):
        conn = sqlite3.connect(db_with_default_missing)
        cursor = conn.cursor()

        assert _get_column_default(cursor, "Patrons", "TotalCredits") is None

        # Get data before fix to verify after
        cursor.execute("SELECT * FROM Patrons ORDER BY PatronID")
        data_before = cursor.fetchall()

        fix_patrons_totalcredits_default(conn, cursor)
        conn.commit()

        # Verify DEFAULT 0 was added
        assert _get_column_default(cursor, "Patrons", "TotalCredits") == "0"

        # Verify data preserved — NULL should have been converted to 0
        cursor.execute("SELECT * FROM Patrons ORDER BY PatronID")
        data_after = cursor.fetchall()
        for before_row, after_row in zip(data_before, data_after):
            # PatronID, FirstName, LastName, EmployeeID match
            assert before_row[:4] == after_row[:4]
            # TotalCredits: NULL becomes 0, otherwise unchanged
            expected = before_row[4] if before_row[4] is not None else 0
            assert after_row[4] == expected, (
                f"Patron {before_row[0]}: expected credits={expected}, "
                f"got {after_row[4]}"
            )

        # Verify foreign key still works (Transactions references Patrons)
        cursor.execute("SELECT * FROM Transactions")
        txns = cursor.fetchall()
        assert len(txns) == 1
        assert txns[0][1] == "TOP_UP"

        conn.close()

    def test_preserves_integrity_with_foreign_keys(self, db_with_default_missing):
        """Verify data integrity and FK-constrained inserts work after table recreation."""
        conn = sqlite3.connect(db_with_default_missing)
        cursor = conn.cursor()
        cursor.execute("PRAGMA foreign_keys = ON")

        fix_patrons_totalcredits_default(conn, cursor)
        conn.commit()

        # Verify existing data intact via FK relationship
        cursor.execute(
            "SELECT t.TransactionType, p.FirstName "
            "FROM Transactions t JOIN Patrons p ON t.PatronID = p.PatronID"
        )
        rows = cursor.fetchall()
        assert len(rows) == 1
        assert rows[0] == ("TOP_UP", "Alice")

        # Verify inserting a transaction referencing an existing patron works
        cursor.execute(
            "INSERT INTO Transactions "
            "(TransactionType, PatronID, TransactionDate, "
            "AmountBeforeTransaction, AmountAfterTransaction) "
            "VALUES ('TOP_UP', 1, '2026-06-01 10:00:00.000000', 1000, 1500)"
        )
        conn.commit()
        assert cursor.lastrowid is not None

        conn.close()


class TestFixNullCredits:
    """Tests for fix_null_credits()."""

    def test_fixes_nulls(self, db_with_default_missing):
        conn = sqlite3.connect(db_with_default_missing)
        cursor = conn.cursor()

        assert _count_nulls(cursor, "Patrons", "TotalCredits") == 1
        assert _count_nulls(cursor, "Snacks", "PricePerItem") == 1

        fix_null_credits(conn, cursor)
        conn.commit()

        assert _count_nulls(cursor, "Patrons", "TotalCredits") == 0
        assert _count_nulls(cursor, "Snacks", "PricePerItem") == 0

        # Verify non-NULL values unchanged
        cursor.execute("SELECT TotalCredits FROM Patrons WHERE PatronID = 2")
        assert cursor.fetchone()[0] == 2000
        cursor.execute("SELECT PricePerItem FROM Snacks WHERE ItemID = 2")
        assert cursor.fetchone()[0] == 100

        conn.close()

    def test_no_nulls_no_change(self, db_clean):
        """Already clean — no NULLs anywhere."""
        conn = sqlite3.connect(db_clean)
        cursor = conn.cursor()

        n_before = _count_nulls(cursor, "Patrons", "TotalCredits")
        fix_null_credits(conn, cursor)
        n_after = _count_nulls(cursor, "Patrons", "TotalCredits")
        assert n_after == n_before

        conn.close()


class TestFixDatabase:
    """Tests for fix_database()."""

    def test_fixes_default_and_nulls(self, db_with_default_missing):
        """Database with missing DEFAULT 0 and NULLs — both get fixed."""
        result = fix_database(db_with_default_missing, dry_run=False)

        assert result is True

        conn = sqlite3.connect(db_with_default_missing)
        cursor = conn.cursor()

        # DEFAULT 0 added
        assert _get_column_default(cursor, "Patrons", "TotalCredits") == "0"

        # NULLs fixed
        assert _count_nulls(cursor, "Patrons", "TotalCredits") == 0
        cursor.execute("SELECT TotalCredits FROM Patrons WHERE PatronID = 3")
        assert cursor.fetchone()[0] == 0

        # non-NULL values preserved
        cursor.execute("SELECT TotalCredits FROM Patrons WHERE PatronID = 1")
        assert cursor.fetchone()[0] == 1000
        cursor.execute("SELECT TotalCredits FROM Patrons WHERE PatronID = 2")
        assert cursor.fetchone()[0] == 2000

        conn.close()

        # Backup was created
        backups = glob.glob("database_backup_fix_*.db")
        assert len(backups) >= 1

    def test_clean_database_no_change(self, db_clean):
        """Fully correct database — no issues to fix."""
        result = fix_database(db_clean, dry_run=False)
        assert result is False  # Nothing to fix

        # No backup should have been created
        backups = glob.glob("database_backup_fix_*.db")
        assert len(backups) == 0

    def test_dry_run_does_not_modify(self, db_with_default_missing):
        """Dry run should detect issues but not fix them."""
        result = fix_database(db_with_default_missing, dry_run=True)

        assert result is True

        conn = sqlite3.connect(db_with_default_missing)
        cursor = conn.cursor()

        # DEFAULT still missing
        assert _get_column_default(cursor, "Patrons", "TotalCredits") is None

        # NULLs still present
        assert _count_nulls(cursor, "Patrons", "TotalCredits") >= 1

        conn.close()

        # No backup created
        backups = glob.glob("database_backup_fix_*.db")
        assert len(backups) == 0

    def test_fixes_both_issues(self, db_with_default_missing):
        """Both missing DEFAULT and NULLs get fixed in one run."""
        result = fix_database(db_with_default_missing, dry_run=False)

        assert result is True

        conn = sqlite3.connect(db_with_default_missing)
        cursor = conn.cursor()

        assert _get_column_default(cursor, "Patrons", "TotalCredits") == "0"
        assert _count_nulls(cursor, "Patrons", "TotalCredits") == 0
        assert _count_nulls(cursor, "Snacks", "PricePerItem") == 0

        cursor.execute("SELECT TotalCredits FROM Patrons WHERE PatronID = 1")
        assert cursor.fetchone()[0] == 1000
        cursor.execute("SELECT TotalCredits FROM Patrons WHERE PatronID = 2")
        assert cursor.fetchone()[0] == 2000

        conn.close()

        backups = glob.glob("database_backup_fix_*.db")
        assert len(backups) >= 1


class TestCreateBackup:
    """Tests for create_backup()."""

    def test_backup_is_identical(self, db_with_default_missing):
        original_size = os.path.getsize(db_with_default_missing)

        backup_path = create_backup(db_with_default_missing)

        assert os.path.exists(backup_path)
        assert os.path.getsize(backup_path) == original_size

        _remove_if_exists(backup_path)

    def test_backup_filename_format(self, db_with_default_missing):
        backup_path = create_backup(db_with_default_missing)

        assert backup_path.startswith("database_backup_fix_")
        assert backup_path.endswith(".db")

        _remove_if_exists(backup_path)


class TestTransactionRollback:
    """Tests that the table recreation rolls back safely on failure."""

    def test_rollback_on_lock_conflict(self, db_with_default_missing):
        """
        If another connection holds a lock, the table recreation should fail
        and leave the original Patrons table intact.
        """
        # Snapshot data before the attempted fix
        conn1 = sqlite3.connect(db_with_default_missing)
        cursor1 = conn1.cursor()
        cursor1.execute("SELECT * FROM Patrons ORDER BY PatronID")
        data_before = cursor1.fetchall()
        assert len(data_before) == 3
        assert _get_column_default(cursor1, "Patrons", "TotalCredits") is None

        # Connection 2 acquires a RESERVED lock (open transaction + write)
        conn2 = sqlite3.connect(db_with_default_missing)
        cursor2 = conn2.cursor()
        cursor2.execute("BEGIN")
        cursor2.execute(
            "INSERT INTO Patrons (FirstName, LastName, EmployeeID, TotalCredits) "
            "VALUES ('LOCK', 'Test', 'LOCK', 0)"
        )
        # Don't commit — conn2 now holds a RESERVED lock

        # Connection 1 tries to recreate the table — should fail
        with pytest.raises(sqlite3.OperationalError):
            fix_patrons_totalcredits_default(conn1, cursor1)

        conn1.rollback()  # Undo any partial changes from the failed attempt

        # Verify original Patrons table is intact and DEFAULT was NOT added
        assert _get_column_default(cursor1, "Patrons", "TotalCredits") is None
        cursor1.execute("SELECT * FROM Patrons ORDER BY PatronID")
        data_after = cursor1.fetchall()
        assert data_after == data_before

        # Verify FK still references work
        cursor1.execute("SELECT TransactionType FROM Transactions WHERE PatronID = 1")
        assert cursor1.fetchone()[0] == "TOP_UP"

        # Clean up connection 2
        conn2.rollback()
        conn2.close()
        conn1.close()

    def test_rollback_preserves_fk_integrity(self, db_with_default_missing):
        """After a failed rollback, FK constraints should still be enforceable."""
        conn = sqlite3.connect(db_with_default_missing)
        cursor = conn.cursor()
        cursor.execute("PRAGMA foreign_keys = ON")

        # Lock via second connection
        conn2 = sqlite3.connect(db_with_default_missing)
        cursor2 = conn2.cursor()
        cursor2.execute("BEGIN")
        cursor2.execute(
            "INSERT INTO Patrons (FirstName, LastName, EmployeeID, TotalCredits) "
            "VALUES ('LOCK', 'Test', 'LOCK', 0)"
        )

        with pytest.raises(sqlite3.OperationalError):
            fix_patrons_totalcredits_default(conn, cursor)

        conn.rollback()
        conn2.rollback()
        conn2.close()

        # Verify FK enforcement still works — valid insert should succeed
        cursor.execute(
            "INSERT INTO Transactions "
            "(TransactionType, PatronID, TransactionDate, "
            "AmountBeforeTransaction, AmountAfterTransaction) "
            "VALUES ('TOP_UP', 1, '2026-06-01 10:00:00.000000', 1000, 1500)"
        )
        conn.commit()
        assert cursor.lastrowid is not None

        conn.close()
