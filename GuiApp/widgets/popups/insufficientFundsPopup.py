from kivy.uix.modalview import ModalView


class InsufficientFundsPopup(ModalView):
    def __init__(self, screenManager, **kwargs):
        super().__init__(**kwargs)
        self.screenManager = screenManager

    def on_close_pressed(self):
        self.dismiss()

    def on_top_up_pressed(self):
        self.dismiss()
        self.screenManager.transitionToScreen("topUpAmountScreen")
