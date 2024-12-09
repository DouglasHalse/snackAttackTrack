from kivy.uix.screenmanager import ScreenManager
from kivy.uix.gridlayout import GridLayout
from widgets.headerBodyLayout import HeaderBodyScreen
from database import UserData


class TopUpAmountScreenContent(GridLayout):
    def __init__(self, screenManager: ScreenManager, userData: UserData, **kwargs):
        super().__init__(**kwargs)
        self.screenManager = screenManager
        self.userData = userData
        self.ids["creditsCurrent"].text = str(self.userData.totalCredits)
        self.ids["creditsAfterwards"].text = str(self.userData.totalCredits)
        self.ids["creditsToAdd"].bind(text=self.updateCreditsAfterwards)

    def updateCreditsAfterwards(self, instance, text):
        currentCredits = float(self.ids["creditsCurrent"].text)
        creditsToAdd = float(self.ids["creditsToAdd"].text)
        self.ids["creditsAfterwards"].text = str(currentCredits + creditsToAdd)

    def onConfirm(self, *largs):
        print("Going to top up payment screen")
        # Switch to Top up payment screen
        # creditsToAdd = float(self.ids["creditsToAdd"].text)

    def onCancel(self, *largs):
        self.screenManager.current = "mainUserPage"


class TopUpAmountScreen(HeaderBodyScreen):
    def __init__(self, **kwargs):
        super().__init__(enableSettingsButton=True, **kwargs)
        self.headerSuffix = "Top up amount screen"

    def on_enter(self, *args):
        super().on_enter(*args)
        self.body.add_widget(
            TopUpAmountScreenContent(screenManager=self.manager, userData=self.userData)
        )
