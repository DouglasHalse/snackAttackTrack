from widgets.GridLayoutScreen import GridLayoutScreen
from widgets.uiElements.buttons import ImageAndTextButton


class HistoryOption(ImageAndTextButton):
    pass


class StatisticsOption(ImageAndTextButton):
    pass


class ProfileScreen(GridLayoutScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.ids.historyOption.bind(on_release=self.onHistoryButtonPressed)
        self.ids.statisticsOption.bind(on_release=self.onStatisticsButtonPressed)
        self.ids.header.bind(on_back_button_pressed=self.onBackButtonPressed)

    def onHistoryButtonPressed(self, _):
        self.manager.transitionToScreen("historyScreen")

    def onStatisticsButtonPressed(self, _):
        self.manager.transitionToScreen("userStatisticsScreen")

    def onBackButtonPressed(self, *largs):
        self.manager.transitionToScreen("mainUserPage", transitionDirection="right")
