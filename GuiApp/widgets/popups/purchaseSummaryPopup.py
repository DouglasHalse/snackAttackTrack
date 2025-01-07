from kivy.uix.popup import Popup

from database import HistoryData
from widgets.clickableTable import ClickableTable


class PurchaseSummaryPopup(Popup):
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

        self.snackTable = ClickableTable(
            ["Snack name", "Quantity", "Price"],
            onEntryPressedCallback=None,
            size_hint_x=0.5,
        )
        for boughtSnack in historyData.transactionItems:
            self.snackTable.addEntry(
                entryContents=[
                    boughtSnack.snackName,
                    str(boughtSnack.quantity),
                    f"{boughtSnack.pricePerItem:.2f}",
                ],
                entryIdentifier=None,
            )

        self.ids["purchaseSummaryContent"].add_widget(self.snackTable)
