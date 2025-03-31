from kivy.uix.modalview import ModalView


class CreateUserOrLinkCardPopup(ModalView):
    def __init__(self, screenManager, readCard, **kwargs):
        super().__init__(**kwargs)
        self.screenManager = screenManager
        self.readCard = readCard

    def createUserPressed(self):
        self.dismiss()
        self.screenManager.get_screen("createUserScreen").cardRead(self.readCard)
        self.screenManager.transitionToScreen("createUserScreen")

    def linkCardPressed(self):
        self.dismiss()
        self.screenManager.get_screen("linkCardScreen").setCardToLink(self.readCard)
        self.screenManager.transitionToScreen("linkCardScreen")

    def on_dismiss(self):
        self.screenManager.RFIDReader.clearLastReadId()
        return super().on_dismiss()
