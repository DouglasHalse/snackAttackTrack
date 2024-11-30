from kivy.uix.popup import Popup

class ErrorMessagePopup(Popup):
    def __init__(self, errorMessage: str, **kwargs):
        super(ErrorMessagePopup, self).__init__(**kwargs)
        self.ids.errorMessagePopupLabel.text = errorMessage