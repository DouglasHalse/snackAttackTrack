from decimal import InvalidOperation
from app_types import Credits
from logger import get_logger
from widgets.GridLayoutScreen import GridLayoutScreen
from widgets.popups.errorMessagePopup import ErrorMessagePopup
from widgets.uiElements.textInputs import TextInputPopup


logger = get_logger(__name__)


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
        patron = self.manager.getCurrentPatron()
        if patron:
            logger.info(
                "Top-up cancelled via back button: patronId=%s", patron.patronId
            )
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

    def set_amount_to_add(self, amount: Credits):
        self.ids.creditsToAdd.text = f"{amount:.2f}"

    def updateCreditsAfterwards(self, instance, text):
        userData = self.manager.getCurrentPatron()
        currentCredits = userData.totalCredits
        try:
            creditsToAdd = Credits(self.ids.creditsToAdd.text)
        except InvalidOperation:
            creditsToAdd = Credits("0.00")

        newTotal = currentCredits + creditsToAdd
        self.ids.creditsAfterwards.text = f"{newTotal:.2f}"

    def onContinue(self, *largs):

        try:
            creditsToAdd = Credits(self.ids.creditsToAdd.text)
        except InvalidOperation:
            ErrorMessagePopup(errorMessage="Credits must be a number").open()
            return

        if creditsToAdd < Credits("0.00"):
            ErrorMessagePopup(errorMessage="Cannot add negative amount").open()
            return

        if creditsToAdd < Credits("1.00"):
            ErrorMessagePopup(errorMessage="Minimum amount is 1.0 Credits").open()
            return

        logger.info(
            "Top-up amount confirmed: patronId=%s amount=%.2f balance=%.2f",
            self.manager.getCurrentPatron().patronId,
            creditsToAdd,
            self.manager.getCurrentPatron().totalCredits,
        )
        self.manager.get_screen("topUpPaymentScreen").setAmountToBePayed(creditsToAdd)
        self.manager.transitionToScreen("topUpPaymentScreen")

    def onCancel(self, *largs):
        patron = self.manager.getCurrentPatron()
        if patron:
            logger.info(
                "Top-up cancelled via cancel button: patronId=%s", patron.patronId
            )
        self.manager.transition_back_from_top_up()
