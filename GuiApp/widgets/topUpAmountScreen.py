from kivy.uix.screenmanager import ScreenManager
from kivy.uix.gridlayout import GridLayout
from widgets.headerBodyLayout import HeaderBodyScreen
from database import UserData


class TopUpAmountScreenContent(GridLayout):
    def __init__(self, screenManager: ScreenManager, userData: UserData, **kwargs):
        super().__init__(**kwargs)
        self.screenManager = screenManager
        self.userData = userData
        self.ids["creditsCurrent"].text = f"{self.userData.totalCredits:.2f}"
        self.ids["creditsAfterwards"].text = f"{self.userData.totalCredits:.2f}"
        self.ids["creditsToAdd"].bind(text=self.updateCreditsAfterwards)

    def updateCreditsAfterwards(self, instance, text):
        currentCredits = float(self.ids["creditsCurrent"].text)
        creditsToAdd = float(self.ids["creditsToAdd"].text)
        newTotal = currentCredits + creditsToAdd
        self.ids["creditsAfterwards"].text = f"{newTotal:.2f}"

    def onConfirm(self, *largs):
        # TODO Sanitize user input
        creditsToAdd = float(self.ids["creditsToAdd"].text)
        self.screenManager.get_screen("topUpPaymentScreen").setAmountToBePayed(
            creditsToAdd
        )
        self.screenManager.current = "topUpPaymentScreen"

    def onCancel(self, *largs):
        self.screenManager.current = "mainUserPage"


class TopUpAmountScreen(HeaderBodyScreen):
    def __init__(self, **kwargs):
        super().__init__(enableSettingsButton=True, **kwargs)
        self.headerSuffix = "Top up amount screen"

    def on_pre_enter(self, *args):
        super().on_pre_enter(*args)
        self.body.add_widget(
            TopUpAmountScreenContent(screenManager=self.manager, userData=self.userData)
        )
