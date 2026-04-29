import sqlite3


class DatabaseMigrator:

    CURRENT_SCHEMA_VERSION = 2

    SCHEMA_VERSIONS = {
        1: "Initial schema version",  # Initial version, no schema version table is created yet.
        2: "Add schema version tracking and change to credits datatype to hundreths of a credit (integer)",
    }

    @staticmethod
    def get_stored_database_version(cursor: sqlite3.Cursor) -> int:
        try:
            cursor.execute("SELECT value FROM settings WHERE name = 'schema_version'")
            result = cursor.fetchone()
            if result is None:
                raise sqlite3.OperationalError(
                    "Schema version not found in settings table."
                )
            return int(result[0])
        except sqlite3.OperationalError:
            # If the settings table doesn't exist, we assume it's version 1.
            return 1

    @staticmethod
    def needs_migration(cursor: sqlite3.Cursor) -> bool:
        stored_version = DatabaseMigrator.get_stored_database_version(cursor)
        return stored_version < DatabaseMigrator.CURRENT_SCHEMA_VERSION

    @staticmethod
    def migrate_database(connection, cursor):
        current_version = DatabaseMigrator.get_stored_database_version(cursor)

        for version in range(
            current_version + 1, DatabaseMigrator.CURRENT_SCHEMA_VERSION + 1
        ):
            method = getattr(DatabaseMigrator, f"migration_{version}", None)
            if method:
                method(connection, cursor)
                cursor.execute(
                    "UPDATE settings SET value = ? WHERE name = 'schema_version'",
                    (version,),
                )
                connection.commit()

    @staticmethod
    def migration_2(connection, cursor):
        # Create the settings table if it doesn't exist and set schema_version to 1 if it's not set
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS settings (
                name TEXT PRIMARY KEY,
                value TEXT NOT NULL
            )
        """
        )
        cursor.execute(
            """
            INSERT OR IGNORE INTO settings (name, value) VALUES ('schema_version', '1')
        """
        )

        # Change TotalCredits from REAL to INTEGER for Patrons (hundreths of a credit)
        cursor.execute("ALTER TABLE Patrons ADD COLUMN TotalCredits_temp INTEGER")
        cursor.execute(
            "UPDATE Patrons SET TotalCredits_temp = CAST(TotalCredits * 100 AS INTEGER)"
        )
        cursor.execute("ALTER TABLE Patrons DROP COLUMN TotalCredits")
        cursor.execute(
            "ALTER TABLE Patrons RENAME COLUMN TotalCredits_temp TO TotalCredits"
        )

        # Change PricePerItem from REAL to INTEGER for Snacks (hundreths of a credit)
        cursor.execute("ALTER TABLE Snacks ADD COLUMN PricePerItem_temp INTEGER")
        cursor.execute(
            "UPDATE Snacks SET PricePerItem_temp = CAST(PricePerItem * 100 AS INTEGER)"
        )
        cursor.execute("ALTER TABLE Snacks DROP COLUMN PricePerItem")
        cursor.execute(
            "ALTER TABLE Snacks RENAME COLUMN PricePerItem_temp TO PricePerItem"
        )

        # Change Value from REAL to INTEGER for AddedSnacks (hundreths of a credit)
        cursor.execute("ALTER TABLE AddedSnacks ADD COLUMN Value_temp INTEGER")
        cursor.execute(
            "UPDATE AddedSnacks SET Value_temp = CAST(Value * 100 AS INTEGER)"
        )
        cursor.execute("ALTER TABLE AddedSnacks DROP COLUMN Value")
        cursor.execute("ALTER TABLE AddedSnacks RENAME COLUMN Value_temp TO Value")

        # Change Value from REAL to INTEGER for LostSnacks (hundreths of a credit)
        cursor.execute("ALTER TABLE LostSnacks ADD COLUMN Value_temp INTEGER")
        cursor.execute(
            "UPDATE LostSnacks SET Value_temp = CAST(Value * 100 AS INTEGER)"
        )
        cursor.execute("ALTER TABLE LostSnacks DROP COLUMN Value")
        cursor.execute("ALTER TABLE LostSnacks RENAME COLUMN Value_temp TO Value")

        # Change AmountBeforeTransaction and AmountAfterTransaction from REAL to INTEGER for Transactions (hundreths of a credit)
        cursor.execute(
            "ALTER TABLE Transactions ADD COLUMN AmountBeforeTransaction_temp INTEGER"
        )
        cursor.execute(
            "UPDATE Transactions SET AmountBeforeTransaction_temp = CAST(AmountBeforeTransaction * 100 AS INTEGER)"
        )
        cursor.execute(
            "ALTER TABLE Transactions ADD COLUMN AmountAfterTransaction_temp INTEGER"
        )
        cursor.execute(
            "UPDATE Transactions SET AmountAfterTransaction_temp = CAST(AmountAfterTransaction * 100 AS INTEGER)"
        )
        cursor.execute("ALTER TABLE Transactions DROP COLUMN AmountBeforeTransaction")
        cursor.execute("ALTER TABLE Transactions DROP COLUMN AmountAfterTransaction")
        cursor.execute(
            "ALTER TABLE Transactions RENAME COLUMN AmountBeforeTransaction_temp TO AmountBeforeTransaction"
        )
        cursor.execute(
            "ALTER TABLE Transactions RENAME COLUMN AmountAfterTransaction_temp TO AmountAfterTransaction"
        )

        # Change Amount from REAL to INTEGER for TransactionItems (hundreths of a credit)
        cursor.execute(
            "ALTER TABLE TransactionItems ADD COLUMN PricePerItem_temp INTEGER"
        )
        cursor.execute(
            "UPDATE TransactionItems SET PricePerItem_temp = CAST(PricePerItem * 100 AS INTEGER)"
        )
        cursor.execute("ALTER TABLE TransactionItems DROP COLUMN PricePerItem")
        cursor.execute(
            "ALTER TABLE TransactionItems RENAME COLUMN PricePerItem_temp TO PricePerItem"
        )

        connection.commit()
