from widgets.GridLayoutScreen import GridLayoutScreen
from widgets.popups.errorMessagePopup import ErrorMessagePopup
from widgets.settingsManager import SettingName
from widgets.uiElements.buttons import ImageAndTextButton


class GambleOption(ImageAndTextButton):
    pass


class BuyOption(ImageAndTextButton):
    pass


class TopUpOption(ImageAndTextButton):
    pass


class ProfileOption(ImageAndTextButton):
    pass


class MainUserScreen(GridLayoutScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.ids.topUpOption.bind(on_release=self.onTopUpButtonPressed)
        self.ids.buyOption.bind(on_release=self.onBuyButtonPressed)
        self.ids.profileOption.bind(on_release=self.onProfileButtonPressed)
        self.ids.gambleOption.bind(on_release=self.onGambleButtonPressed)
        self.ids.header.bind(on_back_button_pressed=self.onBackButtonPressed)

    def onBuyButtonPressed(self, _):
        if self.manager.is_guest_mode():
            ErrorMessagePopup(
                errorMessage="Please create an account to purchase items"
            ).open()
            return
        self.manager.transitionToScreen("buyScreen")

    def onTopUpButtonPressed(self, _):
        if self.manager.is_guest_mode():
            ErrorMessagePopup(
                errorMessage="Please create an account to top up credits"
            ).open()
            return
        self.manager.transitionToScreen("topUpAmountScreen")

    def onProfileButtonPressed(self, _):
        if self.manager.is_guest_mode():
            ErrorMessagePopup(
                errorMessage="Please create an account to view profile"
            ).open()
            return
        self.manager.transitionToScreen("profileScreen")

    def onGambleButtonPressed(self, _):
        if self.manager.is_guest_mode():
            ErrorMessagePopup(
                errorMessage="Please create an account to use the wheel of snacks"
            ).open()
            return
        numberOfSnacks = len(self.manager.database.getAllSnacks())
        if numberOfSnacks < 2:
            ErrorMessagePopup(errorMessage="Need at least 2 snacks to gamble").open()
            return
        self.manager.transitionToScreen("wheelOfSnacksScreen")

    def onBackButtonPressed(self, *largs):
        self.manager.transitionToScreen("loginScreen", transitionDirection="right")

    def on_pre_enter(self, *args):
        super().on_pre_enter(*args)
        gamble_enabled = self.manager.settingsManager.get_setting_value(
            settingName=SettingName.ENABLE_GAMBLING
        )
        self.ids.gambleOption.disabled = not gamble_enabled
