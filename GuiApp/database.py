import sqlite3


class UserData:
    def __init__(self, patronId, firstName, lastName, employeeID):
        self.patronId = patronId
        self.firstName = firstName
        self.lastName = lastName
        self.employeeID = employeeID


def createAllTables():
    connection = sqlite3.connect("database.db")
    cursor = connection.cursor()

    create_queries = [
        """
        CREATE TABLE IF NOT EXISTS Patrons (
            PatronID INTEGER PRIMARY KEY AUTOINCREMENT,
            FirstName TEXT NOT NULL,
            LastName TEXT NOT NULL,
            EmployeeID TEXT NOT NULL
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS Snacks (
            ItemID INTEGER PRIMARY KEY AUTOINCREMENT,
            ItemName TEXT NOT NULL,
            Quantity INTEGER NOT NULL,
            ImageID TEXT NOT NULL
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
        userData = UserData(patronId, firstName, lastName, employeeID)
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
    return UserData(patronId, firstName, lastName, employeeID)


def closeDatabase():
    sqlite3.connect("database.db").cursor().close()
