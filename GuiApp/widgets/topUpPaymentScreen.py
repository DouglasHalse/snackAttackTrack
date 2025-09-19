from datetime import datetime

from database import UserData, addCredits, addTopUpTransaction
from qrcode import make as makeQRCode
from widgets.GridLayoutScreen import GridLayoutScreen
from widgets.popups.creditsAnimationPopup import CreditsAnimationPopup
from widgets.settingsManager import SettingName


class TopUpPaymentScreen(GridLayoutScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.userData: UserData = None
        self.amount_to_be_payed: float = None
        self.ids.header.bind(on_back_button_pressed=self.on_back)

    def on_back(self, _):
        self.manager.transitionToScreen(
            "topUpAmountScreen", transitionDirection="right"
        )

    def setAmountToBePayed(self, amount: float):
        self.amount_to_be_payed = amount

    def on_pre_enter(self, *args):
        self.userData = self.manager.getCurrentPatron()
        swishNumber = self.manager.settingsManager.get_setting_value(
            settingName=SettingName.PAYMENT_SWISH_NUMBER
        )
        self.createQrCode(
            amount=self.amount_to_be_payed,
            name=self.userData.firstName,
            swishNumber=swishNumber,
        )
        self.ids["qrCodeImage"].source = "qr.png"
        self.ids["qrCodeImage"].reload()
        return super().on_pre_enter(*args)

    def onConfirm(self, *largs):
        addTopUpTransaction(
            patronID=self.userData.patronId,
            amountBeforeTransaction=self.userData.totalCredits,
            amountAfterTransaction=self.userData.totalCredits + self.amount_to_be_payed,
            transactionDate=datetime.now(),
        )
        addCredits(self.userData.patronId, self.amount_to_be_payed)

        # Update current patron with new data
        self.manager.refreshCurrentPatron()

        CreditsAnimationPopup(
            title="Thank you for your top-up!",
            creditsBefore=self.userData.totalCredits,
            creditsAfter=self.userData.totalCredits + self.amount_to_be_payed,
        ).open()

        self.manager.transitionToScreen("mainUserPage", transitionDirection="right")

    def onCancel(self, *largs):
        self.manager.transitionToScreen("mainUserPage", transitionDirection="right")

    def createQrCode(self, amount: float, name: str, swishNumber: str):
        qrCode = makeQRCode(
            f"https://app.swish.nu/1/p/sw/?sw={swishNumber}&amt={amount:.2f}&cur=SEK&msg=Snack%20Attack%20Top-up%20for%20{name}&src=qr"
        )
        qrCode.save("qr.png")
