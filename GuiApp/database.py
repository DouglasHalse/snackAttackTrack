import sqlite3


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


def getAllPatrons():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Patrons")
    return cursor.fetchall()


def closeDatabase():
    sqlite3.connect("database.db").cursor().close()
