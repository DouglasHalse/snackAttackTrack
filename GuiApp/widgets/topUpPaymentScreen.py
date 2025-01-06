from datetime import datetime

from kivy.uix.gridlayout import GridLayout

from widgets.customScreenManager import CustomScreenManager
from widgets.headerBodyLayout import HeaderBodyScreen
from database import addCredits, addTopUpTransaction


class TopUpPaymentScreenContent(GridLayout):
    def __init__(
        self,
        screenManager: CustomScreenManager,
        amountToBePayed: float,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.screenManager = screenManager
        self.amountToBePayed = amountToBePayed
        self.userData = self.screenManager.getCurrentPatron()
        self.ids[
            "amountLabel"
        ].text = f"Select {self.amountToBePayed:.2f} SEK as amount"

    def onConfirm(self, *largs):
        addTopUpTransaction(
            patronID=self.userData.patronId,
            amountBeforeTransaction=self.userData.totalCredits,
            amountAfterTransaction=self.userData.totalCredits + self.amountToBePayed,
            transactionDate=datetime.now(),
        )
        addCredits(self.userData.patronId, self.amountToBePayed)

        # Update current patron with new data
        self.screenManager.refreshCurrentPatron()

        self.screenManager.transitionToScreen(
            "mainUserPage", transitionDirection="right"
        )

    def onCancel(self, *largs):
        self.screenManager.transitionToScreen(
            "mainUserPage", transitionDirection="right"
        )


class TopUpPaymentScreen(HeaderBodyScreen):
    def __init__(self, **kwargs):
        super().__init__(previousScreen="topUpAmountScreen", **kwargs)
        self.headerSuffix = "Top up payment screen"
        self.amountToBePayed = 0.0

    def setAmountToBePayed(self, amount: float):
        self.amountToBePayed = amount

    def on_pre_enter(self, *args):
        super().on_pre_enter(*args)
        self.body.add_widget(
            TopUpPaymentScreenContent(
                screenManager=self.manager,
                amountToBePayed=self.amountToBePayed,
            )
        )
