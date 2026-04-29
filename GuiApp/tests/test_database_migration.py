import os
import shutil
import sqlite3

import pytest

from GuiApp.database import DatabaseConnector, LostSnackReason, TransactionType
from GuiApp.DatabaseMigrator import DatabaseMigrator

# Fixtures are counted as redefine-outer-name
# pylint: disable=redefined-outer-name
# pylint: disable=too-many-locals
# pylint: disable=too-many-statements


class PatronData:
    def __init__(self, patronId, firstName, lastName, employeeId, TotalCredits):
        self.patronId = patronId
        self.firstName = firstName
        self.lastName = lastName
        self.employeeId = employeeId
        self.credits = TotalCredits


class SnackData:
    def __init__(self, snackId, name, quantity, imageID, pricePerItem):
        self.snackId = snackId
        self.name = name
        self.quantity = quantity
        self.imageID = imageID
        self.pricePerItem = pricePerItem


class AddedSnackData:
    def __init__(self, addedSnackId, name, dateAdded, quantityAdded, totalPrice):
        self.addedSnackId = addedSnackId
        self.name = name
        self.dateAdded = dateAdded
        self.quantityAdded = quantityAdded
        self.totalPrice = totalPrice


class LostSnackData:
    def __init__(self, lostSnackId, name, reason, dateLost, quantityLost, totalPrice):
        self.lostSnackId = lostSnackId
        self.name = name
        self.reason = reason
        self.dateLost = dateLost
        self.quantityLost = quantityLost
        self.totalPrice = totalPrice


class TransactionData:
    def __init__(
        self,
        transactionId,
        transactionType,
        patronId,
        transactionDate,
        amountBeforeTransaction,
        amountAfterTransaction,
    ):
        self.transactionId = transactionId
        self.transactionType = transactionType
        self.patronId = patronId
        self.transactionDate = transactionDate
        self.amountBeforeTransaction = amountBeforeTransaction
        self.amountAfterTransaction = amountAfterTransaction


class TransactionItemData:
    def __init__(
        self, transactionItemId, transactionId, snackName, quantity, pricePerItem
    ):
        self.transactionItemId = transactionItemId
        self.transactionId = transactionId
        self.snackName = snackName
        self.quantity = quantity
        self.pricePerItem = pricePerItem


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
    user1_before = PatronData(*patrons_data_before[0])
    user2_before = PatronData(*patrons_data_before[1])
    user3_before = PatronData(*patrons_data_before[2])

    # Check that the data is as expected before migration
    assert user1_before.patronId == 1
    assert user1_before.firstName == "User1FirstName"
    assert user1_before.lastName == "User1LastName"
    assert user1_before.employeeId == ""
    assert isinstance(user1_before.credits, float)
    assert user1_before.credits == 5510.040000000001

    assert user2_before.patronId == 2
    assert user2_before.firstName == "User2FirstName"
    assert user2_before.lastName == "User2LastName"
    assert user2_before.employeeId == "12345678"
    assert isinstance(user2_before.credits, float)
    assert user2_before.credits == 221.94

    assert user3_before.patronId == 3
    assert user3_before.firstName == "User3FirstName"
    assert user3_before.lastName == "User3LastName"
    assert user3_before.employeeId == ""
    assert isinstance(user3_before.credits, float)
    assert user3_before.credits == 494.6

    cursor.execute("SELECT * FROM Snacks")
    snacks_data_before = cursor.fetchall()
    snack1_before = SnackData(*snacks_data_before[0])
    snack2_before = SnackData(*snacks_data_before[1])
    snack3_before = SnackData(*snacks_data_before[2])

    assert snack1_before.snackId == 1
    assert snack1_before.name == "Apple"
    assert snack1_before.quantity == 564
    assert snack1_before.imageID == "None"
    assert isinstance(snack1_before.pricePerItem, float)
    assert snack1_before.pricePerItem == 1.33

    assert snack2_before.snackId == 2
    assert snack2_before.name == "Orange"
    assert snack2_before.quantity == 505
    assert snack2_before.imageID == "None"
    assert isinstance(snack2_before.pricePerItem, float)
    assert snack2_before.pricePerItem == 14.73

    assert snack3_before.snackId == 3
    assert snack3_before.name == "Pear"
    assert snack3_before.quantity == 5888
    assert snack3_before.imageID == "None"
    assert isinstance(snack3_before.pricePerItem, float)
    assert snack3_before.pricePerItem == 0.14

    cursor.execute("SELECT * FROM AddedSnacks")
    added_snacks_data_before = cursor.fetchall()
    added_snack1_before = AddedSnackData(*added_snacks_data_before[0])
    added_snack2_before = AddedSnackData(*added_snacks_data_before[1])
    added_snack3_before = AddedSnackData(*added_snacks_data_before[2])

    assert added_snack1_before.addedSnackId == 1
    assert added_snack1_before.name == "Apple"
    assert added_snack1_before.dateAdded == "2026-04-29 20:59:33.290186"
    assert added_snack1_before.quantityAdded == 566
    assert isinstance(added_snack1_before.totalPrice, float)
    assert added_snack1_before.totalPrice == 685

    assert added_snack2_before.addedSnackId == 2
    assert added_snack2_before.name == "Orange"
    assert added_snack2_before.dateAdded == "2026-04-29 20:59:46.311367"
    assert added_snack2_before.quantityAdded == 556
    assert isinstance(added_snack2_before.totalPrice, float)
    assert added_snack2_before.totalPrice == 7445

    assert added_snack3_before.addedSnackId == 3
    assert added_snack3_before.name == "Pear"
    assert added_snack3_before.dateAdded == "2026-04-29 20:59:58.007470"
    assert added_snack3_before.quantityAdded == 5893
    assert isinstance(added_snack3_before.totalPrice, float)
    assert added_snack3_before.totalPrice == 771

    cursor.execute("SELECT * FROM LostSnacks")
    lost_snacks_data_before = cursor.fetchall()
    lost_snack1_before = LostSnackData(*lost_snacks_data_before[0])
    assert lost_snack1_before.lostSnackId == 1
    assert lost_snack1_before.name == "Orange"
    assert lost_snack1_before.reason == LostSnackReason.STOLEN.value
    assert lost_snack1_before.dateLost == "2026-04-29 21:01:20.062596"
    assert lost_snack1_before.quantityLost == 50
    assert isinstance(lost_snack1_before.totalPrice, float)
    assert lost_snack1_before.totalPrice == 736.5

    cursor.execute("SELECT * FROM Transactions")
    transactions_data_before = cursor.fetchall()
    transaction1_before = TransactionData(*transactions_data_before[0])
    transaction2_before = TransactionData(*transactions_data_before[1])
    transaction3_before = TransactionData(*transactions_data_before[2])
    transaction4_before = TransactionData(*transactions_data_before[3])
    transaction5_before = TransactionData(*transactions_data_before[4])
    transaction6_before = TransactionData(*transactions_data_before[5])
    assert transaction1_before.transactionId == 1
    assert transaction1_before.transactionType == TransactionType.TOP_UP.value
    assert transaction1_before.patronId == user1_before.patronId
    assert transaction1_before.transactionDate == "2026-04-29 20:59:19.980700"
    assert isinstance(transaction1_before.amountBeforeTransaction, float)
    assert transaction1_before.amountBeforeTransaction == 0.0
    assert isinstance(transaction1_before.amountAfterTransaction, float)
    assert transaction1_before.amountAfterTransaction == 5526.52

    assert transaction2_before.transactionId == 2
    assert transaction2_before.transactionType == TransactionType.EDIT.value
    assert transaction2_before.patronId == user2_before.patronId
    assert transaction2_before.transactionDate == "2026-04-29 21:00:13.147316"
    assert isinstance(transaction2_before.amountBeforeTransaction, float)
    assert transaction2_before.amountBeforeTransaction == 0.0
    assert isinstance(transaction2_before.amountAfterTransaction, float)
    assert transaction2_before.amountAfterTransaction == 222.22

    assert transaction3_before.transactionId == 3
    assert transaction3_before.transactionType == TransactionType.TOP_UP.value
    assert transaction3_before.patronId == user3_before.patronId
    assert transaction3_before.transactionDate == "2026-04-29 21:00:32.878661"
    assert isinstance(transaction3_before.amountBeforeTransaction, float)
    assert transaction3_before.amountBeforeTransaction == 0.0
    assert isinstance(transaction3_before.amountAfterTransaction, float)
    assert transaction3_before.amountAfterTransaction == 500

    assert transaction4_before.transactionId == 4
    assert transaction4_before.transactionType == TransactionType.GAMBLE.value
    assert transaction4_before.patronId == user3_before.patronId
    assert transaction4_before.transactionDate == "2026-04-29 21:00:37.649922"
    assert isinstance(transaction4_before.amountBeforeTransaction, float)
    assert transaction4_before.amountBeforeTransaction == 500.0
    assert isinstance(transaction4_before.amountAfterTransaction, float)
    assert transaction4_before.amountAfterTransaction == 494.6

    assert transaction5_before.transactionId == 5
    assert transaction5_before.transactionType == TransactionType.PURCHASE.value
    assert transaction5_before.patronId == user2_before.patronId
    assert transaction5_before.transactionDate == "2026-04-29 21:00:57.733077"
    assert isinstance(transaction5_before.amountBeforeTransaction, float)
    assert transaction5_before.amountBeforeTransaction == 222.22
    assert isinstance(transaction5_before.amountAfterTransaction, float)
    assert transaction5_before.amountAfterTransaction == 221.94

    assert transaction6_before.transactionId == 6
    assert transaction6_before.transactionType == TransactionType.PURCHASE.value
    assert transaction6_before.patronId == user1_before.patronId
    assert transaction6_before.transactionDate == "2026-04-29 21:01:46.745517"
    assert isinstance(transaction6_before.amountBeforeTransaction, float)
    assert transaction6_before.amountBeforeTransaction == 5526.52
    assert isinstance(transaction6_before.amountAfterTransaction, float)
    assert transaction6_before.amountAfterTransaction == 5510.040000000001

    cursor.execute("SELECT * FROM TransactionItems")
    transaction_items_data_before = cursor.fetchall()
    transaction_item1_before = TransactionItemData(*transaction_items_data_before[0])
    transaction_item2_before = TransactionItemData(*transaction_items_data_before[1])
    transaction_item3_before = TransactionItemData(*transaction_items_data_before[2])
    transaction_item4_before = TransactionItemData(*transaction_items_data_before[3])
    transaction_item5_before = TransactionItemData(*transaction_items_data_before[4])

    assert transaction_item1_before.transactionItemId == 1
    assert transaction_item1_before.transactionId == transaction4_before.transactionId
    assert transaction_item1_before.snackName == "Apple"
    assert transaction_item1_before.quantity == 1
    assert isinstance(transaction_item1_before.pricePerItem, float)
    assert transaction_item1_before.pricePerItem == 1.33

    assert transaction_item2_before.transactionItemId == 2
    assert transaction_item2_before.transactionId == transaction5_before.transactionId
    assert transaction_item2_before.snackName == "Pear"
    assert transaction_item2_before.quantity == 2
    assert isinstance(transaction_item2_before.pricePerItem, float)
    assert transaction_item2_before.pricePerItem == 0.14

    assert transaction_item3_before.transactionItemId == 3
    assert transaction_item3_before.transactionId == transaction6_before.transactionId
    assert transaction_item3_before.snackName == "Apple"
    assert transaction_item3_before.quantity == 1
    assert isinstance(transaction_item3_before.pricePerItem, float)
    assert transaction_item3_before.pricePerItem == 1.33

    assert transaction_item4_before.transactionItemId == 4
    assert transaction_item4_before.transactionId == transaction6_before.transactionId
    assert transaction_item4_before.snackName == "Orange"
    assert transaction_item4_before.quantity == 1
    assert isinstance(transaction_item4_before.pricePerItem, float)
    assert transaction_item4_before.pricePerItem == 14.73

    assert transaction_item5_before.transactionItemId == 5
    assert transaction_item5_before.transactionId == transaction6_before.transactionId
    assert transaction_item5_before.snackName == "Pear"
    assert transaction_item5_before.quantity == 3
    assert isinstance(transaction_item5_before.pricePerItem, float)
    assert transaction_item5_before.pricePerItem == 0.14

    # Perform migration
    DatabaseMigrator.migrate_database(*version_1_database)

    # After migration, the database should be at the current schema version
    version_after_migration = DatabaseMigrator.get_stored_database_version(cursor)
    assert version_after_migration == DatabaseMigrator.CURRENT_SCHEMA_VERSION

    # Verify data integrity after migration by checking that the data in the tables is the same except for the expected changes to the credits and pricePerItem fields, which should now be integers representing the value in hundredths of a credit.
    cursor.execute("SELECT * FROM Patrons")
    patrons_data_after = cursor.fetchall()
    user1_after = PatronData(*patrons_data_after[0])
    user2_after = PatronData(*patrons_data_after[1])
    user3_after = PatronData(*patrons_data_after[2])

    assert user1_after.patronId == user1_before.patronId
    assert user1_after.firstName == user1_before.firstName
    assert user1_after.lastName == user1_before.lastName
    assert user1_after.employeeId == user1_before.employeeId
    assert isinstance(user1_after.credits, int)
    assert user1_after.credits == int(user1_before.credits * 100)

    assert user2_after.patronId == user2_before.patronId
    assert user2_after.firstName == user2_before.firstName
    assert user2_after.lastName == user2_before.lastName
    assert user2_after.employeeId == user2_before.employeeId
    assert isinstance(user2_after.credits, int)
    assert user2_after.credits == int(user2_before.credits * 100)

    assert user3_after.patronId == user3_before.patronId
    assert user3_after.firstName == user3_before.firstName
    assert user3_after.lastName == user3_before.lastName
    assert user3_after.employeeId == user3_before.employeeId
    assert isinstance(user3_after.credits, int)
    assert user3_after.credits == int(user3_before.credits * 100)

    cursor.execute("SELECT * FROM Snacks")
    snacks_data_after = cursor.fetchall()
    snack1_after = SnackData(*snacks_data_after[0])
    snack2_after = SnackData(*snacks_data_after[1])
    snack3_after = SnackData(*snacks_data_after[2])

    assert snack1_after.snackId == snack1_before.snackId
    assert snack1_after.name == snack1_before.name
    assert snack1_after.quantity == snack1_before.quantity
    assert snack1_after.imageID == snack1_before.imageID
    assert isinstance(snack1_after.pricePerItem, int)
    assert snack1_after.pricePerItem == int(snack1_before.pricePerItem * 100)

    assert snack2_after.snackId == snack2_before.snackId
    assert snack2_after.name == snack2_before.name
    assert snack2_after.quantity == snack2_before.quantity
    assert snack2_after.imageID == snack2_before.imageID
    assert isinstance(snack2_after.pricePerItem, int)
    assert snack2_after.pricePerItem == int(snack2_before.pricePerItem * 100)

    assert snack3_after.snackId == snack3_before.snackId
    assert snack3_after.name == snack3_before.name
    assert snack3_after.quantity == snack3_before.quantity
    assert snack3_after.imageID == snack3_before.imageID
    assert isinstance(snack3_after.pricePerItem, int)
    assert snack3_after.pricePerItem == int(snack3_before.pricePerItem * 100)

    cursor.execute("SELECT * FROM AddedSnacks")
    added_snacks_data_after = cursor.fetchall()
    added_snack1_after = AddedSnackData(*added_snacks_data_after[0])
    added_snack2_after = AddedSnackData(*added_snacks_data_after[1])
    added_snack3_after = AddedSnackData(*added_snacks_data_after[2])

    assert added_snack1_after.addedSnackId == added_snack1_before.addedSnackId
    assert added_snack1_after.name == added_snack1_before.name
    assert added_snack1_after.dateAdded == added_snack1_before.dateAdded
    assert added_snack1_after.quantityAdded == added_snack1_before.quantityAdded
    assert isinstance(added_snack1_after.totalPrice, int)
    assert added_snack1_after.totalPrice == int(added_snack1_before.totalPrice * 100)

    assert added_snack2_after.addedSnackId == added_snack2_before.addedSnackId
    assert added_snack2_after.name == added_snack2_before.name
    assert added_snack2_after.dateAdded == added_snack2_before.dateAdded
    assert added_snack2_after.quantityAdded == added_snack2_before.quantityAdded
    assert isinstance(added_snack2_after.totalPrice, int)
    assert added_snack2_after.totalPrice == int(added_snack2_before.totalPrice * 100)

    assert added_snack3_after.addedSnackId == added_snack3_before.addedSnackId
    assert added_snack3_after.name == added_snack3_before.name
    assert added_snack3_after.dateAdded == added_snack3_before.dateAdded
    assert added_snack3_after.quantityAdded == added_snack3_before.quantityAdded
    assert isinstance(added_snack3_after.totalPrice, int)
    assert added_snack3_after.totalPrice == int(added_snack3_before.totalPrice * 100)

    cursor.execute("SELECT * FROM LostSnacks")
    lost_snacks_data_after = cursor.fetchall()
    lost_snack1_after = LostSnackData(*lost_snacks_data_after[0])
    assert lost_snack1_after.lostSnackId == lost_snack1_before.lostSnackId
    assert lost_snack1_after.name == lost_snack1_before.name
    assert lost_snack1_after.reason == lost_snack1_before.reason
    assert lost_snack1_after.dateLost == lost_snack1_before.dateLost
    assert lost_snack1_after.quantityLost == lost_snack1_before.quantityLost
    assert isinstance(lost_snack1_after.totalPrice, int)
    assert lost_snack1_after.totalPrice == int(lost_snack1_before.totalPrice * 100)

    cursor.execute("SELECT * FROM Transactions")
    transactions_data_after = cursor.fetchall()
    transaction1_after = TransactionData(*transactions_data_after[0])
    transaction2_after = TransactionData(*transactions_data_after[1])
    transaction3_after = TransactionData(*transactions_data_after[2])
    transaction4_after = TransactionData(*transactions_data_after[3])
    transaction5_after = TransactionData(*transactions_data_after[4])
    transaction6_after = TransactionData(*transactions_data_after[5])

    assert transaction1_after.transactionId == transaction1_before.transactionId
    assert transaction1_after.transactionType == transaction1_before.transactionType
    assert transaction1_after.patronId == transaction1_before.patronId
    assert transaction1_after.transactionDate == transaction1_before.transactionDate
    assert isinstance(transaction1_after.amountBeforeTransaction, int)
    assert transaction1_after.amountBeforeTransaction == int(
        transaction1_before.amountBeforeTransaction * 100
    )
    assert isinstance(transaction1_after.amountAfterTransaction, int)
    assert transaction1_after.amountAfterTransaction == int(
        transaction1_before.amountAfterTransaction * 100
    )

    assert transaction2_after.transactionId == transaction2_before.transactionId
    assert transaction2_after.transactionType == transaction2_before.transactionType
    assert transaction2_after.patronId == transaction2_before.patronId
    assert transaction2_after.transactionDate == transaction2_before.transactionDate
    assert isinstance(transaction2_after.amountBeforeTransaction, int)
    assert transaction2_after.amountBeforeTransaction == int(
        transaction2_before.amountBeforeTransaction * 100
    )
    assert isinstance(transaction2_after.amountAfterTransaction, int)
    assert transaction2_after.amountAfterTransaction == int(
        transaction2_before.amountAfterTransaction * 100
    )

    assert transaction3_after.transactionId == transaction3_before.transactionId
    assert transaction3_after.transactionType == transaction3_before.transactionType
    assert transaction3_after.patronId == transaction3_before.patronId
    assert transaction3_after.transactionDate == transaction3_before.transactionDate
    assert isinstance(transaction3_after.amountBeforeTransaction, int)
    assert transaction3_after.amountBeforeTransaction == int(
        transaction3_before.amountBeforeTransaction * 100
    )
    assert isinstance(transaction3_after.amountAfterTransaction, int)
    assert transaction3_after.amountAfterTransaction == int(
        transaction3_before.amountAfterTransaction * 100
    )

    assert transaction4_after.transactionId == transaction4_before.transactionId
    assert transaction4_after.transactionType == transaction4_before.transactionType
    assert transaction4_after.patronId == transaction4_before.patronId
    assert transaction4_after.transactionDate == transaction4_before.transactionDate
    assert isinstance(transaction4_after.amountBeforeTransaction, int)
    assert transaction4_after.amountBeforeTransaction == int(
        transaction4_before.amountBeforeTransaction * 100
    )
    assert isinstance(transaction4_after.amountAfterTransaction, int)
    assert transaction4_after.amountAfterTransaction == int(
        transaction4_before.amountAfterTransaction * 100
    )

    assert transaction5_after.transactionId == transaction5_before.transactionId
    assert transaction5_after.transactionType == transaction5_before.transactionType
    assert transaction5_after.patronId == transaction5_before.patronId
    assert transaction5_after.transactionDate == transaction5_before.transactionDate
    assert isinstance(transaction5_after.amountBeforeTransaction, int)
    assert transaction5_after.amountBeforeTransaction == int(
        transaction5_before.amountBeforeTransaction * 100
    )
    assert isinstance(transaction5_after.amountAfterTransaction, int)
    assert transaction5_after.amountAfterTransaction == int(
        transaction5_before.amountAfterTransaction * 100
    )

    assert transaction6_after.transactionId == transaction6_before.transactionId
    assert transaction6_after.transactionType == transaction6_before.transactionType
    assert transaction6_after.patronId == transaction6_before.patronId
    assert transaction6_after.transactionDate == transaction6_before.transactionDate
    assert isinstance(transaction6_after.amountBeforeTransaction, int)
    assert transaction6_after.amountBeforeTransaction == int(
        transaction6_before.amountBeforeTransaction * 100
    )
    assert isinstance(transaction6_after.amountAfterTransaction, int)
    assert transaction6_after.amountAfterTransaction == int(
        transaction6_before.amountAfterTransaction * 100
    )

    cursor.execute("SELECT * FROM TransactionItems")
    transaction_items_data_after = cursor.fetchall()
    transaction_item1_after = TransactionItemData(*transaction_items_data_after[0])
    transaction_item2_after = TransactionItemData(*transaction_items_data_after[1])
    transaction_item3_after = TransactionItemData(*transaction_items_data_after[2])
    transaction_item4_after = TransactionItemData(*transaction_items_data_after[3])
    transaction_item5_after = TransactionItemData(*transaction_items_data_after[4])

    assert (
        transaction_item1_after.transactionItemId
        == transaction_item1_before.transactionItemId
    )
    assert (
        transaction_item1_after.transactionId == transaction_item1_before.transactionId
    )
    assert transaction_item1_after.snackName == transaction_item1_before.snackName
    assert transaction_item1_after.quantity == transaction_item1_before.quantity
    assert isinstance(transaction_item1_after.pricePerItem, int)
    assert transaction_item1_after.pricePerItem == int(
        transaction_item1_before.pricePerItem * 100
    )

    assert (
        transaction_item2_after.transactionItemId
        == transaction_item2_before.transactionItemId
    )
    assert (
        transaction_item2_after.transactionId == transaction_item2_before.transactionId
    )
    assert transaction_item2_after.snackName == transaction_item2_before.snackName
    assert transaction_item2_after.quantity == transaction_item2_before.quantity
    assert isinstance(transaction_item2_after.pricePerItem, int)
    assert transaction_item2_after.pricePerItem == int(
        transaction_item2_before.pricePerItem * 100
    )

    assert (
        transaction_item3_after.transactionItemId
        == transaction_item3_before.transactionItemId
    )
    assert (
        transaction_item3_after.transactionId == transaction_item3_before.transactionId
    )
    assert transaction_item3_after.snackName == transaction_item3_before.snackName
    assert transaction_item3_after.quantity == transaction_item3_before.quantity
    assert isinstance(transaction_item3_after.pricePerItem, int)
    assert transaction_item3_after.pricePerItem == int(
        transaction_item3_before.pricePerItem * 100
    )

    assert (
        transaction_item4_after.transactionItemId
        == transaction_item4_before.transactionItemId
    )
    assert (
        transaction_item4_after.transactionId == transaction_item4_before.transactionId
    )
    assert transaction_item4_after.snackName == transaction_item4_before.snackName
    assert transaction_item4_after.quantity == transaction_item4_before.quantity
    assert isinstance(transaction_item4_after.pricePerItem, int)
    assert transaction_item4_after.pricePerItem == int(
        transaction_item4_before.pricePerItem * 100
    )

    assert (
        transaction_item5_after.transactionItemId
        == transaction_item5_before.transactionItemId
    )
    assert (
        transaction_item5_after.transactionId == transaction_item5_before.transactionId
    )
    assert transaction_item5_after.snackName == transaction_item5_before.snackName
    assert transaction_item5_after.quantity == transaction_item5_before.quantity
    assert isinstance(transaction_item5_after.pricePerItem, int)
    assert transaction_item5_after.pricePerItem == int(
        transaction_item5_before.pricePerItem * 100
    )
