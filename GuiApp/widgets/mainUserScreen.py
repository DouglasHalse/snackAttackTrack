from database import getAllSnacks
from kivy.uix.gridlayout import GridLayout
from widgets.customScreenManager import CustomScreenManager
from widgets.headerBodyLayout import HeaderBodyScreen
from widgets.popups.errorMessagePopup import ErrorMessagePopup
from widgets.settingsManager import SettingName
from widgets.uiElements.layouts import ClickableRoundedTwoColorGridLayout


class MainUserScreenOption(ClickableRoundedTwoColorGridLayout):
    __events__ = ("on_clicked",)

    def on_press(self):
        self.dispatch("on_clicked")


class GambleOption(MainUserScreenOption):
    def on_clicked(self):
        pass


class BuyOption(MainUserScreenOption):
    def on_clicked(self):
        pass


class TopUpOption(MainUserScreenOption):
    def on_clicked(self):
        pass


class HistoryOption(MainUserScreenOption):
    def on_clicked(self):
        pass


class MainUserScreenContent(GridLayout):
    def __init__(self, screenManager: CustomScreenManager, **kwargs):
        super().__init__(**kwargs)
        self.screenManager: CustomScreenManager = screenManager

        gamble_enabled = self.screenManager.settingsManager.get_setting_value(
            settingName=SettingName.ENABLE_GAMBLING
        )

        top_up_option = TopUpOption()
        buy_option = BuyOption()
        history_option = HistoryOption()

        top_up_option.bind(on_clicked=self.onTopUpButtonPressed)
        buy_option.bind(on_clicked=self.onBuyButtonPressed)
        history_option.bind(on_clicked=self.onHistoryButtonPressed)

        if gamble_enabled:
            gamble_option = GambleOption()

            gamble_option.bind(on_clicked=self.onGambleButtonPressed)

            history_and_top_up_layout = GridLayout(cols=1, spacing=30)
            history_and_top_up_layout.add_widget(top_up_option)
            history_and_top_up_layout.add_widget(history_option)

            self.add_widget(gamble_option)
            self.add_widget(buy_option)
            self.add_widget(history_and_top_up_layout)
        else:
            self.add_widget(history_option)
            self.add_widget(buy_option)
            self.add_widget(top_up_option)

    def onBuyButtonPressed(self, _):
        self.screenManager.transitionToScreen("buyScreen")

    def onTopUpButtonPressed(self, _):
        self.screenManager.transitionToScreen("topUpAmountScreen")

    def onHistoryButtonPressed(self, _):
        self.screenManager.transitionToScreen("historyScreen")

    def onGambleButtonPressed(self, _):
        numberOfSnacks = len(getAllSnacks())
        if numberOfSnacks < 2:
            ErrorMessagePopup(errorMessage="Need at least 2 snacks to gamble").open()
            return
        self.screenManager.transitionToScreen("wheelOfSnacksScreen")


class MainUserScreen(HeaderBodyScreen):
    def __init__(self, **kwargs):
        super().__init__(
            previousScreen="loginScreen", enableSettingsButton=True, **kwargs
        )
        self.headerSuffix = "Main user screen"

    def on_pre_enter(self, *args):
        super().on_pre_enter(*args)
        self.body.add_widget(MainUserScreenContent(screenManager=self.manager))
