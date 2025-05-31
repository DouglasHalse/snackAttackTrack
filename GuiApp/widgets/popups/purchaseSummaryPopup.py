from database import HistoryData
from kivy.clock import Clock
from kivy.uix.modalview import ModalView


class PurchaseSummaryPopup(ModalView):
    def __init__(self, historyData: HistoryData, **kwargs):
        super().__init__(**kwargs)
        self.historyData = historyData

        self.ids["purchaseDateLabel"].text = historyData.transactionDate.strftime(
            "%Y-%m-%d %H:%M:%S"
        )
        self.ids[
            "creditsBeforeLabel"
        ].text = f"{historyData.amountBeforeTransaction:.2f}"
        self.ids["creditsAfterLabel"].text = f"{historyData.amountAfterTransaction:.2f}"
        totalNumberOfItemsBought = sum(
            item.quantity for item in historyData.transactionItems
        )
        self.ids["numberOfItemsBoughtLabel"].text = f"{totalNumberOfItemsBought}"
        totalPrice = sum(
            item.pricePerItem * item.quantity for item in historyData.transactionItems
        )
        self.ids["totalPriceLabel"].text = f"{totalPrice:.2f}"

        for boughtSnack in historyData.transactionItems:
            self.ids.itemsBoughtTable.addEntry(
                entryContents=[
                    boughtSnack.snackName,
                    str(boughtSnack.quantity),
                    f"{boughtSnack.pricePerItem:.2f}",
                ],
                entryIdentifier=None,
            )

        Clock.schedule_once(
            lambda dt: self._setHeightToContentHeight(),
        )
        Clock.schedule_once(
            lambda dt: self._bindHeightToContentHeight(),
            0,
        )

    def _setHeightToContentHeight(self, *args):
        self.height = self.ids.purchaseSummaryPopupContent.height

    def _bindHeightToContentHeight(self):
        self.ids.purchaseSummaryPopupContent.bind(size=self._setHeightToContentHeight)
