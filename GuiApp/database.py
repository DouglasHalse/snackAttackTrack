import sqlite3

def createPatreonTable():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Patrons (
        PatronID INTEGER PRIMARY KEY AUTOINCREMENT,
        FirstName TEXT NOT NULL,
        LastName TEXT NOT NULL,
        EmployeeID TEXT NOT NULL
    )
    """)
    conn.commit()

def addPatron(first_name, last_name, employee_id):
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO Patrons (FirstName, LastName, EmployeeID)
        VALUES (?, ?, ?)
        """, (first_name, last_name, employee_id))
    conn.commit()

def getAllPatrons():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Patrons")
    return cursor.fetchall()

def closeDatabase():
    sqlite3.connect("database.db").cursor().close()