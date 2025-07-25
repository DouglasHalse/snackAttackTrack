from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from widgets.customScreenManager import CustomScreenManager
from widgets.headerBodyLayout import HeaderBodyScreen
from widgets.popups.errorMessagePopup import ErrorMessagePopup
from widgets.settingsManager import (
    SettingName,
    SettingsManager,
    get_presentable_setting_name,
)
from widgets.uiElements.textInputs import TextInputPopup


class BoxLayoutButton(ButtonBehavior, BoxLayout):
    pass


class BoolSettingRow(GridLayout):
    def __init__(
        self, settingName: SettingName, settingManager: SettingsManager, **kwargs
    ):
        super().__init__(**kwargs)
        self.settingManager: SettingsManager = settingManager
        self.settingName: SettingName = settingName
        self.ids["settingName"].text = get_presentable_setting_name(self.settingName)
        currentValue = self.settingManager.get_setting_value(
            settingName=self.settingName
        )
        self.setImage(currentValue)

    def onSettingChanged(self, *largs):
        currentValue = self.settingManager.get_setting_value(
            settingName=self.settingName
        )
        newValue = not currentValue
        self.setImage(newValue)
        self.settingManager.set_setting_value(
            settingName=self.settingName, value=newValue
        )

    def setImage(self, isOn: bool):
        if isOn:
            self.ids["toggleButtonImage"].source = "Images/toggle-on.png"
        else:
            self.ids["toggleButtonImage"].source = "Images/toggle-off.png"


class FloatSettingRow(GridLayout):
    def __init__(
        self, settingName: SettingName, settingManager: SettingsManager, **kwargs
    ):
        super().__init__(**kwargs)
        self.settingManager: SettingsManager = settingManager
        self.settingName: SettingName = settingName
        self.ids["settingName"].text = get_presentable_setting_name(self.settingName)
        settingValue = self.settingManager.get_setting_value(
            settingName=self.settingName
        )
        self.ids["textInput"].text = str(settingValue)
        self.ids["textInput"].bind(focus=self.on_focus)
        self.ids["textInput"].bind(text=self.on_text)

    def validateInput(self):
        try:
            newValue = float(self.ids["textInput"].text)
            self.settingManager.set_setting_value(
                settingName=self.settingName, value=newValue
            )
        except (TypeError, ValueError) as e:
            settingValue = self.settingManager.get_setting_value(
                settingName=self.settingName
            )
            self.ids["textInput"].text = str(settingValue)
            ErrorMessagePopup(str(e)).open()

    # Validate entry on enter
    def on_text(self, instance, *largs):
        self.validateInput()

    # Open popup on focus
    def on_focus(self, instance, value):
        if value:
            TextInputPopup(
                originalTextInputWidget=self.ids["textInput"],
                headerText="Edit " + get_presentable_setting_name(self.settingName),
                hintText="Setting value",
                inputFilter="float",
            ).open()


class StringSettingRow(GridLayout):
    def __init__(
        self, settingName: SettingName, settingManager: SettingsManager, **kwargs
    ):
        super().__init__(**kwargs)
        self.settingManager: SettingsManager = settingManager
        self.settingName: SettingName = settingName
        self.ids["settingName"].text = get_presentable_setting_name(self.settingName)
        settingValue = self.settingManager.get_setting_value(
            settingName=self.settingName
        )
        self.ids["textInput"].text = str(settingValue)
        self.ids["textInput"].bind(focus=self.on_focus)
        self.ids["textInput"].bind(text=self.on_text)

    def validateInput(self):
        try:
            newValue = str(self.ids["textInput"].text)
            self.settingManager.set_setting_value(
                settingName=self.settingName, value=newValue
            )
        except (TypeError, ValueError) as e:
            settingValue = self.settingManager.get_setting_value(
                settingName=self.settingName
            )
            self.ids["textInput"].text = str(settingValue)
            ErrorMessagePopup(str(e)).open()

    # Validate entry on enter
    def on_text(self, instance, *largs):
        self.validateInput()

    # Open popup on focus
    def on_focus(self, instance, value):
        if value:
            TextInputPopup(
                originalTextInputWidget=self.ids["textInput"],
                headerText="Edit " + get_presentable_setting_name(self.settingName),
                hintText="Setting value",
                inputFilter="float",
            ).open()


class SettingsSection(GridLayout):
    def __init__(self, sectionName: str, **kwargs):
        super().__init__(**kwargs)
        self.ids["sectionNameLabel"].text = sectionName


class EditSystemSettingsScreenContent(GridLayout):
    # pylint: disable=too-many-locals
    def __init__(self, screenManager: CustomScreenManager, **kwargs):
        super().__init__(**kwargs)
        self.screenManager = screenManager

        # Navigation settings
        navigationSection = SettingsSection(sectionName="Navigation")
        autoLogoutOnPurchase = BoolSettingRow(
            settingName=SettingName.AUTO_LOGOUT_AFTER_PURCHASE,
            settingManager=self.screenManager.settingsManager,
        )
        autoLogoutTimeoutEnable = BoolSettingRow(
            settingName=SettingName.AUTO_LOGOUT_ON_IDLE_ENABLE,
            settingManager=self.screenManager.settingsManager,
        )
        autoLogoutTimeoutTime = FloatSettingRow(
            settingName=SettingName.AUTO_LOGOUT_ON_IDLE_TIME,
            settingManager=self.screenManager.settingsManager,
        )

        # Disable AUTO_LOGOUT_TIMEOUT if AUTO_LOGOUT_ENABLE is False
        autoLogoutTimeoutTime.set_disabled(
            not self.screenManager.settingsManager.get_setting_value(
                settingName=SettingName.AUTO_LOGOUT_ON_IDLE_ENABLE
            )
        )

        # Disable AUTO_LOGOUT_TIMEOUT if AUTO_LOGOUT_ENABLE is changed to False
        self.screenManager.settingsManager.register_on_setting_change_callback(
            SettingName.AUTO_LOGOUT_ON_IDLE_ENABLE,
            lambda value: autoLogoutTimeoutTime.set_disabled(not value),
        )

        goToSplashScreenOnIdleEnable = BoolSettingRow(
            settingName=SettingName.GO_TO_SPLASH_SCREEN_ON_IDLE_ENABLE,
            settingManager=self.screenManager.settingsManager,
        )

        goToSplashScreenOnIdleTime = FloatSettingRow(
            settingName=SettingName.GO_TO_SPLASH_SCREEN_ON_IDLE_TIME,
            settingManager=self.screenManager.settingsManager,
        )

        # Disable GO_TO_SPLASH_SCREEN_ON_IDLE_TIME if GO_TO_SPLASH_SCREEN_ON_IDLE_ENABLE is False
        goToSplashScreenOnIdleTime.set_disabled(
            not self.screenManager.settingsManager.get_setting_value(
                settingName=SettingName.GO_TO_SPLASH_SCREEN_ON_IDLE_ENABLE
            )
        )

        # Disable GO_TO_SPLASH_SCREEN_ON_IDLE_TIME if GO_TO_SPLASH_SCREEN_ON_IDLE_ENABLE is changed to False
        self.screenManager.settingsManager.register_on_setting_change_callback(
            SettingName.GO_TO_SPLASH_SCREEN_ON_IDLE_ENABLE,
            lambda value: goToSplashScreenOnIdleTime.set_disabled(not value),
        )

        navigationSection.ids["sectionContent"].add_widget(autoLogoutOnPurchase)
        navigationSection.ids["sectionContent"].add_widget(autoLogoutTimeoutEnable)
        navigationSection.ids["sectionContent"].add_widget(autoLogoutTimeoutTime)
        navigationSection.ids["sectionContent"].add_widget(goToSplashScreenOnIdleEnable)
        navigationSection.ids["sectionContent"].add_widget(goToSplashScreenOnIdleTime)

        # Finalcial settings
        financialSection = SettingsSection(sectionName="Financial")
        purchaseFee = FloatSettingRow(
            settingName=SettingName.PURCHASE_FEE,
            settingManager=self.screenManager.settingsManager,
        )
        paymentSwishNumber = StringSettingRow(
            settingName=SettingName.PAYMENT_SWISH_NUMBER,
            settingManager=self.screenManager.settingsManager,
        )

        financialSection.ids["sectionContent"].add_widget(purchaseFee)
        financialSection.ids["sectionContent"].add_widget(paymentSwishNumber)

        buyScreenSection = SettingsSection(sectionName="Buy screen")

        orderInventoryByMostPurchased = BoolSettingRow(
            settingName=SettingName.ORDER_INVENTORY_BY_MOST_PURCHASED,
            settingManager=self.screenManager.settingsManager,
        )

        buyScreenSection.ids["sectionContent"].add_widget(orderInventoryByMostPurchased)

        # Gambling settings
        gamblingSection = SettingsSection(sectionName="Gambling")

        enableGambling = BoolSettingRow(
            settingName=SettingName.ENABLE_GAMBLING,
            settingManager=self.screenManager.settingsManager,
        )

        excitingGambling = BoolSettingRow(
            settingName=SettingName.EXCITING_GAMBLING,
            settingManager=self.screenManager.settingsManager,
        )

        excitingGambling.set_disabled(
            not self.screenManager.settingsManager.get_setting_value(
                settingName=SettingName.ENABLE_GAMBLING
            )
        )

        self.screenManager.settingsManager.register_on_setting_change_callback(
            SettingName.ENABLE_GAMBLING,
            lambda value: excitingGambling.set_disabled(not value),
        )

        gamblingSection.ids["sectionContent"].add_widget(enableGambling)
        gamblingSection.ids["sectionContent"].add_widget(excitingGambling)

        # Add sections to the layout
        self.ids["settingsLayout"].add_widget(navigationSection)
        self.ids["settingsLayout"].add_widget(financialSection)
        self.ids["settingsLayout"].add_widget(buyScreenSection)
        self.ids["settingsLayout"].add_widget(gamblingSection)

    # pylint: enable=too-many-locals


class EditSystemSettingsScreen(HeaderBodyScreen):
    def __init__(self, **kwargs):
        super().__init__(previousScreen="adminScreen", **kwargs)
        self.headerSuffix = "Edit system settings screen"

    def on_pre_enter(self, *args):
        super().on_pre_enter(*args)
        self.body.add_widget(
            EditSystemSettingsScreenContent(screenManager=self.manager)
        )
