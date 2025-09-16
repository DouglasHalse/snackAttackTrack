from database import getAllSnacks
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


class HistoryOption(ImageAndTextButton):
    pass


class MainUserScreen(GridLayoutScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.ids.topUpOption.bind(on_release=self.onTopUpButtonPressed)
        self.ids.buyOption.bind(on_release=self.onBuyButtonPressed)
        self.ids.historyOption.bind(on_release=self.onHistoryButtonPressed)
        self.ids.gambleOption.bind(on_release=self.onGambleButtonPressed)
        self.ids.header.bind(on_back_button_pressed=self.onBackButtonPressed)

    def onBuyButtonPressed(self, _):
        self.manager.transitionToScreen("buyScreen")

    def onTopUpButtonPressed(self, _):
        self.manager.transitionToScreen("topUpAmountScreen")

    def onHistoryButtonPressed(self, _):
        self.manager.transitionToScreen("historyScreen")

    def onGambleButtonPressed(self, _):
        numberOfSnacks = len(getAllSnacks())
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
