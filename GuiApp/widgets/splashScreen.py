from kivy.uix.screenmanager import Screen
from widgets.popups.createUserOrLinkCardPopup import CreateUserOrLinkCardPopup


class SplashScreenWidget(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.create_or_link_card_popup = None

    def on_enter(self, *args):
        self.manager.RFIDReader.start(self.card_read_callback)
        return super().on_enter(*args)

    def on_pre_leave(self, *args):
        self.manager.RFIDReader.stop()
        if self.create_or_link_card_popup is not None:
            self.create_or_link_card_popup = None
        return super().on_pre_leave(*args)

    def card_read_callback(self, cardId, *args):
        user_id = self.manager.database.getPatronIdByCardId(cardId=cardId)
        if user_id is None:
            self.create_or_link_card_popup = CreateUserOrLinkCardPopup(
                screenManager=self.manager, readCard=cardId
            )
            self.create_or_link_card_popup.open()
            return

        # Card login - no PIN required
        self.manager.login(user_id)
        self.manager.transitionToScreen("mainUserPage")

    def onPressed(self):
        self.manager.transitionToScreen("loginScreen")
