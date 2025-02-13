import sqlite3
from enum import Enum
from datetime import datetime


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


def createAllTables():
    connection = sqlite3.connect("database.db")
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


def addPurchaseTransaction(
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

    conn = sqlite3.connect("database.db")
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


def addTopUpTransaction(
    patronID: int,
    amountBeforeTransaction: float,
    amountAfterTransaction: float,
    transactionDate: str,
):
    conn = sqlite3.connect("database.db")
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


def addEditTransaction(
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

    conn = sqlite3.connect("database.db")
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


def getTransactionItems(transactionID: int) -> list[SnackData]:
    conn = sqlite3.connect("database.db")
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
    return transactionItems


def removeTransactionItems(transactionID: int):
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute(
        f"DELETE FROM TransactionItems WHERE TransactionID = {transactionID}"
    )
    conn.commit()


def getTransactions(patronID: int):
    conn = sqlite3.connect("database.db")
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
        transactionItems = getTransactionItems(transactionID)
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


def getTransaction(transactionID: int) -> HistoryData:
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM Transactions WHERE TransactionID = {transactionID}")
    sqlResult = cursor.fetchone()
    transactionID = sqlResult[0]
    transactionType = TransactionType(sqlResult[1])
    transactionDate = sqlResult[3]
    amountBeforeTransaction = sqlResult[4]
    amountAfterTransaction = sqlResult[5]
    transactionItems = getTransactionItems(transactionID)
    parsedDatetime = datetime.strptime(transactionDate, "%Y-%m-%d %H:%M:%S.%f")
    return HistoryData(
        transactionID,
        transactionType,
        parsedDatetime,
        amountBeforeTransaction,
        amountAfterTransaction,
        transactionItems,
    )


def getTransactionIds(patronID: int):
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute(
        f"SELECT TransactionID FROM Transactions WHERE PatronID = {patronID}"
    )
    sqlResult = cursor.fetchall()
    transactionIds = []
    for transactionEntry in sqlResult:
        transactionIds.append(transactionEntry[0])
    return transactionIds


def removeTransactions(patronID: int):
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute(f"DELETE FROM Transactions WHERE PatronID = {patronID}")
    conn.commit()


def addPatron(first_name, last_name, employee_id):
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO Patrons (FirstName, LastName, EmployeeID)
        VALUES (?, ?, ?)
        """,
        (first_name, last_name, employee_id),
    )
    conn.commit()


def getAllPatrons() -> list[UserData]:
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Patrons")
    sqlResult = cursor.fetchall()
    userDataList = []
    for userEntry in sqlResult:
        patronId = userEntry[0]
        firstName = userEntry[1]
        lastName = userEntry[2]
        employeeID = userEntry[3]
        totalCredits = userEntry[4]
        userData = UserData(patronId, firstName, lastName, employeeID, totalCredits)
        userDataList.append(userData)
    return userDataList


def getPatronData(patronID: int) -> UserData:
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM Patrons WHERE PatronID = {patronID}")
    sqlResult = cursor.fetchone()
    patronId = sqlResult[0]
    firstName = sqlResult[1]
    lastName = sqlResult[2]
    employeeID = sqlResult[3]
    totalCredits = sqlResult[4]
    return UserData(patronId, firstName, lastName, employeeID, totalCredits)


def updatePatronData(patronId: int, newUserData: UserData):
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute(
        f"UPDATE Patrons Set FirstName = '{newUserData.firstName}', LastName = '{newUserData.lastName}', EmployeeID = '{newUserData.employeeID}', TotalCredits = {newUserData.totalCredits} WHERE PatronID = {patronId}"
    )
    conn.commit()


def updateSnackData(snackId: int, newSnackData: SnackData):
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute(
        f"UPDATE Snacks Set ItemName = '{newSnackData.snackName}', Quantity = {newSnackData.quantity}, ImageID = '{newSnackData.imageID}', PricePerItem = {newSnackData.pricePerItem} WHERE ItemID = {snackId}"
    )
    conn.commit()


def removePatron(patronId: int):
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute(f"DELETE from Patrons WHERE PatronID = {patronId}")
    conn.commit()

    patronsTransactionIds = getTransactionIds(patronId)
    for transactionId in patronsTransactionIds:
        removeTransactionItems(transactionId)
    removeTransactions(patronId)


def removeSnack(snackId: int):
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute(f"DELETE from Snacks WHERE ItemID = {snackId}")
    conn.commit()


def subtractPatronCredits(patronID: int, creditsToSubtract: float):
    patronData = getPatronData(patronID=patronID)
    oldCreditsAmount = patronData.totalCredits
    newCreditsAmount = oldCreditsAmount - creditsToSubtract
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute(
        f"UPDATE Patrons Set TotalCredits = {newCreditsAmount} WHERE PatronID = {patronID}"
    )
    conn.commit()


def addSnack(itemName, quantity, imageID, pricePerItem):
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO Snacks (ItemName, Quantity, ImageID, PricePerItem)
        VALUES (?, ?, ?, ?)
        """,
        (itemName, quantity, imageID, pricePerItem),
    )
    conn.commit()


def getSnack(snackId: int) -> SnackData:
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM Snacks WHERE ItemID = {snackId}")
    sqlResult = cursor.fetchone()
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


def subtractSnackQuantity(snackId: int, quantity: int):
    snack = getSnack(snackId=snackId)
    oldQuantity = snack.quantity
    newQuantity = oldQuantity - quantity
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute(
        f"UPDATE Snacks Set Quantity = {newQuantity} WHERE ItemID = {snackId}"
    )
    conn.commit()


def getAllSnacks() -> list[SnackData]:
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Snacks")
    sqlResult = cursor.fetchall()
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


def addCredits(userId: int, amount: float):
    conn = sqlite3.connect("database.db")
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


def getPatronIdByCardId(cardId: str) -> int:
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute(f"SELECT PatronID FROM Patrons WHERE EmployeeID = '{cardId}'")
    sqlResult = cursor.fetchone()
    if sqlResult:
        return sqlResult[0]
    return None


def closeDatabase():
    sqlite3.connect("database.db").cursor().close()
