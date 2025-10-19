from kivy.uix.modalview import ModalView


class RemoveConfirmationPopup(ModalView):
    __events__ = ("on_removed", "on_canceled")

    def __init__(self, question_text, custom_remove_button_text="Remove", **kwargs):
        super().__init__(**kwargs)
        self.ids.question_label.text = question_text
        self.ids.remove_button.text = custom_remove_button_text

    def on_canceled(self):
        pass

    def on_removed(self):
        pass

    def cancel_button_pressed(self):
        self.dispatch("on_canceled")
        self.dismiss()

    def remove_button_pressed(self):
        self.dispatch("on_removed")
        self.dismiss()
