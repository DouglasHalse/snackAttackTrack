from widgets.GridLayoutScreen import GridLayoutScreen
from widgets.settingsManager import SettingName
from widgets.uiElements.buttons import ImageAndTextButton


class SystemSettingsOption(ImageAndTextButton):
    pass


class StoreStatsOption(ImageAndTextButton):
    pass


class EditSnacksOption(ImageAndTextButton):
    pass


class EditUsersOption(ImageAndTextButton):
    pass


class SalesHistoryOption(ImageAndTextButton):
    pass


class AdminScreen(GridLayoutScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.ids.systemSettingsOption.bind(
            on_release=self.onSystemSettingsButtonPressed
        )
        self.ids.editSnacksOption.bind(on_release=self.onEditSnacksButtonPressed)
        self.ids.editUsersOption.bind(on_release=self.onEditUsersButtonPressed)
        self.ids.header.bind(on_back_button_pressed=self.onBackButtonPressed)
        self.ids.storeStatsOption.bind(on_release=self.onStoreStatsButtonPressed)
        self.ids.salesHistoryOption.bind(on_release=self.onSalesHistoryButtonPressed)
        self.ids.aboutButton.bind(on_release=self.onAboutButtonPressed)

    def onSystemSettingsButtonPressed(self, _):
        self.manager.transitionToScreen("editSystemSettingsScreen")

    def onStoreStatsButtonPressed(self, _):
        self.manager.transitionToScreen("storeStatsScreen")

    def onEditSnacksButtonPressed(self, _):
        self.manager.transitionToScreen("editSnacksScreen")

    def onEditUsersButtonPressed(self, _):
        self.manager.transitionToScreen("editUsersScreen")

    def onSalesHistoryButtonPressed(self, _):
        self.manager.transitionToScreen("salesHistoryScreen")

    def onBackButtonPressed(self, _):
        self.manager.transitionToScreen("mainUserPage", transitionDirection="right")

    def onAboutButtonPressed(self, _):
        from widgets.popups.abortPopup import AboutPopup

        AboutPopup().open()

    def on_pre_enter(self, *args):
        """Check for low inventory when entering admin screen."""
        threshold = self.manager.settingsManager.get_setting_value(
            settingName=SettingName.LOW_INVENTORY_THRESHOLD
        )
        low_inventory_snacks = self.manager.database.getLowInventorySnacks(threshold)

        if low_inventory_snacks:
            from widgets.popups.lowInventoryAlertPopup import LowInventoryAlertPopup

            LowInventoryAlertPopup(snacks=low_inventory_snacks).open()

        return super().on_pre_enter(*args)
