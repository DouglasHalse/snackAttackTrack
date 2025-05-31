from database import HistoryData
from kivy.clock import Clock
from kivy.uix.modalview import ModalView


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

        Clock.schedule_once(
            lambda dt: self._bindHeightToContentHeight(),
            0,
        )

        Clock.schedule_once(
            lambda dt: self._setHeightToContentHeight(),
        )

    def _setHeightToContentHeight(self, *args):
        self.height = self.ids.topUpSummaryPopupContent.height

    def _bindHeightToContentHeight(self):
        self.ids.topUpSummaryPopupContent.bind(size=self._setHeightToContentHeight)
