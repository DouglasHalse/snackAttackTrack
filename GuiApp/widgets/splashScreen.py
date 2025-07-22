from database import getPatronIdByCardId
from kivy.uix.screenmanager import Screen
from widgets.popups.createUserOrLinkCardPopup import CreateUserOrLinkCardPopup


class SplashScreenWidget(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def on_enter(self, *args):
        self.manager.RFIDReader.start(self.card_read_callback)
        return super().on_enter(*args)

    def on_pre_leave(self, *args):
        self.manager.RFIDReader.stop()
        return super().on_pre_leave(*args)

    def card_read_callback(self, cardId, *args):
        user_id = getPatronIdByCardId(cardId=cardId)
        if user_id is None:
            CreateUserOrLinkCardPopup(
                screenManager=self.manager, readCard=cardId
            ).open()
            return

        self.manager.login(user_id)
        self.manager.transitionToScreen("mainUserPage")

    def onPressed(self):
        self.manager.transitionToScreen("loginScreen")
