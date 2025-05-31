from kivy.uix.gridlayout import GridLayout
from widgets.customScreenManager import CustomScreenManager
from widgets.headerBodyLayout import HeaderBodyScreen
from widgets.popups.errorMessagePopup import ErrorMessagePopup
from widgets.uiElements.textInputs import TextInputPopup


class TopUpAmountScreenContent(GridLayout):
    def __init__(self, screenManager: CustomScreenManager, **kwargs):
        super().__init__(**kwargs)
        self.screenManager = screenManager
        self.userData = self.screenManager.getCurrentPatron()
        self.ids["creditsCurrent"].text = f"{self.userData.totalCredits:.2f}"
        self.ids["creditsAfterwards"].text = f"{self.userData.totalCredits:.2f}"
        self.ids["creditsToAdd"].bind(text=self.updateCreditsAfterwards)
        self.ids["creditsToAdd"].bind(focus=self.on_focus)

    def on_focus(self, instance, value):
        if value:
            TextInputPopup(
                originalTextInputWidget=self.ids["creditsToAdd"],
                headerText="Credits to add",
                hintText="Enter amount",
                inputFilter="float",
            ).open()

    def updateCreditsAfterwards(self, instance, text):
        currentCredits = float(self.ids["creditsCurrent"].text)
        try:
            creditsToAdd = float(self.ids["creditsToAdd"].text)
        except ValueError:
            creditsToAdd = 0.0

        newTotal = currentCredits + creditsToAdd
        self.ids["creditsAfterwards"].text = f"{newTotal:.2f}"

    def onContinue(self, *largs):

        try:
            creditsToAdd = float(self.ids["creditsToAdd"].text)
        except ValueError:
            ErrorMessagePopup(errorMessage="Credits must be a number").open()
            return

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
