from kivy.uix.modalview import ModalView
from app_types import UserData


class LinkCardConfirmationPopup(ModalView):
    NEW_CARD = 0
    EXISTING_CARD = 1

    __events__ = ("on_confirm",)

    def __init__(self, patron_to_edit: UserData, change_type: int, **kwargs):
        super().__init__(**kwargs)
        assert isinstance(
            patron_to_edit, UserData
        ), "patron_to_edit must be an instance of UserData"
        assert change_type in (
            self.NEW_CARD,
            self.EXISTING_CARD,
        ), "change_type must be either NEW_CARD or EXISTING_CARD"
        if change_type == self.NEW_CARD:
            self.ids.title.text = (
                f"Link card to {patron_to_edit.firstName} {patron_to_edit.lastName}?"
            )
            self.ids.question.text = "Are you sure you want to link this card?"
        elif change_type == self.EXISTING_CARD:
            self.ids.title.text = f"Change linked card for {patron_to_edit.firstName} {patron_to_edit.lastName}?"
            self.ids.question.text = "Are you sure you want to change the linked card?"
        else:
            raise ValueError("Invalid change type")

    def on_confirm_button_release(self):
        self.dispatch("on_confirm")
        self.dismiss()

    def on_cancel_button_release(self):
        self.dismiss()

    def on_confirm(self):
        pass
