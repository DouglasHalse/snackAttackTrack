from database import HistoryData
from kivy.clock import Clock
from kivy.uix.modalview import ModalView


class EditSummaryPopup(ModalView):
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

        Clock.schedule_once(lambda dt: self._setHeightToContentHeight())
        Clock.schedule_once(lambda dt: self._bindHeightToContentHeight())

    def _setHeightToContentHeight(self, *args):
        self.height = self.ids.editSummaryPopupContent.height

    def _bindHeightToContentHeight(self):
        self.ids.editSummaryPopupContent.bind(size=self._setHeightToContentHeight)
