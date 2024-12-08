import sqlite3


class UserData:
    def __init__(self, patronId, firstName, lastName, employeeID, totalCredits):
        self.patronId = patronId
        self.firstName = firstName
        self.lastName = lastName
        self.employeeID = employeeID
        self.totalCredits = totalCredits


class SnackData:
    def __init__(self, snackId, snackName, quantity, imageID, pricePerItem):
        self.snackId = snackId
        self.snackName = snackName
        self.quantity = quantity
        self.imageID = imageID
        self.pricePerItem = pricePerItem


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
            TotalCredits INTEGER NOT NULL DEFAULT 0
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
        CREATE TABLE IF NOT EXISTS Payments (
            PatronID INTEGER PRIMARY KEY, 
            TransactionDate TEXT NOT NULL, 
            AmountBeforeTransaction REAL NOT NULL, 
            AmountAfterTransaction REAL NOT NULL
        );
        """,
    ]

    for query in create_queries:
        cursor.execute(query)

    connection.commit()


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


def closeDatabase():
    sqlite3.connect("database.db").cursor().close()
