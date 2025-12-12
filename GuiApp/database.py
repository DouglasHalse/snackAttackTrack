"""
Database connector for SnackAttack Track.

This module handles all database operations including:
- User management (create, read, update, delete)
- Snack inventory management
- Transaction history (purchases, top-ups, edits, gambling)
- RFID card linking
- Statistics and analytics

Database Schema:
- Patron: User accounts with credits and PINs
- RFID: RFID cards linked to users
- Snack: Inventory items with pricing
- TransactionTable: All financial transactions
- TransactionSnackTable: Items involved in each transaction
"""

import hashlib
import sqlite3
from datetime import datetime
from enum import Enum


class TransactionType(Enum):
    """
    Types of transactions that can occur in the system.

    PURCHASE: User bought snacks
    TOP_UP: User added credits to account
    EDIT: Admin modified user balance
    GAMBLE: User played wheel of snacks
    """

    PURCHASE = "PURCHASE"
    TOP_UP = "TOP_UP"
    EDIT = "EDIT"
    GAMBLE = "GAMBLE"


class LostSnackReason(Enum):
    """
    Reasons for removing snacks from inventory without sale.

    Used for tracking inventory loss and waste.
    """

    STOLEN = 1  # Theft
    EXPIRED = 2  # Past expiration date
    DAMAGED = 3  # Damaged/unsellable


def transactionTypeToPresentableString(transactionType: TransactionType) -> str:
    """
    Convert TransactionType enum to human-readable string.

    Args:
        transactionType: The transaction type enum value

    Returns:
        User-friendly string representation
    """
    if transactionType == TransactionType.PURCHASE:
        return "Purchase"
    if transactionType == TransactionType.TOP_UP:
        return "Top-up"
    if transactionType == TransactionType.EDIT:
        return "Edit"
    if transactionType == TransactionType.GAMBLE:
        return "Gamble"
    return "Unknown"


class UserData:
    """
    Data class representing a user account.

    Attributes:
        patronId: Unique user ID (auto-generated)
        firstName: User's first name
        lastName: User's last name
        employeeID: Company/organization employee ID
        totalCredits: Current account balance in currency
        pin: 4-digit PIN for authentication (optional)
    """

    def __init__(
        self, patronId, firstName, lastName, employeeID, totalCredits, pin=None
    ):
        self.patronId = patronId
        self.firstName = firstName
        self.lastName = lastName
        self.employeeID = employeeID
        self.totalCredits = totalCredits
        self.pin = pin


class SnackData:
    """
    Data class representing a snack item.

    Attributes:
        snackId: Unique snack ID (auto-generated)
        snackName: Display name of the snack
        quantity: Current stock quantity
        imageID: Filename of snack image (in GuiApp/Images/)
        pricePerItem: Cost per item in currency
    """

    def __init__(
        self,
        snackId: int,
        snackName: str,
        quantity: int,
        imageID: str,
        pricePerItem: float,
    ):
        self.snackId: int = snackId
        self.snackName: str = snackName
        self.quantity: int = quantity
        self.imageID: str = imageID
        self.pricePerItem: float = pricePerItem


class HistoryData:
    """
    Data class representing a transaction history entry.

    Attributes:
        transactionId: Unique transaction ID
        transactionType: Type of transaction (purchase/top-up/edit/gamble)
        transactionDate: Timestamp of transaction
        amountBeforeTransaction: Account balance before transaction
        amountAfterTransaction: Account balance after transaction
        transactionItems: List of snacks involved (empty for top-ups/edits)
    """

    def __init__(
        self,
        transactionId: int,
        transactionType: TransactionType,
        transactionDate: datetime,
        amountBeforeTransaction: float,
        amountAfterTransaction: float,
        transactionItems: list[SnackData],
    ):
        self.transactionId: int = transactionId
        self.transactionType: TransactionType = transactionType
        self.transactionDate: datetime = transactionDate
        self.amountBeforeTransaction: float = amountBeforeTransaction
        self.amountAfterTransaction: float = amountAfterTransaction
        self.transactionItems: list[SnackData] = transactionItems


# Disable too-many-public-methods for database class
# This is expected for a database connector with CRUD operations
# pylint: disable=too-many-public-methods


class DatabaseConnector:
    """
    Main database connector class handling all SQLite operations.

    This class provides methods for:
    - User CRUD operations
    - Snack inventory management
    - Transaction recording and history
    - RFID card management
    - Statistics and analytics

    Args:
        database_path: Path to SQLite database file (default: "database.db")
    """

    def __init__(self, database_path: str = "database.db"):
        # Connect to SQLite database (creates file if doesn't exist)
        self.connection = sqlite3.connect(database_path)
        self.cursor = self.connection.cursor()
        # Initialize all tables if they don't exist
        self.createAllTables()

    def close(self):
        """Close database connection. Call this when application exits."""
        self.connection.close()

    def createAllTables(self):
        """
        Create all required database tables if they don't exist.

        Tables created:
        - Patron: User accounts
        - RFID: RFID card mappings
        - Snack: Inventory items
        - TransactionTable: Financial transactions
        - TransactionSnackTable: Transaction line items
        - LostSnackTable: Inventory loss tracking
        """

        create_queries = [
            # Table of all the users
            # FirstName is the user's first name
            # LastName is the user's last name
            # EmployeeID is the user's employee ID
            # TotalCredits is the user's total credits
            # PIN is the user's 4-digit PIN for authentication (hashed with SHA-256)
            """
            CREATE TABLE IF NOT EXISTS Patrons (
                PatronID INTEGER PRIMARY KEY AUTOINCREMENT,
                FirstName TEXT NOT NULL,
                LastName TEXT NOT NULL,
                EmployeeID TEXT NOT NULL,
                TotalCredits REAL NOT NULL DEFAULT 0,
                PIN TEXT
            );
            """,
            # Table of all the snacks currently available for purchase
            # ItemName is name of the snack
            # Quantity is the number of snacks available for purchase
            # ImageID is the ID of the snack's image (unused)
            # PricePerItem is the price of a single snack
            """
            CREATE TABLE IF NOT EXISTS Snacks (
                ItemID INTEGER PRIMARY KEY AUTOINCREMENT,
                ItemName TEXT NOT NULL,
                Quantity INTEGER NOT NULL,
                ImageID TEXT NOT NULL,
                PricePerItem REAL NOT NULL
            );
            """,
            # Table of all the transactions that have occurred
            # TransactionType is one of TransactionType enum
            # PatronID references Patrons.PatronID
            # TransactionDate is stored as a string in the format "%Y-%m-%d %H:%M:%S.%f"
            # AmountBeforeTransaction is the amount of credits the patron had before the transaction
            # AmountAfterTransaction is the amount of credits the patron had after the transaction
            """
            CREATE TABLE IF NOT EXISTS Transactions (
                TransactionID INTEGER PRIMARY KEY AUTOINCREMENT,
                TransactionType TEXT NOT NULL,
                PatronID INTEGER NOT NULL, 
                TransactionDate TEXT NOT NULL, 
                AmountBeforeTransaction REAL NOT NULL, 
                AmountAfterTransaction REAL NOT NULL,
                FOREIGN KEY(PatronID) REFERENCES Patrons(PatronID)
            );
            """,
            # Table of all the items associated with a transaction
            # TransactionID references Transactions.TransactionID
            # ItemName references Snacks.ItemName
            # Quantity is the number of items of this type in the transaction
            # PricePerItem is the price of a single item of this type
            """
            CREATE TABLE IF NOT EXISTS TransactionItems (
                TransactionItemId INTEGER PRIMARY KEY AUTOINCREMENT,
                TransactionID INTEGER NOT NULL,
                ItemName TEXT NOT NULL,
                Quantity INTEGER NOT NULL,
                PricePerItem REAL NOT NULL,
                FOREIGN KEY(TransactionID) REFERENCES Transactions(TransactionID)
            );
            """,
            # Table of all added snacks to restock inventory
            # SnackName references Snacks.ItemName
            # AddedDate is stored as a string in the format "%Y-%m-%d %H:%M:%S.%f"
            # Quantity is the number of snacks added
            # Value is the total value of the added snacks
            """
            CREATE TABLE IF NOT EXISTS AddedSnacks (
                AddedID INTEGER PRIMARY KEY AUTOINCREMENT,
                SnackName TEXT NOT NULL,
                AddedDate TEXT NOT NULL,
                Quantity INTEGER NOT NULL,
                Value REAL NOT NULL
            );
            """,
            # Table of all snacks cosidered stolen or lost
            # SnackName references Snacks.ItemName
            # Reason references LostSnackReason enum
            # LostDate is stored as a string in the format "%Y-%m-%d %H:%M:%S.%f"
            # Quantity is the number of snacks lost
            # Value is the total value of the lost snacks
            """
            CREATE TABLE IF NOT EXISTS LostSnacks (
                LostID INTEGER PRIMARY KEY AUTOINCREMENT,
                SnackName TEXT NOT NULL,
                Reason INTEGER NOT NULL,
                LostDate TEXT NOT NULL,
                Quantity INTEGER NOT NULL,
                Value REAL NOT NULL
            );
            """,
        ]

        for query in create_queries:
            self.cursor.execute(query)

        self.connection.commit()

    # ============================================================================
    # INVENTORY TRACKING - Lost and Added Snacks
    # ============================================================================

    def clear_lost_snacks(self):
        """
        Remove all rows from LostSnacks table.

        Used for resetting inventory tracking data.
        """
        self.cursor.execute("DELETE FROM LostSnacks")
        self.connection.commit()

    def clear_added_snacks(self):
        """
        Remove all rows from AddedSnacks table.

        Used for resetting inventory tracking data.
        """
        self.cursor.execute("DELETE FROM AddedSnacks")
        self.connection.commit()

    def clear_transactions(self):
        """
        Remove all transaction history from database.

        Clears both TransactionItems and Transactions tables.
        TransactionItems must be cleared first to avoid foreign key violations.
        """
        self.cursor.execute("DELETE FROM TransactionItems")
        self.cursor.execute("DELETE FROM Transactions")
        self.connection.commit()

    def add_lost_snack(
        self,
        snack_name: str,
        reason: LostSnackReason,
        quantity: int,
        total_value: float,
    ):
        """
        Record snacks removed from inventory without sale.

        Used for tracking theft, expiration, damage, etc.

        Args:
            snack_name: Name of the snack removed
            reason: Reason for removal (LostSnackReason enum)
            quantity: Number of items removed
            total_value: Total value of removed items

        Returns:
            int: ID of the created LostSnacks record
        """
        assert isinstance(quantity, int)
        assert isinstance(total_value, float)
        assert isinstance(reason, LostSnackReason)
        assert reason in LostSnackReason

        # Record timestamp of loss
        lost_date = datetime.now()
        lost_date_str = lost_date.strftime("%Y-%m-%d %H:%M:%S.%f")

        self.cursor.execute(
            """
            INSERT INTO LostSnacks (SnackName, Reason, LostDate, Quantity, Value)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                snack_name,
                reason.value,
                lost_date_str,
                quantity,
                float(total_value),
            ),
        )
        self.connection.commit()
        return self.cursor.lastrowid

    def add_added_snack(
        self,
        snack_name: str,
        quantity: int,
        value: float,
    ):
        """
        Record snacks added to inventory.

        Used for tracking restocking and inventory additions.

        Args:
            snack_name: Name of the snack added
            quantity: Number of items added
            value: Total value of added items

        Returns:
            int: ID of the created AddedSnacks record
        """
        assert isinstance(quantity, int)
        assert isinstance(value, float)

        added_date = datetime.now()
        added_date_str = added_date.strftime("%Y-%m-%d %H:%M:%S.%f")
        self.cursor.execute(
            """
            INSERT INTO AddedSnacks (SnackName, AddedDate, Quantity, Value)
            VALUES (?, ?, ?, ?)
            """,
            (
                snack_name,
                added_date_str,
                quantity,
                float(value),
            ),
        )
        self.connection.commit()
        return self.cursor.lastrowid

    def get_value_of_added_snacks(self) -> float:
        self.cursor.execute("SELECT SUM(Value) FROM AddedSnacks")
        sqlResult = self.cursor.fetchone()
        total_value = sqlResult[0]
        if total_value is None:
            return 0.0
        return float(total_value)

    def get_total_snacks_added(self) -> int:
        self.cursor.execute("SELECT SUM(Quantity) FROM AddedSnacks")
        sqlResult = self.cursor.fetchone()
        total_snacks = sqlResult[0]
        if total_snacks is None:
            return 0
        return int(total_snacks)

    def get_value_of_lost_snacks(self) -> float:
        self.cursor.execute("SELECT SUM(Value) FROM LostSnacks")
        sqlResult = self.cursor.fetchone()
        total_value = sqlResult[0]
        if total_value is None:
            return 0.0
        return float(total_value)

    def get_total_snacks_lost(self) -> int:
        self.cursor.execute("SELECT SUM(Quantity) FROM LostSnacks")
        sqlResult = self.cursor.fetchone()
        total_snacks = sqlResult[0]
        if total_snacks is None:
            return 0
        return int(total_snacks)

    def addGambleTransaction(
        self,
        patronID: int,
        amountBeforeTransaction: float,
        amountAfterTransaction: float,
        transactionDate: str,
        transactionItem: SnackData,
    ):
        # Verify data types
        assert isinstance(patronID, int)
        assert isinstance(amountBeforeTransaction, float)
        assert isinstance(amountAfterTransaction, float)
        assert isinstance(transactionDate, datetime)
        assert isinstance(transactionItem, SnackData)

        self.cursor.execute(
            """
            INSERT INTO Transactions (TransactionType, PatronID, TransactionDate, AmountBeforeTransaction, AmountAfterTransaction)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                TransactionType.GAMBLE.value,
                patronID,
                transactionDate,
                amountBeforeTransaction,
                amountAfterTransaction,
            ),
        )
        transactionID = self.cursor.lastrowid
        self.cursor.execute(
            """
            INSERT INTO TransactionItems (TransactionID, ItemName, Quantity, PricePerItem)
            VALUES (?, ?, ?, ?)
            """,
            (
                transactionID,
                transactionItem.snackName,
                transactionItem.quantity,
                transactionItem.pricePerItem,
            ),
        )
        self.connection.commit()

    def addPurchaseTransaction(
        self,
        patronID: int,
        amountBeforeTransaction: float,
        amountAfterTransaction: float,
        transactionDate: str,
        transactionItems: list[SnackData],
    ):
        # Verify data types
        assert isinstance(patronID, int)
        assert isinstance(amountBeforeTransaction, float)
        assert isinstance(amountAfterTransaction, float)
        assert isinstance(transactionDate, datetime)
        assert isinstance(transactionItems, list)

        self.cursor.execute(
            """
            INSERT INTO Transactions (TransactionType, PatronID, TransactionDate, AmountBeforeTransaction, AmountAfterTransaction)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                TransactionType.PURCHASE.value,
                patronID,
                transactionDate,
                amountBeforeTransaction,
                amountAfterTransaction,
            ),
        )
        transactionID = self.cursor.lastrowid
        for transactionItem in transactionItems:
            self.cursor.execute(
                """
                INSERT INTO TransactionItems (TransactionID, ItemName, Quantity, PricePerItem)
                VALUES (?, ?, ?, ?)
                """,
                (
                    transactionID,
                    transactionItem.snackName,
                    transactionItem.quantity,
                    transactionItem.pricePerItem,
                ),
            )
        self.connection.commit()

    def addTopUpTransaction(
        self,
        patronID: int,
        amountBeforeTransaction: float,
        amountAfterTransaction: float,
        transactionDate: str,
    ):
        self.cursor.execute(
            """
            INSERT INTO Transactions (TransactionType, PatronID, TransactionDate, AmountBeforeTransaction, AmountAfterTransaction)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                TransactionType.TOP_UP.value,
                patronID,
                transactionDate,
                amountBeforeTransaction,
                amountAfterTransaction,
            ),
        )
        self.connection.commit()

    def addEditTransaction(
        self,
        patronID: int,
        amountBeforeTransaction: float,
        amountAfterTransaction: float,
        transactionDate: str,
    ):
        # Verify data types
        assert isinstance(patronID, int)
        assert isinstance(amountBeforeTransaction, float)
        assert isinstance(amountAfterTransaction, float)
        assert isinstance(transactionDate, datetime)

        self.cursor.execute(
            """
            INSERT INTO Transactions (TransactionType, PatronID, TransactionDate, AmountBeforeTransaction, AmountAfterTransaction)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                TransactionType.EDIT.value,
                patronID,
                transactionDate,
                amountBeforeTransaction,
                amountAfterTransaction,
            ),
        )
        self.connection.commit()

    def getTransactionItems(self, transactionID: int) -> list[SnackData]:
        self.cursor.execute(
            f"SELECT * FROM TransactionItems WHERE TransactionID = {transactionID}"
        )
        sqlResult = self.cursor.fetchall()
        transactionItems = []
        for transactionItemEntry in sqlResult:
            itemName = transactionItemEntry[2]
            quantity = transactionItemEntry[3]
            pricePerItem = transactionItemEntry[4]
            transactionItems.append(SnackData(-1, itemName, quantity, "", pricePerItem))
        return transactionItems

    def removeTransactionItems(self, transactionID: int):
        self.cursor.execute(
            f"DELETE FROM TransactionItems WHERE TransactionID = {transactionID}"
        )
        self.connection.commit()

    def getTransactions(self, patronID: int) -> list[HistoryData]:
        self.cursor.execute(f"SELECT * FROM Transactions WHERE PatronID = {patronID}")
        sqlResult = self.cursor.fetchall()
        transactionList = []
        for transactionEntry in sqlResult:
            transactionID = transactionEntry[0]
            transactionType = TransactionType(transactionEntry[1])
            transactionDate = transactionEntry[3]
            amountBeforeTransaction = transactionEntry[4]
            amountAfterTransaction = transactionEntry[5]
            transactionItems = self.getTransactionItems(transactionID)
            parsedDatetime = datetime.strptime(transactionDate, "%Y-%m-%d %H:%M:%S.%f")
            transactionData = HistoryData(
                transactionID,
                transactionType,
                parsedDatetime,
                amountBeforeTransaction,
                amountAfterTransaction,
                transactionItems,
            )
            transactionList.append(transactionData)
        return transactionList

    def getTransaction(self, transactionID: int) -> HistoryData:
        self.cursor.execute(
            f"SELECT * FROM Transactions WHERE TransactionID = {transactionID}"
        )
        sqlResult = self.cursor.fetchone()
        transactionID = sqlResult[0]
        transactionType = TransactionType(sqlResult[1])
        transactionDate = sqlResult[3]
        amountBeforeTransaction = sqlResult[4]
        amountAfterTransaction = sqlResult[5]
        transactionItems = self.getTransactionItems(transactionID)
        parsedDatetime = datetime.strptime(transactionDate, "%Y-%m-%d %H:%M:%S.%f")
        return HistoryData(
            transactionID,
            transactionType,
            parsedDatetime,
            amountBeforeTransaction,
            amountAfterTransaction,
            transactionItems,
        )

    def getTransactionIds(self, patronID: int):
        self.cursor.execute(
            f"SELECT TransactionID FROM Transactions WHERE PatronID = {patronID}"
        )
        sqlResult = self.cursor.fetchall()
        transactionIds = []
        for transactionEntry in sqlResult:
            transactionIds.append(transactionEntry[0])
        return transactionIds

    def getMostPurchasedSnacksByPatron(self, patronId: int) -> list[str]:
        """
        Get the most purchased snacks by a patron in descending order of quantity.
        """
        self.cursor.execute(
            f"""
            SELECT ItemName, SUM(Quantity) as TotalQuantity
            FROM TransactionItems
            WHERE TransactionID IN (
                SELECT TransactionID
                FROM Transactions
                WHERE PatronID = {patronId}
            )
            GROUP BY ItemName
            ORDER BY TotalQuantity DESC
            """
        )
        sqlResult = self.cursor.fetchall()
        mostPurchasedSnacks = []
        for entry in sqlResult:
            mostPurchasedSnacks.append(entry[0])
        return mostPurchasedSnacks

    def removeTransactions(self, patronID: int):
        self.cursor.execute(f"DELETE FROM Transactions WHERE PatronID = {patronID}")
        self.connection.commit()

    def getAllSnackTransactions(self) -> list[HistoryData]:
        """Get all snack purchase and gamble transactions across all patrons."""
        self.cursor.execute(
            "SELECT * FROM Transactions WHERE TransactionType IN ('PURCHASE', 'GAMBLE')"
        )
        sqlResult = self.cursor.fetchall()
        transactionList = []
        for transactionEntry in sqlResult:
            transactionID = transactionEntry[0]
            transactionType = TransactionType(transactionEntry[1])
            transactionDate = transactionEntry[3]
            amountBeforeTransaction = transactionEntry[4]
            amountAfterTransaction = transactionEntry[5]
            transactionItems = self.getTransactionItems(transactionID)
            parsedDatetime = datetime.strptime(transactionDate, "%Y-%m-%d %H:%M:%S.%f")
            transactionData = HistoryData(
                transactionID,
                transactionType,
                parsedDatetime,
                amountBeforeTransaction,
                amountAfterTransaction,
                transactionItems,
            )
            transactionList.append(transactionData)
        return transactionList

    def getAllTopUpTransactions(self) -> list[HistoryData]:
        """Get all top-up transactions across all patrons."""
        self.cursor.execute(
            "SELECT * FROM Transactions WHERE TransactionType = 'TOP_UP'"
        )
        sqlResult = self.cursor.fetchall()
        transactionList = []
        for transactionEntry in sqlResult:
            transactionID = transactionEntry[0]
            transactionType = TransactionType(transactionEntry[1])
            transactionDate = transactionEntry[3]
            amountBeforeTransaction = transactionEntry[4]
            amountAfterTransaction = transactionEntry[5]
            transactionItems = self.getTransactionItems(transactionID)
            parsedDatetime = datetime.strptime(transactionDate, "%Y-%m-%d %H:%M:%S.%f")
            transactionData = HistoryData(
                transactionID,
                transactionType,
                parsedDatetime,
                amountBeforeTransaction,
                amountAfterTransaction,
                transactionItems,
            )
            transactionList.append(transactionData)
        return transactionList

    def addPatron(self, first_name, last_name, employee_id, pin=None):
        hashed_pin = None
        if pin:
            # Hash the PIN with SHA-256 for security
            hashed_pin = hashlib.sha256(pin.encode()).hexdigest()

        self.cursor.execute(
            """
            INSERT INTO Patrons (FirstName, LastName, EmployeeID, PIN)
            VALUES (?, ?, ?, ?)
            """,
            (first_name, last_name, employee_id, hashed_pin),
        )
        self.connection.commit()

    def getAllPatrons(self) -> list[UserData]:
        self.cursor.execute("SELECT * FROM Patrons")
        sqlResult = self.cursor.fetchall()
        userDataList = []
        for userEntry in sqlResult:
            patronId = userEntry[0]
            firstName = userEntry[1]
            lastName = userEntry[2]
            employeeID = userEntry[3]
            totalCredits = userEntry[4]
            pin = userEntry[5] if len(userEntry) > 5 else None
            userData = UserData(
                patronId, firstName, lastName, employeeID, totalCredits, pin
            )
            userDataList.append(userData)
        return userDataList

    def getPatronData(self, patronID: int) -> UserData:
        self.cursor.execute(f"SELECT * FROM Patrons WHERE PatronID = {patronID}")
        sqlResult = self.cursor.fetchone()
        patronId = sqlResult[0]
        firstName = sqlResult[1]
        lastName = sqlResult[2]
        employeeID = sqlResult[3]
        totalCredits = sqlResult[4]
        pin = sqlResult[5] if len(sqlResult) > 5 else None
        return UserData(patronId, firstName, lastName, employeeID, totalCredits, pin)

    def getPatronByID(self, patronID: int) -> UserData:
        """Alias for getPatronData for consistency with test naming"""
        return self.getPatronData(patronID)

    def getPatronByEmployeeId(self, employeeId: int) -> UserData:
        """Get patron by employee ID"""
        self.cursor.execute(f"SELECT * FROM Patrons WHERE EmployeeID = {employeeId}")
        sqlResult = self.cursor.fetchone()
        if sqlResult is None:
            return None
        patronId = sqlResult[0]
        firstName = sqlResult[1]
        lastName = sqlResult[2]
        employeeID = sqlResult[3]
        totalCredits = sqlResult[4]
        pin = sqlResult[5] if len(sqlResult) > 5 else None
        return UserData(patronId, firstName, lastName, employeeID, totalCredits, pin)

    def updatePatronData(self, patronId: int, newUserData: UserData):
        self.cursor.execute(
            f"UPDATE Patrons Set FirstName = '{newUserData.firstName}', LastName = '{newUserData.lastName}', EmployeeID = '{newUserData.employeeID}', TotalCredits = {newUserData.totalCredits} WHERE PatronID = {patronId}"
        )
        self.connection.commit()

    def updatePatronPin(self, patronId: int, new_pin: str) -> bool:
        """Update the PIN for a patron. Returns True on success, False on failure."""
        try:
            hashed_pin = hashlib.sha256(new_pin.encode()).hexdigest()
            self.cursor.execute(
                "UPDATE Patrons SET PIN = ? WHERE PatronID = ?", (hashed_pin, patronId)
            )
            self.connection.commit()
            return True
        except Exception as e:
            print(f"Error updating patron PIN: {e}")
            return False

    def updateSnackData(self, snackId: int, newSnackData: SnackData):
        self.cursor.execute(
            f"UPDATE Snacks Set ItemName = '{newSnackData.snackName}', Quantity = {newSnackData.quantity}, ImageID = '{newSnackData.imageID}', PricePerItem = {newSnackData.pricePerItem} WHERE ItemID = {snackId}"
        )
        self.connection.commit()

    def removePatron(self, patronId: int):
        self.cursor.execute(f"DELETE from Patrons WHERE PatronID = {patronId}")
        self.connection.commit()

        patronsTransactionIds = self.getTransactionIds(patronId)
        for transactionId in patronsTransactionIds:
            self.removeTransactionItems(transactionId)
        self.removeTransactions(patronId)

    def removeSnack(self, snackId: int):
        self.cursor.execute(f"DELETE from Snacks WHERE ItemID = {snackId}")
        self.connection.commit()

    def subtractPatronCredits(self, patronID: int, creditsToSubtract: float):
        patronData = self.getPatronData(patronID=patronID)
        oldCreditsAmount = patronData.totalCredits
        newCreditsAmount = oldCreditsAmount - creditsToSubtract
        self.cursor.execute(
            f"UPDATE Patrons Set TotalCredits = {newCreditsAmount} WHERE PatronID = {patronID}"
        )
        self.connection.commit()

    def addSnack(self, itemName, quantity, imageID, pricePerItem):
        self.cursor.execute(
            """
            INSERT INTO Snacks (ItemName, Quantity, ImageID, PricePerItem)
            VALUES (?, ?, ?, ?)
            """,
            (itemName, quantity, imageID, pricePerItem),
        )
        self.connection.commit()

    def getSnack(self, snackId: int) -> SnackData:
        self.cursor.execute(f"SELECT * FROM Snacks WHERE ItemID = {snackId}")
        sqlResult = self.cursor.fetchone()
        snackId = sqlResult[0]
        snackName = sqlResult[1]
        quantity = sqlResult[2]
        imageId = sqlResult[3]
        pricePerItem = sqlResult[4]
        return SnackData(
            snackId=snackId,
            snackName=snackName,
            quantity=quantity,
            imageID=imageId,
            pricePerItem=pricePerItem,
        )

    def subtractSnackQuantity(self, snackId: int, quantity: int):
        snack = self.getSnack(snackId=snackId)
        oldQuantity = snack.quantity
        newQuantity = oldQuantity - quantity
        self.cursor.execute(
            f"UPDATE Snacks Set Quantity = {newQuantity} WHERE ItemID = {snackId}"
        )
        self.connection.commit()

    def getAllSnacks(self) -> list[SnackData]:
        self.cursor.execute("SELECT * FROM Snacks")
        sqlResult = self.cursor.fetchall()
        snackDataList = []
        for snackEntry in sqlResult:
            snackId = snackEntry[0]
            snackName = snackEntry[1]
            quantity = snackEntry[2]
            imageId = snackEntry[3]
            pricePerItem = snackEntry[4]
            snackData = SnackData(
                snackId=snackId,
                snackName=snackName,
                quantity=quantity,
                imageID=imageId,
                pricePerItem=pricePerItem,
            )
            snackDataList.append(snackData)
        return snackDataList

    def getSnackByID(self, snackId: int) -> SnackData:
        """Alias for getSnack for consistency with test naming"""
        return self.getSnack(snackId)

    def getSnackByName(self, snackName: str) -> SnackData:
        """Get snack by name"""
        self.cursor.execute(f"SELECT * FROM Snacks WHERE ItemName = '{snackName}'")
        sqlResult = self.cursor.fetchone()
        if sqlResult is None:
            return None
        snackId = sqlResult[0]
        snackName = sqlResult[1]
        quantity = sqlResult[2]
        imageId = sqlResult[3]
        pricePerItem = sqlResult[4]
        return SnackData(
            snackId=snackId,
            snackName=snackName,
            quantity=quantity,
            imageID=imageId,
            pricePerItem=pricePerItem,
        )

    def updateSnackQuantity(self, snackId: int, quantity: int):
        """Update the quantity of a snack to a specific value"""
        self.cursor.execute(
            f"UPDATE Snacks Set Quantity = {quantity} WHERE ItemID = {snackId}"
        )
        self.connection.commit()

    def getLowInventorySnacks(self, threshold: int) -> list[SnackData]:
        """Get all snacks with quantity at or below the threshold."""
        self.cursor.execute("SELECT * FROM Snacks WHERE Quantity <= ?", (threshold,))
        sqlResult = self.cursor.fetchall()
        snackDataList = []
        for snackEntry in sqlResult:
            snackId = snackEntry[0]
            snackName = snackEntry[1]
            quantity = snackEntry[2]
            imageId = snackEntry[3]
            pricePerItem = snackEntry[4]
            snackData = SnackData(
                snackId=snackId,
                snackName=snackName,
                quantity=quantity,
                imageID=imageId,
                pricePerItem=pricePerItem,
            )
            snackDataList.append(snackData)
        return snackDataList

    def addCredits(self, userId: int, amount: float):
        self.cursor.execute(
            f"SELECT TotalCredits FROM Patrons WHERE PatronID = {userId}"
        )
        sqlResult = self.cursor.fetchone()
        currentCredits = float(sqlResult[0])
        newTotalCredits = currentCredits + amount
        self.cursor.execute(
            f"""
            UPDATE Patrons
            SET TotalCredits = {newTotalCredits}
            WHERE PatronID = {userId}
            """
        )
        self.connection.commit()

    def getPatronIdByCardId(self, cardId: str) -> int:
        self.cursor.execute(
            f"SELECT PatronID FROM Patrons WHERE EmployeeID = '{cardId}'"
        )
        sqlResult = self.cursor.fetchone()
        if sqlResult:
            return sqlResult[0]
        return None

    def verifyPatronPin(self, patronID: int, pin: str) -> bool:
        """Verify if the provided PIN matches the patron's stored PIN."""
        patron_data = self.getPatronData(patronID)

        # If user has no PIN set, allow access (for backward compatibility)
        if patron_data.pin is None:
            return True

        # Hash the provided PIN and compare
        hashed_pin = hashlib.sha256(pin.encode()).hexdigest()
        return hashed_pin == patron_data.pin
