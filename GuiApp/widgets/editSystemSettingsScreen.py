from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.behaviors import ButtonBehavior
from widgets.customScreenManager import CustomScreenManager
from widgets.headerBodyLayout import HeaderBodyScreen
from widgets.settingsManager import (
    SettingsManager,
    SettingName,
    get_presentable_setting_name,
)
from widgets.popups.errorMessagePopup import ErrorMessagePopup
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
        self.ids["textInput"].bind(on_text_validate=self.on_enter)
        self.ids["textInput"].bind(focus=self.on_focus)

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
    def on_enter(self, instance):
        self.validateInput()

    # Validate entry on defocus
    def on_focus(self, instance, value):
        if value:
            TextInputPopup(
                originalTextInputWidget=self.ids["textInput"],
                headerText="Edit " + get_presentable_setting_name(self.settingName),
                hintText="Setting value",
                inputFilter="float",
            ).open()
        else:
            self.validateInput()


class SettingsSection(GridLayout):
    def __init__(self, sectionName: str, **kwargs):
        super().__init__(**kwargs)
        self.ids["sectionNameLabel"].text = sectionName


class EditSystemSettingsScreenContent(GridLayout):
    def __init__(self, screenManager: CustomScreenManager, **kwargs):
        super().__init__(**kwargs)
        self.screenManager = screenManager

        # Navigation settings
        navigationSection = SettingsSection(sectionName="Navigation")
        enableAutoLogoutOnPurchase = BoolSettingRow(
            settingName=SettingName.AUTO_LOGOUT_AFTER_PURCHASE,
            settingManager=self.screenManager.settingsManager,
        )
        enableAutoLogoutTimeoutEnable = BoolSettingRow(
            settingName=SettingName.AUTO_LOGOUT_ON_IDLE_ENABLE,
            settingManager=self.screenManager.settingsManager,
        )
        enableAutoLogoutTimeoutTime = FloatSettingRow(
            settingName=SettingName.AUTO_LOGOUT_ON_IDLE_TIME,
            settingManager=self.screenManager.settingsManager,
        )

        # Disable AUTO_LOGOUT_TIMEOUT if AUTO_LOGOUT_ENABLE is False
        enableAutoLogoutTimeoutTime.set_disabled(
            not self.screenManager.settingsManager.get_setting_value(
                settingName=SettingName.AUTO_LOGOUT_ON_IDLE_ENABLE
            )
        )

        # Disable AUTO_LOGOUT_TIMEOUT if AUTO_LOGOUT_ENABLE is changed to False
        self.screenManager.settingsManager.register_on_setting_change_callback(
            SettingName.AUTO_LOGOUT_ON_IDLE_ENABLE,
            lambda value: enableAutoLogoutTimeoutTime.set_disabled(not value),
        )

        navigationSection.ids["sectionContent"].add_widget(enableAutoLogoutOnPurchase)
        navigationSection.ids["sectionContent"].add_widget(
            enableAutoLogoutTimeoutEnable
        )
        navigationSection.ids["sectionContent"].add_widget(enableAutoLogoutTimeoutTime)

        # Finalcial settings
        financialSection = SettingsSection(sectionName="Financial")
        spillFactor = FloatSettingRow(
            settingName=SettingName.SPILL_FACTOR,
            settingManager=self.screenManager.settingsManager,
        )
        financialSection.ids["sectionContent"].add_widget(spillFactor)

        # Add sections to the layout
        self.ids["settingsLayout"].add_widget(navigationSection)
        self.ids["settingsLayout"].add_widget(financialSection)


class EditSystemSettingsScreen(HeaderBodyScreen):
    def __init__(self, **kwargs):
        super().__init__(previousScreen="adminScreen", **kwargs)
        self.headerSuffix = "Edit system settings screen"

    def on_pre_enter(self, *args):
        super().on_pre_enter(*args)
        self.body.add_widget(
            EditSystemSettingsScreenContent(screenManager=self.manager)
        )
