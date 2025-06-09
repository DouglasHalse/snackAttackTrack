from database import HistoryData
from kivy.clock import Clock
from kivy.uix.modalview import ModalView


class GambleSummaryPopup(ModalView):
    def __init__(self, historyData: HistoryData, **kwargs):
        super().__init__(**kwargs)
        self.historyData = historyData

        self.ids["creditsAfterLabel"].text = f"{historyData.amountAfterTransaction:.2f}"

        self.ids["gambleDateLabel"].text = historyData.transactionDate.strftime(
            "%Y-%m-%d %H:%M:%S"
        )
        self.ids[
            "creditsBeforeLabel"
        ].text = f"{historyData.amountBeforeTransaction:.2f}"

        costOfGamble = (
            historyData.amountBeforeTransaction - historyData.amountAfterTransaction
        )
        self.ids["costOfGambleLabel"].text = f"{costOfGamble:.2f}"

        totalValueOfItemsWon = sum(
            item.pricePerItem for item in historyData.transactionItems
        )

        winReturn = (
            (totalValueOfItemsWon / costOfGamble) * 100 if costOfGamble != 0 else 0
        )

        self.ids["returnLabel"].text = f"{totalValueOfItemsWon:.2f} ({winReturn:.2f}%)"

        Clock.schedule_once(
            lambda dt: self._setHeightToContentHeight(),
        )

        for wonSnack in historyData.transactionItems:
            self.ids.itemsWonTable.addEntry(
                entryContents=[
                    wonSnack.snackName,
                    f"{wonSnack.pricePerItem:.2f}",
                ],
                entryIdentifier=None,
            )

        Clock.schedule_once(
            lambda dt: self._bindHeightToContentHeight(),
            0,
        )

    def _setHeightToContentHeight(self, *args):
        self.height = self.ids.gambleSummaryPopupContent.height

    def _bindHeightToContentHeight(self):
        self.ids.gambleSummaryPopupContent.bind(size=self._setHeightToContentHeight)
