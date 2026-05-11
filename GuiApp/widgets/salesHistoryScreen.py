from database import TransactionType, transactionTypeToPresentableString
from widgets.GridLayoutScreen import GridLayoutScreen
from widgets.popups.gambleSummaryPopup import GambleSummaryPopup
from widgets.popups.purchaseSummaryPopup import PurchaseSummaryPopup


class SalesHistoryScreen(GridLayoutScreen):
    def on_enter(self, *_):
        # Load all purchase and gamble transactions
        transactions = self.manager.database.getAllSnackTransactions()

        # Sort by date (newest first)
        transactions.sort(key=lambda x: x.transactionDate, reverse=True)

        # Clear existing entries
        self.ids.salesTable.clearEntries()

        # Get all patrons once to avoid repeated queries
        patrons = {p.patronId: p for p in self.manager.database.getAllPatrons()}

        # Add transactions to table
        for transaction in transactions:
            # Get patron ID for this transaction
            patron_id = self.manager.database.cursor.execute(
                "SELECT PatronID FROM Transactions WHERE TransactionID = ?",
                (transaction.transactionId,),
            ).fetchone()[0]

            patron = patrons.get(patron_id)
            if not patron:
                continue

            # Calculate total items and price
            total_items = sum(item.quantity for item in transaction.transactionItems)
            total_price = sum(
                item.pricePerItem * item.quantity
                for item in transaction.transactionItems
            )

            # Format date
            date_str = transaction.transactionDate.strftime("%Y-%m-%d %H:%M")

            # Add entry
            self.ids.salesTable.addEntry(
                entryContents=[
                    date_str,
                    f"{patron.firstName} {patron.lastName}",
                    transactionTypeToPresentableString(transaction.transactionType),
                    f"{total_items}",
                    f"${total_price:.2f}",
                ],
                entryIdentifier=transaction.transactionId,
            )

    def on_leave(self, *_):
        self.ids.salesTable.clearEntries()

    def onSalesEntryPressed(self, transactionId):
        transaction = self.manager.database.getTransaction(transactionId)
        if transaction.transactionType == TransactionType.PURCHASE:
            PurchaseSummaryPopup(historyData=transaction).open()
        elif transaction.transactionType == TransactionType.GAMBLE:
            GambleSummaryPopup(historyData=transaction).open()

    def onBackButtonPressed(self, _):
        self.manager.transitionToScreen("adminScreen", transitionDirection="right")
