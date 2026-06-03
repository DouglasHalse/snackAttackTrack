#!/usr/bin/env python3
"""
Standalone script to fix v1-to-v2 migration issues in a SnackAttackTrack database.

This script:
  1. Ensures Patrons.TotalCredits has NOT NULL DEFAULT 0
     (recreates the table if the default is missing — needed for databases
      migrated before migration_2 included the DEFAULT 0 fix)
  2. Fixes any NULL values in all credit columns across all tables

Usage:
    python scripts/fix_database_version_1_migration.py path/to/database.db
"""

import datetime
import os
import sqlite3
import sys


FIXES = [
    # (table, column, description)
    ("Patrons", "TotalCredits", "user credits"),
    ("Snacks", "PricePerItem", "snack price per item"),
    ("AddedSnacks", "Value", "added snack value"),
    ("LostSnacks", "Value", "lost snack value"),
    ("Transactions", "AmountBeforeTransaction", "transaction before-amount"),
    ("Transactions", "AmountAfterTransaction", "transaction after-amount"),
    ("TransactionItems", "PricePerItem", "transaction item price"),
]

# Full CREATE statement for Patrons with DEFAULT 0 on TotalCredits.
# Used when recreating the table to add the missing default.
PATRONS_CREATE_SQL = """\
CREATE TABLE Patrons_new (
    PatronID INTEGER PRIMARY KEY AUTOINCREMENT,
    FirstName TEXT NOT NULL,
    LastName TEXT NOT NULL,
    EmployeeID TEXT NOT NULL,
    TotalCredits INTEGER NOT NULL DEFAULT 0
)
"""


def create_backup(db_path: str) -> str:
    """Create a timestamped backup of the database. Returns the backup path."""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    backup_path = f"database_backup_fix_{timestamp}.db"
    source = sqlite3.connect(db_path)
    target = sqlite3.connect(backup_path)
    source.backup(target=target, pages=0, progress=None)
    target.close()
    source.close()
    print(f"  💾 Backup created: {backup_path}")
    return backup_path


def check_patrons_totalcredits_needs_fix(cursor: sqlite3.Cursor) -> bool:
    """Check if Patrons.TotalCredits is missing DEFAULT 0."""
    cursor.execute("PRAGMA table_info('Patrons')")
    columns = cursor.fetchall()
    for col in columns:
        name, dflt_value = col[1], col[4]
        if name == "TotalCredits":
            return dflt_value != "0"
    return False


def fix_patrons_totalcredits_default(
    conn: sqlite3.Connection, cursor: sqlite3.Cursor
) -> bool:
    """Recreate Patrons table with DEFAULT 0 on TotalCredits.
    Any existing NULL values are converted to 0 during the copy.
    Uses a transaction to prevent database corruption if the process crashes."""
    print("  ⚠️  Patrons.TotalCredits: missing DEFAULT 0 — recreating table")
    cursor.execute("PRAGMA foreign_keys = OFF")
    try:
        cursor.execute("BEGIN")
        cursor.execute(PATRONS_CREATE_SQL)
        # Use IFNULL to convert any existing NULLs to 0 (NOT NULL constraint)
        cursor.execute(
            "INSERT INTO Patrons_new (PatronID, FirstName, LastName, EmployeeID, TotalCredits) "
            "SELECT PatronID, FirstName, LastName, EmployeeID, IFNULL(TotalCredits, 0) "
            "FROM Patrons"
        )
        cursor.execute("DROP TABLE Patrons")
        cursor.execute("ALTER TABLE Patrons_new RENAME TO Patrons")
        conn.commit()
    except BaseException:
        conn.rollback()
        print("     ❌ Failed to recreate Patrons table — rolled back")
        raise
    finally:
        cursor.execute("PRAGMA foreign_keys = ON")
    print("     ✅ Added DEFAULT 0 to Patrons.TotalCredits")
    return True


def fix_null_credits(conn: sqlite3.Connection, cursor: sqlite3.Cursor) -> bool:
    """Fix NULL values in all credit columns. Returns True if any NULLs fixed."""
    total_fixed = 0
    any_fixed = False

    for table, column, description in FIXES:
        cursor.execute(f"SELECT COUNT(*) FROM [{table}] WHERE [{column}] IS NULL")
        count = cursor.fetchone()[0]

        if count > 0:
            any_fixed = True
            total_fixed += count
            print(
                f"  ⚠️  {table}.{column} ({description}): "
                f"{count} NULL value{'s' if count != 1 else ''} found"
            )
            cursor.execute(
                f"UPDATE [{table}] SET [{column}] = 0 WHERE [{column}] IS NULL"
            )
        else:
            print(f"  ✅ {table}.{column} ({description}): clean")

    if any_fixed:
        print(
            f"\n  Fixed {total_fixed} NULL value{'s' if total_fixed != 1 else ''} "
            f"across {len(FIXES)} tables"
        )
    else:
        print("\n  No NULL values found")

    return any_fixed


def fix_database(db_path: str, dry_run: bool = False) -> bool:
    """Fix issues in the database. Returns True if anything was fixed."""

    if not os.path.isfile(db_path):
        print(f"❌ Database not found: {db_path}", file=sys.stderr)
        return False

    print(f"📁 Database: {db_path}")
    if dry_run:
        print("🔍 Dry-run mode — no changes will be made")

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # --- Check phase: determine what needs fixing ---
    needs_default_fix = check_patrons_totalcredits_needs_fix(cursor)
    needs_null_fix = False
    for table, column, _ in FIXES:
        cursor.execute(f"SELECT COUNT(*) FROM [{table}] WHERE [{column}] IS NULL")
        if cursor.fetchone()[0] > 0:
            needs_null_fix = True
            break

    any_change = needs_default_fix or needs_null_fix

    if not any_change:
        print("\n✅ Database is clean — no issues found")
        conn.close()
        return False

    # --- Report what needs fixing ---
    print()
    if needs_default_fix:
        print("  ⚠️  Patrons.TotalCredits missing DEFAULT 0")
    if needs_null_fix:
        print("  ⚠️  NULL values found in credit columns")

    if dry_run:
        print("\n🔍 Would fix the issues above")
        conn.close()
        return True

    # --- Backup phase ---
    print("\nCreating backup before modifications...")
    create_backup(db_path)
    # Re-open (backup closed our connection)
    conn.close()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # --- Fix phase ---
    print()
    if needs_default_fix:
        fix_patrons_totalcredits_default(conn, cursor)

    print()
    if needs_null_fix:
        fix_null_credits(conn, cursor)

    conn.commit()
    print("\n✅ Database fixed successfully")
    conn.close()
    return True


def main():
    if len(sys.argv) < 2 or sys.argv[1] in ("-h", "--help"):
        print(__doc__)
        print("Options:")
        print("  --dry-run    Show what would be fixed without making changes")
        print()
        print("Examples:")
        print(f"  python {sys.argv[0]} database.db")
        print(f"  python {sys.argv[0]} /home/pi/snackattack/database.db --dry-run")
        return

    db_path = sys.argv[1]
    dry_run = "--dry-run" in sys.argv

    if not os.path.isfile(db_path):
        print(f"❌ File not found: {db_path}", file=sys.stderr)
        sys.exit(1)

    fix_database(db_path, dry_run=dry_run)


if __name__ == "__main__":
    main()
