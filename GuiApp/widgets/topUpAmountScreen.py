from kivy.uix.gridlayout import GridLayout

from widgets.customScreenManager import CustomScreenManager
from widgets.headerBodyLayout import HeaderBodyScreen
from widgets.popups.errorMessagePopup import ErrorMessagePopup


class TopUpAmountScreenContent(GridLayout):
    def __init__(self, screenManager: CustomScreenManager, **kwargs):
        super().__init__(**kwargs)
        self.screenManager = screenManager
        self.userData = self.screenManager.getCurrentPatron()
        self.ids["creditsCurrent"].text = f"{self.userData.totalCredits:.2f}"
        self.ids["creditsAfterwards"].text = f"{self.userData.totalCredits:.2f}"
        self.ids["creditsToAdd"].bind(text=self.updateCreditsAfterwards)

    def getCreditsToAdd(self) -> float:
        creditsToAddStr = self.ids["creditsToAdd"].text
        if not creditsToAddStr or creditsToAddStr == "-":
            return 0.0
        return float(self.ids["creditsToAdd"].text)

    def updateCreditsAfterwards(self, instance, text):
        currentCredits = float(self.ids["creditsCurrent"].text)
        creditsToAdd = self.getCreditsToAdd()
        newTotal = currentCredits + creditsToAdd
        self.ids["creditsAfterwards"].text = f"{newTotal:.2f}"

    def onConfirm(self, *largs):
        creditsToAdd = self.getCreditsToAdd()

        if creditsToAdd < 0.0:
            ErrorMessagePopup(errorMessage="Cannot add negative amount").open()
            return

        if creditsToAdd < 1.0:
            ErrorMessagePopup(errorMessage="Minimum amount is 1.0 Credits").open()
            return

        self.screenManager.get_screen("topUpPaymentScreen").setAmountToBePayed(
            creditsToAdd
        )
        self.screenManager.transitionToScreen("topUpPaymentScreen")

    def onCancel(self, *largs):
        self.screenManager.transitionToScreen(
            "mainUserPage", transitionDirection="right"
        )


class TopUpAmountScreen(HeaderBodyScreen):
    def __init__(self, **kwargs):
        super().__init__(previousScreen="mainUserPage", **kwargs)
        self.headerSuffix = "Top up amount screen"

    def on_pre_enter(self, *args):
        super().on_pre_enter(*args)
        self.body.add_widget(TopUpAmountScreenContent(screenManager=self.manager))
