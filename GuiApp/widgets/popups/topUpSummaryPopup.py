from kivy.uix.modalview import ModalView

from database import HistoryData


class TopUpSummaryPopup(ModalView):
    def __init__(self, historyData: HistoryData, **kwargs):
        super().__init__(**kwargs)
        self.historyData = historyData

        self.ids["topUpDateLabel"].text = historyData.transactionDate.strftime(
            "%Y-%m-%d %H:%M:%S"
        )

        self.ids[
            "creditsBeforeTopUpLabel"
        ].text = f"{historyData.amountBeforeTransaction:.2f}"

        self.ids[
            "creditsAfterTopUpLabel"
        ].text = f"{historyData.amountAfterTransaction:.2f}"
