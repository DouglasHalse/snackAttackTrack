from kivy.uix.screenmanager import Screen
from database import getPatronIdByCardId


class SplashScreenWidget(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def on_enter(self, *args):
        self.manager.registerCardReadCallback(self.cardRead)
        self.manager.RFIDReader.start()
        return super().on_enter(*args)

    def on_leave(self, *args):
        self.manager.unregisterCardReadCallback()
        self.manager.RFIDReader.stop()
        return super().on_leave(*args)

    def cardRead(self, cardId, *args):
        patronId = getPatronIdByCardId(cardId=cardId)
        if patronId is not None:
            self.manager.login(patronId)
            self.manager.transitionToScreen("buyScreen")

    def onPressed(self):
        self.manager.transitionToScreen("loginScreen")
