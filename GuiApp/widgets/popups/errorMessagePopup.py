from kivy.uix.modalview import ModalView


class ErrorMessagePopup(ModalView):
    def __init__(self, errorMessage: str, **kwargs):
        super().__init__(**kwargs)
        self.ids.errorMessagePopupLabel.text = errorMessage
