from widgets.GridLayoutScreen import GridLayoutScreen
from widgets.popups.errorMessagePopup import ErrorMessagePopup
from widgets.uiElements.textInputs import TextInputPopup


class TopUpAmountScreen(GridLayoutScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.credit_input_popup = None
        self.ids.creditsToAdd.bind(text=self.updateCreditsAfterwards)
        self.ids.creditsToAdd.bind(focus=self.on_focus)
        self.ids.header.bind(on_back_button_pressed=self.on_back)

    def on_pre_enter(self, *args):
        userData = self.manager.getCurrentPatron()
        self.ids.creditsCurrent.text = f"{userData.totalCredits:.2f}"
        self.ids.creditsAfterwards.text = f"{userData.totalCredits:.2f}"
        self.ids.creditsToAdd.text = ""
        return super().on_pre_enter(*args)

    def on_pre_leave(self, *args):
        if self.credit_input_popup:
            self.credit_input_popup.dismiss()
            self.credit_input_popup = None
        return super().on_pre_leave(*args)

    def on_back(self, _):
        self.manager.transition_back_from_top_up()

    def on_focus(self, instance, value):
        if value:
            self.credit_input_popup = TextInputPopup(
                originalTextInputWidget=self.ids.creditsToAdd,
                headerText="Credits to add",
                hintText="Enter amount",
                inputFilter="currency",
            )
            self.credit_input_popup.open()

    def set_amount_to_add(self, amount: float):
        self.ids.creditsToAdd.text = f"{amount:.2f}"

    def updateCreditsAfterwards(self, instance, text):
        currentCredits = float(self.ids.creditsCurrent.text)
        try:
            creditsToAdd = float(self.ids.creditsToAdd.text)
        except ValueError:
            creditsToAdd = 0.0

        newTotal = currentCredits + creditsToAdd
        self.ids.creditsAfterwards.text = f"{newTotal:.2f}"

    def onContinue(self, *largs):

        try:
            creditsToAdd = float(self.ids.creditsToAdd.text)
        except ValueError:
            ErrorMessagePopup(errorMessage="Credits must be a number").open()
            return

        if creditsToAdd < 0.0:
            ErrorMessagePopup(errorMessage="Cannot add negative amount").open()
            return

        if creditsToAdd < 1.0:
            ErrorMessagePopup(errorMessage="Minimum amount is 1.0 Credits").open()
            return

        self.manager.get_screen("topUpPaymentScreen").setAmountToBePayed(creditsToAdd)
        self.manager.transitionToScreen("topUpPaymentScreen")

    def onCancel(self, *largs):
        self.manager.transition_back_from_top_up()
