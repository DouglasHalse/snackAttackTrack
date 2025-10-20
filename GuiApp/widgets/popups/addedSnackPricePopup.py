from kivy.uix.modalview import ModalView


class AddedSnackPricePopup(ModalView):
    __events__ = ("on_selection", "on_canceled")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def on_selection(self, reason: str):
        pass

    def on_canceled(self):
        pass

    def cancel_button_pressed(self):
        self.dispatch("on_canceled")
        self.dismiss()

    def confirm_button_pressed(self):
        self.dispatch("on_selection", float(self.ids.priceInput.getText()))
        self.dismiss()
