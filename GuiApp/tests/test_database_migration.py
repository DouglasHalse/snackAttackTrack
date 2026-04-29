import os
import shutil
import sqlite3

import pytest

from GuiApp.database import DatabaseConnector
from GuiApp.DatabaseMigrator import DatabaseMigrator

# Fixtures are counted as redefine-outer-name
# pylint: disable=redefined-outer-name


@pytest.fixture
def new_database_connector():
    if os.path.exists("test_new_database.db"):
        os.remove("test_new_database.db")
    database_connector = DatabaseConnector("test_new_database.db")
    yield database_connector
    if os.path.exists("test_new_database.db"):
        os.remove("test_new_database.db")


@pytest.fixture
def version_1_database():
    assert os.path.exists(
        "GuiApp/tests/database_test_version_1.db"
    ), "Could not find the test database file 'database_test_version_1.db'"

    # create working copy of the version 1 database for testing
    if os.path.exists("GuiApp/tests/test_version_1_database.db"):
        os.remove("GuiApp/tests/test_version_1_database.db")
    shutil.copy(
        "GuiApp/tests/database_test_version_1.db",
        "GuiApp/tests/test_version_1_database.db",
    )

    conn = sqlite3.connect("GuiApp/tests/test_version_1_database.db")
    cursor = conn.cursor()

    yield conn, cursor

    cursor.close()
    conn.close()

    if os.path.exists("GuiApp/tests/test_version_1_database.db"):
        os.remove("GuiApp/tests/test_version_1_database.db")


def test_get_stored_database_version_new_database(new_database_connector):
    with new_database_connector.connection as conn:
        cursor = conn.cursor()
        version = DatabaseMigrator.get_stored_database_version(cursor)
        assert version == DatabaseMigrator.CURRENT_SCHEMA_VERSION


def test_get_stored_database_version_version_1_database(version_1_database):
    _, cursor = version_1_database
    version = DatabaseMigrator.get_stored_database_version(cursor)
    assert version == 1


def test_needs_migration_version_1_database(version_1_database):
    _, cursor = version_1_database
    assert DatabaseMigrator.needs_migration(cursor) is True


def test_migrate_database_version_1_database(version_1_database):
    _, cursor = version_1_database

    # Before migration, the database should be at version 1
    version = DatabaseMigrator.get_stored_database_version(cursor)
    assert version == 1

    # List tables before migration
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;")
    print("Tables before migration:", cursor.fetchall())

    # Save data from Patrons table before migration
    cursor.execute("SELECT * FROM Patrons")
    patrons_data_before = cursor.fetchall()
    patron1 = patrons_data_before[0]
    patron1_id = patron1[0]
    patron1_first_name = patron1[1]
    patron1_last_name = patron1[2]
    patron1_employee_id = patron1[3]
    patron1_credits = patron1[4]

    # In version 1, credits are stored as a REAL representing the number of credits (e.g. 10.0)

    assert patron1_id == 1
    assert patron1_first_name == "Douglas"
    assert patron1_last_name == "Halse"
    assert patron1_employee_id == ""
    assert isinstance(patron1[4], float)
    assert patron1_credits == 50033.33
