from kivy.uix.gridlayout import GridLayout

from database import (
    getTransactions,
    transactionTypeToPresentableString,
    getTransaction,
    TransactionType,
)
from widgets.customScreenManager import CustomScreenManager
from widgets.headerBodyLayout import HeaderBodyScreen
from widgets.popups.purchaseSummaryPopup import PurchaseSummaryPopup
from widgets.clickableTable import ClickableTable


class HistoryScreenContent(GridLayout):
    def __init__(self, screenManager: CustomScreenManager, **kwargs):
        super().__init__(**kwargs)
        self.screenManager = screenManager

        self.historyTable = ClickableTable(
            ["Date", "Credits before", "Credits after", "Type"],
            onEntryPressedCallback=self.onHistoryEntryPressed,
        )

        currentPatron = self.screenManager.getCurrentPatron()
        self.transactions = getTransactions(currentPatron.patronId)

        # Redorder transactions so that the most recent transactions are at the top
        self.transactions = sorted(
            self.transactions, key=lambda x: x.transactionDate, reverse=True
        )

        for transaction in self.transactions:
            self.historyTable.addEntry(
                entryContents=[
                    transaction.transactionDate.strftime("%Y-%m-%d %H:%M:%S"),
                    f"{transaction.amountBeforeTransaction:.2f}",
                    f"{transaction.amountAfterTransaction:.2f}",
                    transactionTypeToPresentableString(transaction.transactionType),
                ],
                entryIdentifier=transaction.transactionId,
            )

        self.add_widget(self.historyTable)

    def onHistoryEntryPressed(self, transactionId):
        transaction = getTransaction(transactionId)
        if transaction.transactionType == TransactionType.PURCHASE:
            PurchaseSummaryPopup(historyData=transaction).open()
        else:
            print(
                f"History entry pressed: {transactionId} ({transaction.transactionType.value})"
            )


class HistoryScreen(HeaderBodyScreen):
    def __init__(self, **kwargs):
        super().__init__(previousScreen="mainUserPage", **kwargs)
        self.headerSuffix = "History screen"

    def on_pre_enter(self, *args):
        super().on_pre_enter(*args)
        self.body.add_widget(HistoryScreenContent(screenManager=self.manager))
