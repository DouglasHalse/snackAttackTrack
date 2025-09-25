from kivy.uix.modalview import ModalView


class InsufficientFundsPopup(ModalView):
    __events__ = ("on_close_pressed", "on_top_up_pressed")

    def __init__(self, screen_manager, credits_needed=None, **kwargs):
        super().__init__(**kwargs)
        self.screen_manager = screen_manager
        self.credits_needed = credits_needed

    def on_close_pressed(self):
        pass

    def on_top_up_pressed(self):
        pass

    def on_close(self):
        self.dismiss()
        self.dispatch("on_close_pressed")

    def on_top_up(self):
        self.dismiss()
        self.screen_manager.transitionToScreen("topUpAmountScreen")
        if self.credits_needed:
            self.credits_needed = max(self.credits_needed, 1.0)
            self.screen_manager.get_screen("topUpAmountScreen").set_amount_to_add(
                self.credits_needed
            )
        self.dispatch("on_top_up_pressed")
