from kivy.clock import Clock
from kivy.uix.modalview import ModalView


class NoPaymentMethodPopup(ModalView):
    __events__ = ("on_cancel_pressed", "on_set_up_payment_pressed")

    def __init__(self, screen_manager, **kwargs):
        super().__init__(**kwargs)
        self.screen_manager = screen_manager

    def on_cancel_pressed(self):
        pass

    def on_set_up_payment_pressed(self):
        pass

    def on_cancel(self):
        self.dismiss()
        self.dispatch("on_cancel_pressed")

    def on_set_up_payment(self):
        self.dismiss()
        self.screen_manager.transitionToScreen("editSystemSettingsScreen")
        # After the screen transition completes, scroll to the payment detail row
        Clock.schedule_once(lambda dt: self._scroll_to_payment_setting(), 0.3)
        self.dispatch("on_set_up_payment_pressed")

    def _scroll_to_payment_setting(self):
        screen = self.screen_manager.get_screen("editSystemSettingsScreen")
        if hasattr(screen, "scroll_to_payment_detail_setting"):
            screen.scroll_to_payment_detail_setting()
