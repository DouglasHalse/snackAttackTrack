from datetime import datetime

from database import addCredits, addTopUpTransaction
from kivy.uix.gridlayout import GridLayout
from kivy.uix.image import Image
from qrcode import make as makeQRCode
from widgets.customScreenManager import CustomScreenManager
from widgets.headerBodyLayout import HeaderBodyScreen
from widgets.popups.creditsAnimationPopup import CreditsAnimationPopup
from widgets.settingsManager import SettingName


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
        swishNumber = self.screenManager.settingsManager.get_setting_value(
            settingName=SettingName.PAYMENT_SWISH_NUMBER
        )
        self.createQrCode(
            amount=self.amountToBePayed,
            name=self.userData.firstName,
            swishNumber=swishNumber,
        )
        image = Image(source="qr.png")
        self.ids["qrCodeLayout"].add_widget(image)
        image.reload()

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

        CreditsAnimationPopup(
            title="Thank you for your top-up!",
            creditsBefore=self.userData.totalCredits,
            creditsAfter=self.userData.totalCredits + self.amountToBePayed,
        ).open()

        self.screenManager.transitionToScreen(
            "mainUserPage", transitionDirection="right"
        )

    def onCancel(self, *largs):
        self.screenManager.transitionToScreen(
            "mainUserPage", transitionDirection="right"
        )

    def createQrCode(self, amount: float, name: str, swishNumber: str):
        qrCode = makeQRCode(
            f"https://app.swish.nu/1/p/sw/?sw={swishNumber}&amt={amount:.2f}&cur=SEK&msg=Snack%20Attack%20Top-up%20for%20{name}&src=qr"
        )
        qrCode.save("qr.png")


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
