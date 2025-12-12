"""
Database migration script to add PIN column to existing Patrons table.
Run this script once to update existing databases.
"""

import sqlite3
import sys


def migrate_database(database_path="database.db"):
    """Add PIN column to Patrons table if it doesn't exist."""
    try:
        connection = sqlite3.connect(database_path)
        cursor = connection.cursor()

        # Check if PIN column already exists
        cursor.execute("PRAGMA table_info(Patrons)")
        columns = cursor.fetchall()
        column_names = [column[1] for column in columns]

        if "PIN" not in column_names:
            print("Adding PIN column to Patrons table...")
            cursor.execute("ALTER TABLE Patrons ADD COLUMN PIN TEXT")
            connection.commit()
            print("✓ PIN column added successfully!")
            print("\nNote: Existing users will not have PINs set.")
            print("They can log in without a PIN until they set one.")
        else:
            print("PIN column already exists. No migration needed.")

        connection.close()
        return True

    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return False
    except Exception as e:
        print(f"Error: {e}")
        return False


if __name__ == "__main__":
    # Allow custom database path via command line argument
    db_path = sys.argv[1] if len(sys.argv) > 1 else "database.db"

    print(f"Migrating database: {db_path}")
    print("-" * 50)

    success = migrate_database(db_path)

    if success:
        print("\n✓ Migration completed successfully!")
        sys.exit(0)
    else:
        print("\n✗ Migration failed!")
        sys.exit(1)
