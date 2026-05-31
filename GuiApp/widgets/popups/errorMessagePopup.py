from kivy.uix.modalview import ModalView
from logger import get_logger


logger = get_logger(__name__)


class ErrorMessagePopup(ModalView):
    def __init__(self, errorMessage: str, **kwargs):
        super().__init__(**kwargs)
        self.ids.errorMessagePopupLabel.text = errorMessage
        logger.warning("Error popup shown: %s", errorMessage)
