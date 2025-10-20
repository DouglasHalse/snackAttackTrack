from database import LostSnackReason
from kivy.uix.modalview import ModalView


class RemovalReasonPopup(ModalView):
    __events__ = ("on_selection", "on_canceled")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def on_selection(self, reason: str):
        pass

    def on_canceled(self):
        pass

    def stolen_button_pressed(self):
        self.dispatch("on_selection", LostSnackReason.STOLEN)
        self.dismiss()

    def expired_button_pressed(self):
        self.dispatch("on_selection", LostSnackReason.EXPIRED)
        self.dismiss()

    def damaged_button_pressed(self):
        self.dispatch("on_selection", LostSnackReason.DAMAGED)
        self.dismiss()

    def cancel_button_pressed(self):
        self.dispatch("on_canceled")
        self.dismiss()
