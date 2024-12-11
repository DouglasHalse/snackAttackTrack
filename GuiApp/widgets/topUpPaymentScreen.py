from kivy.uix.screenmanager import ScreenManager
from kivy.uix.gridlayout import GridLayout
from widgets.headerBodyLayout import HeaderBodyScreen
from database import addCredits


class TopUpPaymentScreenContent(GridLayout):
    def __init__(
        self,
        screenManager: ScreenManager,
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
        addCredits(self.userData.patronId, self.amountToBePayed)
        self.screenManager.refreshCurrentPatron()  # Refresh current patron with new credits
        self.screenManager.current = "mainUserPage"

    def onCancel(self, *largs):
        self.screenManager.current = "mainUserPage"


class TopUpPaymentScreen(HeaderBodyScreen):
    def __init__(self, **kwargs):
        super().__init__(enableSettingsButton=True, **kwargs)
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
