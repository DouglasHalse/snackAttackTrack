from database import (
    TransactionType,
    getTransaction,
    getTransactions,
    transactionTypeToPresentableString,
)
from widgets.GridLayoutScreen import GridLayoutScreen
from widgets.popups.editSummaryPopup import EditSummaryPopup
from widgets.popups.gambleSummaryPopup import GambleSummaryPopup
from widgets.popups.purchaseSummaryPopup import PurchaseSummaryPopup
from widgets.popups.topUpSummaryPopup import TopUpSummaryPopup


class HistoryScreen(GridLayoutScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.ids.header.bind(on_back_button_pressed=self.on_back_button_pressed)

    def on_back_button_pressed(self, *args):
        self.manager.transitionToScreen("profileScreen", transitionDirection="right")

    def on_pre_enter(self, *args):
        currentPatron = self.manager.getCurrentPatron()
        transactions = getTransactions(currentPatron.patronId)

        # Redorder transactions so that the most recent transactions are at the top
        transactions = sorted(
            transactions, key=lambda x: x.transactionDate, reverse=True
        )

        for transaction in transactions:
            self.ids.historyTable.addEntry(
                entryContents=[
                    transaction.transactionDate.strftime("%Y-%m-%d %H:%M:%S"),
                    f"{transaction.amountBeforeTransaction:.2f}",
                    f"{transaction.amountAfterTransaction:.2f}",
                    transactionTypeToPresentableString(transaction.transactionType),
                ],
                entryIdentifier=transaction.transactionId,
            )
        return super().on_pre_enter(*args)

    def on_leave(self, *args):
        self.ids.historyTable.clearEntries()

    def onHistoryEntryPressed(self, transactionId):
        transaction = getTransaction(transactionId)
        if transaction.transactionType == TransactionType.PURCHASE:
            PurchaseSummaryPopup(historyData=transaction).open()
        elif transaction.transactionType == TransactionType.EDIT:
            EditSummaryPopup(historyData=transaction).open()
        elif transaction.transactionType == TransactionType.TOP_UP:
            TopUpSummaryPopup(historyData=transaction).open()
        elif transaction.transactionType == TransactionType.GAMBLE:
            GambleSummaryPopup(historyData=transaction).open()
        else:
            print(
                f"History entry pressed: {transactionId} ({transaction.transactionType.value})"
            )
