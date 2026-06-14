"""
Seed a test database for performance testing.

Creates a rich database with:
  - 20 users (long first/last names)
  - 15 snacks
  - ~5 transactions per user (top-up + purchase)
  - 3 added-snack records
  - 2 lost-snack records

Usage:
    python scripts/seed_perf_db.py [--output PATH]
"""

import argparse
import os
import sys
import tempfile
from datetime import datetime, timedelta

sys.path.insert(
    0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "GuiApp")
)

# pylint: disable=wrong-import-position,wrong-import-order
from app_types import Credits, SnackData, LostSnackReason  # noqa: E402
from database import DatabaseConnector  # noqa: E402


LONG_FIRST_NAMES = [
    "Alexandria",
    "Bartholomew",
    "Christabella",
    "Demetrianne",
    "Evangelista",
    "Frederickson",
    "Giovannabeth",
    "Henriettalyn",
    "Isabellandra",
    "Jacquelinette",
    "Katherinelle",
    "Lysandrianna",
    "Maximillianne",
    "Nicolasandro",
    "Ophelianette",
    "Persephonique",
    "Quintessandra",
    "Roderickson",
    "Sebastianelle",
    "Theodosianne",
]

LONG_LAST_NAMES = [
    "Applethwaite",
    "Bramblethorn",
    "Chestertonville",
    "Davenportshire",
    "Eppingforest",
    "Fotheringhaycastle",
    "Gillinghamworth",
    "Hatherleighforge",
    "Inkpennington",
    "Jollywaggoners",
    "Kingsbridgewater",
    "Loughboroughjunction",
    "Micklethwaite",
    "Netherwallopton",
    "Ogglethorpestone",
    "Puddlecoteville",
    "Quickenhampton",
    "Rotherhithedock",
    "Snodgrassington",
    "Tiddlywinkshire",
]

SNACKS = [
    ("Chips", 40, "img_chips", Credits("1.50")),
    ("Chocolate Bar", 25, "img_choc", Credits("2.00")),
    ("Granola Bar", 30, "img_granola", Credits("1.25")),
    ("Pretzels", 35, "img_pretzel", Credits("1.75")),
    ("Popcorn", 20, "img_popcorn", Credits("1.50")),
    ("Gummy Bears", 15, "img_gummy", Credits("1.00")),
    ("Trail Mix", 22, "img_trail", Credits("2.50")),
    ("Crackers", 28, "img_cracker", Credits("1.25")),
    ("Cookies", 18, "img_cookie", Credits("2.00")),
    ("Beef Jerky", 12, "img_jerky", Credits("3.00")),
    ("Mixed Nuts", 16, "img_nuts", Credits("2.50")),
    ("Rice Cakes", 20, "img_rice", Credits("1.00")),
    ("Fruit Snacks", 24, "img_fruit", Credits("1.25")),
    ("Protein Bar", 30, "img_protein", Credits("2.75")),
    ("Dark Chocolate", 10, "img_dark", Credits("3.50")),
]

EMPLOYEE_IDS = [f"EMP{i:08d}" for i in range(1000, 1020)]


def create_database(db_path: str) -> DatabaseConnector:
    """Create and populate the test database. Returns the connector."""
    if os.path.exists(db_path):
        os.remove(db_path)

    db = DatabaseConnector(database_path=db_path)

    for i in range(20):
        db.addPatron(
            first_name=LONG_FIRST_NAMES[i],
            last_name=LONG_LAST_NAMES[i],
            employee_id=EMPLOYEE_IDS[i],
        )
        db.addCredits(userId=i + 1, amount=Credits(f"{i * 5 + 10}.00"))

    for name, qty, img, price in SNACKS:
        db.addSnack(name, qty, img, price)

    base_date = datetime.now() - timedelta(days=30)
    for patron_id in range(1, 11):
        db.addTopUpTransaction(
            patronID=patron_id,
            amountBeforeTransaction=Credits("0.00"),
            amountAfterTransaction=Credits(f"{patron_id * 5 + 10}.00"),
            transactionDate=base_date,
        )
        for week in range(4):
            date = base_date + timedelta(days=week * 7)
            items = [
                SnackData(
                    snackId=(week % 15) + 1,
                    snackName=SNACKS[week % 15][0],
                    quantity=1,
                    imageID=SNACKS[week % 15][2],
                    pricePerItem=SNACKS[week % 15][3],
                )
            ]
            before = Credits(f"{max(5, patron_id * 5 + 10 - week * 2)}.00")
            after = Credits(
                f"{max(3, patron_id * 5 + 10 - week * 2 - (week % 15 + 1))}.00"
            )
            db.addPurchaseTransaction(
                patronID=patron_id,
                amountBeforeTransaction=before,
                amountAfterTransaction=after,
                transactionDate=date,
                transactionItems=items,
            )
        mid_date = base_date + timedelta(days=14)
        before = Credits(f"{max(2, patron_id * 3)}.00")
        after = Credits(f"{max(2, patron_id * 3) + 10}.00")
        db.addTopUpTransaction(
            patronID=patron_id,
            amountBeforeTransaction=before,
            amountAfterTransaction=after,
            transactionDate=mid_date,
        )

    for i in range(3):
        db.add_added_snack(
            snack_name=SNACKS[i][0],
            quantity=10 + i * 5,
            value=SNACKS[i][3] * (10 + i * 5),
        )
    for i in range(2):
        db.add_lost_snack(
            snack_name=SNACKS[i + 3][0],
            reason=LostSnackReason.STOLEN if i == 0 else LostSnackReason.EXPIRED,
            quantity=2,
            total_value=SNACKS[i + 3][3] * 2,
        )

    return db


def main():
    parser = argparse.ArgumentParser(description="Seed performance test database")
    parser.add_argument(
        "--output", type=str, default=None, help="Path to write the database"
    )
    args = parser.parse_args()

    db_path = args.output or os.path.join(tempfile.gettempdir(), "perf_test_seed.db")
    print(f"Creating seed database at: {db_path}")
    db = create_database(db_path)
    patrons = db.getAllPatrons()
    snacks = db.getAllSnacks()
    tx_count = sum(len(db.getTransactions(p.patronId)) for p in patrons)
    print(f"  Patrons: {len(patrons)}, Snacks: {len(snacks)}, Transactions: {tx_count}")
    print(
        f"  Added snacks: {db.get_total_snacks_added()}, Lost snacks: {db.get_total_snacks_lost()}"
    )
    db.close()


if __name__ == "__main__":
    main()
