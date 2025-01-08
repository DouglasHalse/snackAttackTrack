from kivy.uix.popup import Popup

from database import HistoryData


class EditSummaryPopup(Popup):
    def __init__(self, historyData: HistoryData, **kwargs):
        super().__init__(**kwargs)
        self.historyData = historyData

        self.ids["editDateLabel"].text = historyData.transactionDate.strftime(
            "%Y-%m-%d %H:%M:%S"
        )

        self.ids[
            "creditsBeforeEditLabel"
        ].text = f"{historyData.amountBeforeTransaction:.2f}"

        self.ids[
            "creditsAfterEditLabel"
        ].text = f"{historyData.amountAfterTransaction:.2f}"
