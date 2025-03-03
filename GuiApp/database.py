import sqlite3
from enum import Enum
from datetime import datetime

# pylint: disable=too-many-public-methods


class TransactionType(Enum):
    PURCHASE = "PURCHASE"
    TOP_UP = "TOP_UP"
    EDIT = "EDIT"


def transactionTypeToPresentableString(transactionType: TransactionType) -> str:
    if transactionType == TransactionType.PURCHASE:
        return "Purchase"
    if transactionType == TransactionType.TOP_UP:
        return "Top-up"
    if transactionType == TransactionType.EDIT:
        return "Edit"
    return "Unknown"


class UserData:
    def __init__(self, patronId, firstName, lastName, employeeID, totalCredits):
        self.patronId = patronId
        self.firstName = firstName
        self.lastName = lastName
        self.employeeID = employeeID
        self.totalCredits = totalCredits


class SnackData:
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


class Database:
    def __init__(self, db_name="database.db"):
        self.db_name = db_name
        self.create_all_tables()

    def _connect(self):
        return sqlite3.connect(self.db_name)

    def create_all_tables(self):
        connection = self._connect()
        cursor = connection.cursor()

        create_queries = [
            """
            CREATE TABLE IF NOT EXISTS Patrons (
                PatronID INTEGER PRIMARY KEY AUTOINCREMENT,
                FirstName TEXT NOT NULL,
                LastName TEXT NOT NULL,
                EmployeeID TEXT NOT NULL,
                TotalCredits REAL NOT NULL DEFAULT 0
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS Snacks (
                ItemID INTEGER PRIMARY KEY AUTOINCREMENT,
                ItemName TEXT NOT NULL,
                Quantity INTEGER NOT NULL,
                ImageID TEXT NOT NULL,
                PricePerItem REAL NOT NULL
            );
            """,
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
        ]

        for query in create_queries:
            cursor.execute(query)

        connection.commit()
        connection.close()

    def add_purchase_transaction(
        self,
        patronID: int,
        amountBeforeTransaction: float,
        amountAfterTransaction: float,
        transactionDate: datetime,
        transactionItems: list[SnackData],
    ):
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute(
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
        transactionID = cursor.lastrowid
        for transactionItem in transactionItems:
            cursor.execute(
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
        conn.commit()
        conn.close()

    def add_top_up_transaction(
        self,
        patronID: int,
        amountBeforeTransaction: float,
        amountAfterTransaction: float,
        transactionDate: datetime,
    ):
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute(
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
        conn.commit()
        conn.close()

    def add_edit_transaction(
        self,
        patronID: int,
        amountBeforeTransaction: float,
        amountAfterTransaction: float,
        transactionDate: datetime,
    ):
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute(
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
        conn.commit()
        conn.close()

    def get_transaction_items(self, transactionID: int) -> list[SnackData]:
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute(
            f"SELECT * FROM TransactionItems WHERE TransactionID = {transactionID}"
        )
        sqlResult = cursor.fetchall()
        transactionItems = []
        for transactionItemEntry in sqlResult:
            itemName = transactionItemEntry[2]
            quantity = transactionItemEntry[3]
            pricePerItem = transactionItemEntry[4]
            transactionItems.append(SnackData(-1, itemName, quantity, "", pricePerItem))
        conn.close()
        return transactionItems

    def remove_transaction_items(self, transactionID: int):
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute(
            f"DELETE FROM TransactionItems WHERE TransactionID = {transactionID}"
        )
        conn.commit()
        conn.close()

    def get_transactions(self, patronID: int):
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM Transactions WHERE PatronID = {patronID}")
        sqlResult = cursor.fetchall()
        transactionList = []
        for transactionEntry in sqlResult:
            transactionID = transactionEntry[0]
            transactionType = TransactionType(transactionEntry[1])
            transactionDate = transactionEntry[3]
            amountBeforeTransaction = transactionEntry[4]
            amountAfterTransaction = transactionEntry[5]
            transactionItems = self.get_transaction_items(transactionID)
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
        conn.close()
        return transactionList

    def get_transaction(self, transactionID: int) -> HistoryData:
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute(
            f"SELECT * FROM Transactions WHERE TransactionID = {transactionID}"
        )
        sqlResult = cursor.fetchone()
        transactionID = sqlResult[0]
        transactionType = TransactionType(sqlResult[1])
        transactionDate = sqlResult[3]
        amountBeforeTransaction = sqlResult[4]
        amountAfterTransaction = sqlResult[5]
        transactionItems = self.get_transaction_items(transactionID)
        parsedDatetime = datetime.strptime(transactionDate, "%Y-%m-%d %H:%M:%S.%f")
        conn.close()
        return HistoryData(
            transactionID,
            transactionType,
            parsedDatetime,
            amountBeforeTransaction,
            amountAfterTransaction,
            transactionItems,
        )

    def get_transaction_ids(self, patronID: int):
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute(
            f"SELECT TransactionID FROM Transactions WHERE PatronID = {patronID}"
        )
        sqlResult = cursor.fetchall()
        transactionIds = [transactionEntry[0] for transactionEntry in sqlResult]
        conn.close()
        return transactionIds

    def remove_transactions(self, patronID: int):
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute(f"DELETE FROM Transactions WHERE PatronID = {patronID}")
        conn.commit()
        conn.close()

    def add_patron(self, first_name, last_name, employee_id):
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO Patrons (FirstName, LastName, EmployeeID)
            VALUES (?, ?, ?)
            """,
            (first_name, last_name, employee_id),
        )
        conn.commit()
        conn.close()

    def get_all_patrons(self) -> list[UserData]:
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Patrons")
        sqlResult = cursor.fetchall()
        userDataList = [
            UserData(
                userEntry[0], userEntry[1], userEntry[2], userEntry[3], userEntry[4]
            )
            for userEntry in sqlResult
        ]
        conn.close()
        return userDataList

    def get_patron_data(self, patronID: int) -> UserData:
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM Patrons WHERE PatronID = {patronID}")
        sqlResult = cursor.fetchone()
        conn.close()
        return UserData(
            sqlResult[0], sqlResult[1], sqlResult[2], sqlResult[3], sqlResult[4]
        )

    def update_patron_data(self, patronId: int, newUserData: UserData):
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute(
            f"UPDATE Patrons Set FirstName = '{newUserData.firstName}', LastName = '{newUserData.lastName}', EmployeeID = '{newUserData.employeeID}', TotalCredits = {newUserData.totalCredits} WHERE PatronID = {patronId}"
        )
        conn.commit()
        conn.close()

    def update_snack_data(self, snackId: int, newSnackData: SnackData):
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute(
            f"UPDATE Snacks Set ItemName = '{newSnackData.snackName}', Quantity = {newSnackData.quantity}, ImageID = '{newSnackData.imageID}', PricePerItem = {newSnackData.pricePerItem} WHERE ItemID = {snackId}"
        )
        conn.commit()
        conn.close()

    def remove_patron(self, patronId: int):
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute(f"DELETE from Patrons WHERE PatronID = {patronId}")
        conn.commit()

        patronsTransactionIds = self.get_transaction_ids(patronId)
        for transactionId in patronsTransactionIds:
            self.remove_transaction_items(transactionId)
        self.remove_transactions(patronId)
        conn.close()

    def remove_snack(self, snackId: int):
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute(f"DELETE from Snacks WHERE ItemID = {snackId}")
        conn.commit()
        conn.close()

    def subtract_patron_credits(self, patronID: int, creditsToSubtract: float):
        patronData = self.get_patron_data(patronID=patronID)
        oldCreditsAmount = patronData.totalCredits
        newCreditsAmount = oldCreditsAmount - creditsToSubtract
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute(
            f"UPDATE Patrons Set TotalCredits = {newCreditsAmount} WHERE PatronID = {patronID}"
        )
        conn.commit()
        conn.close()

    def add_snack(self, itemName, quantity, imageID, pricePerItem):
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO Snacks (ItemName, Quantity, ImageID, PricePerItem)
            VALUES (?, ?, ?, ?)
            """,
            (itemName, quantity, imageID, pricePerItem),
        )
        conn.commit()
        conn.close()

    def get_snack(self, snackId: int) -> SnackData:
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM Snacks WHERE ItemID = {snackId}")
        sqlResult = cursor.fetchone()
        conn.close()
        return SnackData(
            snackId=sqlResult[0],
            snackName=sqlResult[1],
            quantity=sqlResult[2],
            imageID=sqlResult[3],
            pricePerItem=sqlResult[4],
        )

    def subtract_snack_quantity(self, snackId: int, quantity: int):
        snack = self.get_snack(snackId=snackId)
        oldQuantity = snack.quantity
        newQuantity = oldQuantity - quantity
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute(
            f"UPDATE Snacks Set Quantity = {newQuantity} WHERE ItemID = {snackId}"
        )
        conn.commit()
        conn.close()

    def get_all_snacks(self) -> list[SnackData]:
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Snacks")
        sqlResult = cursor.fetchall()
        snackDataList = [
            SnackData(
                snackEntry[0],
                snackEntry[1],
                snackEntry[2],
                snackEntry[3],
                snackEntry[4],
            )
            for snackEntry in sqlResult
        ]
        conn.close()
        return snackDataList

    def add_credits(self, userId: int, amount: float):
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute(f"SELECT TotalCredits FROM Patrons WHERE PatronID = {userId}")
        sqlResult = cursor.fetchone()
        currentCredits = float(sqlResult[0])
        newTotalCredits = currentCredits + amount
        cursor.execute(
            f"""
            UPDATE Patrons
            SET TotalCredits = {newTotalCredits}
            WHERE PatronID = {userId}
            """
        )
        conn.commit()
        conn.close()

    def get_patron_id_by_card_id(self, cardId: str) -> int:
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute(f"SELECT PatronID FROM Patrons WHERE EmployeeID = '{cardId}'")
        sqlResult = cursor.fetchone()
        conn.close()
        if sqlResult:
            return sqlResult[0]
        return None

    def close_database(self):
        self._connect().cursor().close()
