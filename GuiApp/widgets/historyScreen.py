from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.behaviors import ButtonBehavior

from database import getTransactions, HistoryData, transactionTypeToPresentableString
from widgets.customScreenManager import CustomScreenManager
from widgets.headerBodyLayout import HeaderBodyScreen


class BoxLayoutButton(ButtonBehavior, BoxLayout):
    pass


class HistoryScreenContent(GridLayout):
    def __init__(self, screenManager: CustomScreenManager, **kwargs):
        super().__init__(**kwargs)
        self.screenManager = screenManager
        currentPatron = self.screenManager.getCurrentPatron()
        self.transactions = getTransactions(currentPatron.patronId)

        # Redorder transactions so that the most recent transactions are at the top
        self.transactions = sorted(
            self.transactions, key=lambda x: x.transactionDate, reverse=True
        )

        for transaction in self.transactions:
            self.ids["historyScrollViewLayout"].add_widget(
                HistoryEntry(historyData=transaction)
            )


class HistoryScreen(HeaderBodyScreen):
    def __init__(self, **kwargs):
        super().__init__(previousScreen="mainUserPage", **kwargs)
        self.headerSuffix = "History screen"

    def on_pre_enter(self, *args):
        super().on_pre_enter(*args)
        self.body.add_widget(HistoryScreenContent(screenManager=self.manager))


class HistoryEntry(BoxLayoutButton):
    def __init__(
        self,
        historyData: HistoryData,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.historyData = historyData
        self.ids["historyDateLabel"].text = historyData.transactionDate.strftime(
            "%Y-%m-%d %H:%M:%S"
        )
        self.ids[
            "historyCreditsBeforeLabel"
        ].text = f"{historyData.amountBeforeTransaction:.2f}"
        self.ids[
            "historyCreditsAfterLabel"
        ].text = f"{historyData.amountAfterTransaction:.2f}"
        self.ids["historyTypeLabel"].text = transactionTypeToPresentableString(
            historyData.transactionType
        )

    def onPress(self, *largs):
        print("History entry pressed")
