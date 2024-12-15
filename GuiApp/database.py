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
        self.snackId: int = snackId
        self.snackName: str = snackName
        self.quantity: int = quantity
        self.imageID: str = imageID
        self.pricePerItem: float = pricePerItem


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


def updatePatronData(patronId: int, newUserData: UserData):
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute(
        f"UPDATE Patrons Set FirstName = '{newUserData.firstName}', LastName = '{newUserData.lastName}', EmployeeID = {newUserData.employeeID}, TotalCredits = {newUserData.totalCredits} WHERE PatronID = {patronId}"
    )
    conn.commit()


def removePatron(patronId: int):
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute(f"DELETE from Patrons WHERE PatronID = {patronId}")
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


def removeSnack(snackId: int):
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute(f"DELETE FROM Snacks WHERE ItemID = {snackId}")
    conn.commit()


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


def closeDatabase():
    sqlite3.connect("database.db").cursor().close()
