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

        # Change credits datatype to integer (hundreths of a credit)
        cursor.execute("ALTER TABLE users ADD COLUMN credits_temp INTEGER")
        cursor.execute("UPDATE users SET credits_temp = CAST(credits * 100 AS INTEGER)")
        cursor.execute("ALTER TABLE users DROP COLUMN credits")
        cursor.execute("ALTER TABLE users RENAME COLUMN credits_temp TO credits")
        connection.commit()
