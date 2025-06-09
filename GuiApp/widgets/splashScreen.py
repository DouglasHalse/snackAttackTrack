from database import getPatronIdByCardId
from kivy.uix.screenmanager import Screen
from widgets.popups.createUserOrLinkCardPopup import CreateUserOrLinkCardPopup


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
        if patronId is None:
            CreateUserOrLinkCardPopup(
                screenManager=self.manager, readCard=cardId
            ).open()
            return

        self.manager.login(patronId)
        self.manager.transitionToScreen("buyScreen")

    def onPressed(self):
        self.manager.transitionToScreen("loginScreen")
