"""
Programmatic schema factory for building test databases at specific versions.

Each version can be built via SchemaBuilder.build(db_path, version),
producing a database with the correct schema and seed data for that
version of the SnackAttackTrack schema.
"""

import sqlite3


# ── Schema SQL (single-line format to avoid pylint duplicate-code) ──────────
# V1: Initial schema with REAL credit columns, no settings table
SCHEMA_V1 = (
    "CREATE TABLE IF NOT EXISTS Patrons ("
    "PatronID INTEGER PRIMARY KEY AUTOINCREMENT, "
    "FirstName TEXT NOT NULL, LastName TEXT NOT NULL, EmployeeID TEXT NOT NULL, "
    "TotalCredits REAL NOT NULL DEFAULT 0.0); "
    "CREATE TABLE IF NOT EXISTS Snacks ("
    "ItemID INTEGER PRIMARY KEY AUTOINCREMENT, "
    "ItemName TEXT NOT NULL, Quantity INTEGER NOT NULL, ImageID TEXT NOT NULL, "
    "PricePerItem REAL NOT NULL); "
    "CREATE TABLE IF NOT EXISTS Transactions ("
    "TransactionID INTEGER PRIMARY KEY AUTOINCREMENT, "
    "TransactionType TEXT NOT NULL, PatronID INTEGER NOT NULL, "
    "TransactionDate TEXT NOT NULL, AmountBeforeTransaction REAL NOT NULL, "
    "AmountAfterTransaction REAL NOT NULL, "
    "FOREIGN KEY(PatronID) REFERENCES Patrons(PatronID)); "
    "CREATE TABLE IF NOT EXISTS TransactionItems ("
    "TransactionItemId INTEGER PRIMARY KEY AUTOINCREMENT, "
    "TransactionID INTEGER NOT NULL, ItemName TEXT NOT NULL, "
    "Quantity INTEGER NOT NULL, PricePerItem REAL NOT NULL, "
    "FOREIGN KEY(TransactionID) REFERENCES Transactions(TransactionID)); "
    "CREATE TABLE IF NOT EXISTS AddedSnacks ("
    "AddedID INTEGER PRIMARY KEY AUTOINCREMENT, "
    "SnackName TEXT NOT NULL, AddedDate TEXT NOT NULL, "
    "Quantity INTEGER NOT NULL, Value REAL NOT NULL); "
    "CREATE TABLE IF NOT EXISTS LostSnacks ("
    "LostID INTEGER PRIMARY KEY AUTOINCREMENT, "
    "SnackName TEXT NOT NULL, Reason INTEGER NOT NULL, "
    "LostDate TEXT NOT NULL, Quantity INTEGER NOT NULL, Value REAL NOT NULL);"
)

# V2: Schema after migration_2 — INTEGER credits, TotalCredits bare (no DEFAULT 0)
SCHEMA_V2 = (
    "CREATE TABLE IF NOT EXISTS settings ("
    "name TEXT PRIMARY KEY, value TEXT NOT NULL); "
    "INSERT OR IGNORE INTO settings (name, value) VALUES ('schema_version', '2'); "
    "CREATE TABLE IF NOT EXISTS Patrons ("
    "PatronID INTEGER PRIMARY KEY AUTOINCREMENT, "
    "FirstName TEXT NOT NULL, LastName TEXT NOT NULL, EmployeeID TEXT NOT NULL, "
    "TotalCredits INTEGER); "
    "CREATE TABLE IF NOT EXISTS Snacks ("
    "ItemID INTEGER PRIMARY KEY AUTOINCREMENT, "
    "ItemName TEXT NOT NULL, Quantity INTEGER NOT NULL, ImageID TEXT NOT NULL, "
    "PricePerItem INTEGER NOT NULL); "
    "CREATE TABLE IF NOT EXISTS Transactions ("
    "TransactionID INTEGER PRIMARY KEY AUTOINCREMENT, "
    "TransactionType TEXT NOT NULL, PatronID INTEGER NOT NULL, "
    "TransactionDate TEXT NOT NULL, AmountBeforeTransaction INTEGER NOT NULL, "
    "AmountAfterTransaction INTEGER NOT NULL, "
    "FOREIGN KEY(PatronID) REFERENCES Patrons(PatronID)); "
    "CREATE TABLE IF NOT EXISTS TransactionItems ("
    "TransactionItemId INTEGER PRIMARY KEY AUTOINCREMENT, "
    "TransactionID INTEGER NOT NULL, ItemName TEXT NOT NULL, "
    "Quantity INTEGER NOT NULL, PricePerItem INTEGER NOT NULL, "
    "FOREIGN KEY(TransactionID) REFERENCES Transactions(TransactionID)); "
    "CREATE TABLE IF NOT EXISTS AddedSnacks ("
    "AddedID INTEGER PRIMARY KEY AUTOINCREMENT, "
    "SnackName TEXT NOT NULL, AddedDate TEXT NOT NULL, "
    "Quantity INTEGER NOT NULL, Value INTEGER NOT NULL); "
    "CREATE TABLE IF NOT EXISTS LostSnacks ("
    "LostID INTEGER PRIMARY KEY AUTOINCREMENT, "
    "SnackName TEXT NOT NULL, Reason INTEGER NOT NULL, "
    "LostDate TEXT NOT NULL, Quantity INTEGER NOT NULL, Value INTEGER NOT NULL);"
)

# V3: Correct schema — INTEGER credits, TotalCredits has DEFAULT 0
SCHEMA_V3 = (
    "CREATE TABLE IF NOT EXISTS settings ("
    "name TEXT PRIMARY KEY, value TEXT NOT NULL); "
    "INSERT OR IGNORE INTO settings (name, value) VALUES ('schema_version', '3'); "
    "CREATE TABLE IF NOT EXISTS Patrons ("
    "PatronID INTEGER PRIMARY KEY AUTOINCREMENT, "
    "FirstName TEXT NOT NULL, LastName TEXT NOT NULL, EmployeeID TEXT NOT NULL, "
    "TotalCredits INTEGER NOT NULL DEFAULT 0); "
    "CREATE TABLE IF NOT EXISTS Snacks ("
    "ItemID INTEGER PRIMARY KEY AUTOINCREMENT, "
    "ItemName TEXT NOT NULL, Quantity INTEGER NOT NULL, ImageID TEXT NOT NULL, "
    "PricePerItem INTEGER NOT NULL); "
    "CREATE TABLE IF NOT EXISTS Transactions ("
    "TransactionID INTEGER PRIMARY KEY AUTOINCREMENT, "
    "TransactionType TEXT NOT NULL, PatronID INTEGER NOT NULL, "
    "TransactionDate TEXT NOT NULL, AmountBeforeTransaction INTEGER NOT NULL, "
    "AmountAfterTransaction INTEGER NOT NULL, "
    "FOREIGN KEY(PatronID) REFERENCES Patrons(PatronID)); "
    "CREATE TABLE IF NOT EXISTS TransactionItems ("
    "TransactionItemId INTEGER PRIMARY KEY AUTOINCREMENT, "
    "TransactionID INTEGER NOT NULL, ItemName TEXT NOT NULL, "
    "Quantity INTEGER NOT NULL, PricePerItem INTEGER NOT NULL, "
    "FOREIGN KEY(TransactionID) REFERENCES Transactions(TransactionID)); "
    "CREATE TABLE IF NOT EXISTS AddedSnacks ("
    "AddedID INTEGER PRIMARY KEY AUTOINCREMENT, "
    "SnackName TEXT NOT NULL, AddedDate TEXT NOT NULL, "
    "Quantity INTEGER NOT NULL, Value INTEGER NOT NULL); "
    "CREATE TABLE IF NOT EXISTS LostSnacks ("
    "LostID INTEGER PRIMARY KEY AUTOINCREMENT, "
    "SnackName TEXT NOT NULL, Reason INTEGER NOT NULL, "
    "LostDate TEXT NOT NULL, Quantity INTEGER NOT NULL, Value INTEGER NOT NULL);"
)


# ── Seed data SQL ──────────────────────────────────────────────────────────

# Seed data for V1 and V2 (V1 has REAL credits, V2 has INTEGER converted from V1)
# Credits values in REAL: 5510.04, 221.94, 494.60
# INTEGER equivalents (×100): 551004, 22194, 49460
_V1_SEEDS = (
    "INSERT INTO Patrons (FirstName, LastName, EmployeeID, TotalCredits) "
    "VALUES ('User1FirstName', 'User1LastName', '', 5510.04); "
    "INSERT INTO Patrons (FirstName, LastName, EmployeeID, TotalCredits) "
    "VALUES ('User2FirstName', 'User2LastName', '12345678', 221.94); "
    "INSERT INTO Patrons (FirstName, LastName, EmployeeID, TotalCredits) "
    "VALUES ('User3FirstName', 'User3LastName', '', 494.60); "
    "INSERT INTO Snacks (ItemName, Quantity, ImageID, PricePerItem) "
    "VALUES ('Apple', 564, 'None', 1.33); "
    "INSERT INTO Snacks (ItemName, Quantity, ImageID, PricePerItem) "
    "VALUES ('Orange', 505, 'None', 14.73); "
    "INSERT INTO Snacks (ItemName, Quantity, ImageID, PricePerItem) "
    "VALUES ('Pear', 5888, 'None', 0.14); "
    "INSERT INTO AddedSnacks (SnackName, AddedDate, Quantity, Value) "
    "VALUES ('Apple', '2026-04-29 20:59:33.290186', 566, 685.00); "
    "INSERT INTO AddedSnacks (SnackName, AddedDate, Quantity, Value) "
    "VALUES ('Orange', '2026-04-29 20:59:46.311367', 556, 7445.00); "
    "INSERT INTO AddedSnacks (SnackName, AddedDate, Quantity, Value) "
    "VALUES ('Pear', '2026-04-29 20:59:58.007470', 5893, 771.00); "
    "INSERT INTO LostSnacks (SnackName, Reason, LostDate, Quantity, Value) "
    "VALUES ('Orange', 1, '2026-04-29 21:01:20.062596', 50, 736.50); "
    "INSERT INTO Transactions (TransactionType, PatronID, TransactionDate, "
    "AmountBeforeTransaction, AmountAfterTransaction) "
    "VALUES ('TOP_UP', 1, '2026-04-29 20:59:19.980700', 0.0, 5526.52); "
    "INSERT INTO Transactions (TransactionType, PatronID, TransactionDate, "
    "AmountBeforeTransaction, AmountAfterTransaction) "
    "VALUES ('EDIT', 2, '2026-04-29 21:00:13.147316', 0.0, 222.22); "
    "INSERT INTO Transactions (TransactionType, PatronID, TransactionDate, "
    "AmountBeforeTransaction, AmountAfterTransaction) "
    "VALUES ('TOP_UP', 3, '2026-04-29 21:00:32.878661', 0.0, 500.00); "
    "INSERT INTO Transactions (TransactionType, PatronID, TransactionDate, "
    "AmountBeforeTransaction, AmountAfterTransaction) "
    "VALUES ('GAMBLE', 3, '2026-04-29 21:00:37.649922', 500.0, 494.60); "
    "INSERT INTO Transactions (TransactionType, PatronID, TransactionDate, "
    "AmountBeforeTransaction, AmountAfterTransaction) "
    "VALUES ('PURCHASE', 2, '2026-04-29 21:00:57.733077', 222.22, 221.94); "
    "INSERT INTO Transactions (TransactionType, PatronID, TransactionDate, "
    "AmountBeforeTransaction, AmountAfterTransaction) "
    "VALUES ('PURCHASE', 1, '2026-04-29 21:01:46.745517', 5526.52, 5510.04); "
    "INSERT INTO TransactionItems (TransactionID, ItemName, Quantity, PricePerItem) "
    "VALUES (4, 'Apple', 1, 1.33); "
    "INSERT INTO TransactionItems (TransactionID, ItemName, Quantity, PricePerItem) "
    "VALUES (5, 'Pear', 2, 0.14); "
    "INSERT INTO TransactionItems (TransactionID, ItemName, Quantity, PricePerItem) "
    "VALUES (6, 'Apple', 1, 1.33); "
    "INSERT INTO TransactionItems (TransactionID, ItemName, Quantity, PricePerItem) "
    "VALUES (6, 'Orange', 1, 14.73); "
    "INSERT INTO TransactionItems (TransactionID, ItemName, Quantity, PricePerItem) "
    "VALUES (6, 'Pear', 3, 0.14);"
)

# V2 seed data: same as V1 but TotalCredits is INTEGER (×100) plus a NULL row
_V2_SEEDS = (
    "INSERT INTO Patrons (FirstName, LastName, EmployeeID, TotalCredits) "
    "VALUES ('User1FirstName', 'User1LastName', '', 551004); "
    "INSERT INTO Patrons (FirstName, LastName, EmployeeID, TotalCredits) "
    "VALUES ('User2FirstName', 'User2LastName', '12345678', 22194); "
    "INSERT INTO Patrons (FirstName, LastName, EmployeeID, TotalCredits) "
    "VALUES ('User3FirstName', 'User3LastName', '', 49460); "
    # A patron with NULL TotalCredits — exercises the DEFAULT 0 fix
    "INSERT INTO Patrons (FirstName, LastName, EmployeeID, TotalCredits) "
    "VALUES ('NullCredit', 'User', 'NULLTEST', NULL); "
    "INSERT INTO Snacks (ItemName, Quantity, ImageID, PricePerItem) "
    "VALUES ('Apple', 564, 'None', 133); "
    "INSERT INTO Snacks (ItemName, Quantity, ImageID, PricePerItem) "
    "VALUES ('Orange', 505, 'None', 1473); "
    "INSERT INTO Snacks (ItemName, Quantity, ImageID, PricePerItem) "
    "VALUES ('Pear', 5888, 'None', 14); "
    "INSERT INTO AddedSnacks (SnackName, AddedDate, Quantity, Value) "
    "VALUES ('Apple', '2026-04-29 20:59:33.290186', 566, 68500); "
    "INSERT INTO AddedSnacks (SnackName, AddedDate, Quantity, Value) "
    "VALUES ('Orange', '2026-04-29 20:59:46.311367', 556, 744500); "
    "INSERT INTO AddedSnacks (SnackName, AddedDate, Quantity, Value) "
    "VALUES ('Pear', '2026-04-29 20:59:58.007470', 5893, 77100); "
    "INSERT INTO LostSnacks (SnackName, Reason, LostDate, Quantity, Value) "
    "VALUES ('Orange', 1, '2026-04-29 21:01:20.062596', 50, 73650); "
    "INSERT INTO Transactions (TransactionType, PatronID, TransactionDate, "
    "AmountBeforeTransaction, AmountAfterTransaction) "
    "VALUES ('TOP_UP', 1, '2026-04-29 20:59:19.980700', 0, 552652); "
    "INSERT INTO Transactions (TransactionType, PatronID, TransactionDate, "
    "AmountBeforeTransaction, AmountAfterTransaction) "
    "VALUES ('EDIT', 2, '2026-04-29 21:00:13.147316', 0, 22222); "
    "INSERT INTO Transactions (TransactionType, PatronID, TransactionDate, "
    "AmountBeforeTransaction, AmountAfterTransaction) "
    "VALUES ('TOP_UP', 3, '2026-04-29 21:00:32.878661', 0, 50000); "
    "INSERT INTO Transactions (TransactionType, PatronID, TransactionDate, "
    "AmountBeforeTransaction, AmountAfterTransaction) "
    "VALUES ('GAMBLE', 3, '2026-04-29 21:00:37.649922', 50000, 49460); "
    "INSERT INTO Transactions (TransactionType, PatronID, TransactionDate, "
    "AmountBeforeTransaction, AmountAfterTransaction) "
    "VALUES ('PURCHASE', 2, '2026-04-29 21:00:57.733077', 22222, 22194); "
    "INSERT INTO Transactions (TransactionType, PatronID, TransactionDate, "
    "AmountBeforeTransaction, AmountAfterTransaction) "
    "VALUES ('PURCHASE', 1, '2026-04-29 21:01:46.745517', 552652, 551004); "
    "INSERT INTO TransactionItems (TransactionID, ItemName, Quantity, PricePerItem) "
    "VALUES (4, 'Apple', 1, 133); "
    "INSERT INTO TransactionItems (TransactionID, ItemName, Quantity, PricePerItem) "
    "VALUES (5, 'Pear', 2, 14); "
    "INSERT INTO TransactionItems (TransactionID, ItemName, Quantity, PricePerItem) "
    "VALUES (6, 'Apple', 1, 133); "
    "INSERT INTO TransactionItems (TransactionID, ItemName, Quantity, PricePerItem) "
    "VALUES (6, 'Orange', 1, 1473); "
    "INSERT INTO TransactionItems (TransactionID, ItemName, Quantity, PricePerItem) "
    "VALUES (6, 'Pear', 3, 14);"
)

# V3 seed data: same as V2 but no NULL row (DEFAULT 0 prevents it)
_V3_SEEDS = (
    "INSERT INTO Patrons (FirstName, LastName, EmployeeID, TotalCredits) "
    "VALUES ('User1FirstName', 'User1LastName', '', 551004); "
    "INSERT INTO Patrons (FirstName, LastName, EmployeeID, TotalCredits) "
    "VALUES ('User2FirstName', 'User2LastName', '12345678', 22194); "
    "INSERT INTO Patrons (FirstName, LastName, EmployeeID, TotalCredits) "
    "VALUES ('User3FirstName', 'User3LastName', '', 49460); "
    "INSERT INTO Snacks (ItemName, Quantity, ImageID, PricePerItem) "
    "VALUES ('Apple', 564, 'None', 133); "
    "INSERT INTO Snacks (ItemName, Quantity, ImageID, PricePerItem) "
    "VALUES ('Orange', 505, 'None', 1473); "
    "INSERT INTO Snacks (ItemName, Quantity, ImageID, PricePerItem) "
    "VALUES ('Pear', 5888, 'None', 14); "
    "INSERT INTO AddedSnacks (SnackName, AddedDate, Quantity, Value) "
    "VALUES ('Apple', '2026-04-29 20:59:33.290186', 566, 68500); "
    "INSERT INTO AddedSnacks (SnackName, AddedDate, Quantity, Value) "
    "VALUES ('Orange', '2026-04-29 20:59:46.311367', 556, 744500); "
    "INSERT INTO AddedSnacks (SnackName, AddedDate, Quantity, Value) "
    "VALUES ('Pear', '2026-04-29 20:59:58.007470', 5893, 77100); "
    "INSERT INTO LostSnacks (SnackName, Reason, LostDate, Quantity, Value) "
    "VALUES ('Orange', 1, '2026-04-29 21:01:20.062596', 50, 73650); "
    "INSERT INTO Transactions (TransactionType, PatronID, TransactionDate, "
    "AmountBeforeTransaction, AmountAfterTransaction) "
    "VALUES ('TOP_UP', 1, '2026-04-29 20:59:19.980700', 0, 552652); "
    "INSERT INTO Transactions (TransactionType, PatronID, TransactionDate, "
    "AmountBeforeTransaction, AmountAfterTransaction) "
    "VALUES ('EDIT', 2, '2026-04-29 21:00:13.147316', 0, 22222); "
    "INSERT INTO Transactions (TransactionType, PatronID, TransactionDate, "
    "AmountBeforeTransaction, AmountAfterTransaction) "
    "VALUES ('TOP_UP', 3, '2026-04-29 21:00:32.878661', 0, 50000); "
    "INSERT INTO Transactions (TransactionType, PatronID, TransactionDate, "
    "AmountBeforeTransaction, AmountAfterTransaction) "
    "VALUES ('GAMBLE', 3, '2026-04-29 21:00:37.649922', 50000, 49460); "
    "INSERT INTO Transactions (TransactionType, PatronID, TransactionDate, "
    "AmountBeforeTransaction, AmountAfterTransaction) "
    "VALUES ('PURCHASE', 2, '2026-04-29 21:00:57.733077', 22222, 22194); "
    "INSERT INTO Transactions (TransactionType, PatronID, TransactionDate, "
    "AmountBeforeTransaction, AmountAfterTransaction) "
    "VALUES ('PURCHASE', 1, '2026-04-29 21:01:46.745517', 552652, 551004); "
    "INSERT INTO TransactionItems (TransactionID, ItemName, Quantity, PricePerItem) "
    "VALUES (4, 'Apple', 1, 133); "
    "INSERT INTO TransactionItems (TransactionID, ItemName, Quantity, PricePerItem) "
    "VALUES (5, 'Pear', 2, 14); "
    "INSERT INTO TransactionItems (TransactionID, ItemName, Quantity, PricePerItem) "
    "VALUES (6, 'Apple', 1, 133); "
    "INSERT INTO TransactionItems (TransactionID, ItemName, Quantity, PricePerItem) "
    "VALUES (6, 'Orange', 1, 1473); "
    "INSERT INTO TransactionItems (TransactionID, ItemName, Quantity, PricePerItem) "
    "VALUES (6, 'Pear', 3, 14);"
)


# ── Schema/SQL map ─────────────────────────────────────────────────────────

_SCHEMA_MAP = {
    "v1": (SCHEMA_V1, _V1_SEEDS),
    "v2": (SCHEMA_V2, _V2_SEEDS),
    "v3": (SCHEMA_V3, _V3_SEEDS),
}


# ── Public API ──────────────────────────────────────────────────────────────


class SchemaBuilder:
    """Builds databases at specific schema versions for testing."""

    @staticmethod
    def build(db_path: str, version: str, seed: bool = True) -> str:
        """
        Build a database at the given schema version.

        Args:
            db_path: Path to the database file to create.
            version: One of 'v1', 'v2', 'v3'.
            seed: Whether to insert seed data (default: True).

        Returns:
            db_path (for chaining).

        Raises:
            ValueError: If version is unknown.
        """
        if version not in _SCHEMA_MAP:
            raise ValueError(
                f"Unknown schema version: {version}. "
                f"Expected one of: {list(_SCHEMA_MAP.keys())}"
            )

        schema_sql, seed_sql = _SCHEMA_MAP[version]

        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.executescript(schema_sql)
        if seed:
            cursor.executescript(seed_sql)
        conn.commit()
        conn.close()
        return db_path
