from kivy.uix.screenmanager import ScreenManager
from kivy.uix.gridlayout import GridLayout
from widgets.headerBodyLayout import HeaderBodyScreen
from database import addCredits, getPatronData


class TopUpPaymentScreenContent(GridLayout):
    def __init__(
        self,
        screenManager: ScreenManager,
        amountToBePayed: float,
        userId: int,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.screenManager = screenManager
        self.amountToBePayed = amountToBePayed
        self.userId = userId
        self.ids[
            "amountLabel"
        ].text = f"Select {self.amountToBePayed:.2f} SEK as amount"

    def onConfirm(self, *largs):
        addCredits(self.userId, self.amountToBePayed)
        # TODO update UserData in a better way
        newUserData = getPatronData(patronID=self.userId)
        self.screenManager.get_screen("mainUserPage").setUserData(newUserData)
        self.screenManager.get_screen("adminScreen").setUserData(newUserData)
        self.screenManager.get_screen("editSnacksScreen").setUserData(newUserData)
        self.screenManager.get_screen("editUsersScreen").setUserData(newUserData)
        self.screenManager.get_screen("addSnackScreen").setUserData(newUserData)
        self.screenManager.get_screen("topUpAmountScreen").setUserData(newUserData)
        self.screenManager.get_screen("topUpPaymentScreen").setUserData(newUserData)
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
                userId=self.userData.patronId,
            )
        )
