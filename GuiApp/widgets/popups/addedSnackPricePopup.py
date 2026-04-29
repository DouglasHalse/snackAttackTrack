from decimal import InvalidOperation
from kivy.uix.modalview import ModalView

from app_types import Credits
from widgets.popups.errorMessagePopup import ErrorMessagePopup


class AddedSnackPricePopup(ModalView):
    __events__ = ("on_selection", "on_canceled")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def on_selection(self, price: Credits):
        pass

    def on_canceled(self):
        pass

    def cancel_button_pressed(self):
        self.dispatch("on_canceled")
        self.dismiss()

    def confirm_button_pressed(self):

        try:
            price = Credits(self.ids.priceInput.getText())
        except InvalidOperation:
            ErrorMessagePopup(errorMessage="Price must be a number").open()
            return

        if price < 0:
            ErrorMessagePopup(errorMessage="Price cannot be negative").open()
            return

        if price == Credits("0.00"):
            ErrorMessagePopup(errorMessage="Price cannot be 0").open()
            return

        self.dispatch("on_selection", price)
        self.dismiss()
