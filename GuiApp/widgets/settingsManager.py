import json
import os
from enum import Enum
from typing import Any, Callable, Dict

from widgets.swishApiClient import SwishApiClient


class SettingName(Enum):
    SPILL_FACTOR = "spill_factor"
    AUTO_LOGOUT_ON_IDLE_ENABLE = "auto_logout_on_idle_enable"
    AUTO_LOGOUT_ON_IDLE_TIME = "auto_logout_on_idle_time"
    AUTO_LOGOUT_AFTER_PURCHASE = "auto_logout_after_purchase"
    PURCHASE_FEE = "purchase_fee"
    PAYMENT_METHOD = "payment_method"
    PAYMENT_SWISH_NUMBER = "payment_swish_number"
    ENABLE_SWISH_COMMERCE = "enable_swish_commerce"
    SWISH_API_BASE_URL = "swish_api_base_url"
    GO_TO_SPLASH_SCREEN_ON_IDLE_ENABLE = "go_to_splash_screen_on_idle_enable"
    GO_TO_SPLASH_SCREEN_ON_IDLE_TIME = "go_to_splash_screen_on_idle_time"
    ORDER_INVENTORY_BY_MOST_PURCHASED = "order_inventory_by_most_purchased"
    ENABLE_GAMBLING = "enable_gambling"
    EXCITING_GAMBLING = "exciting_gambling"


class PaymentMethodType(Enum):
    """Supported payment method options."""

    SWISH = "swish"

    def display_name(self) -> str:
        """Return a human-readable name for this payment method."""
        return self.value.replace("_", " ").title()

    @staticmethod
    def from_value(value: str) -> "PaymentMethodType":
        """Get the enum member for a given string value, defaulting to SWISH."""
        for member in PaymentMethodType:
            if member.value == value:
                return member
        return PaymentMethodType.SWISH


class SwishEnvironment(Enum):
    """Swish API environment options with human-readable names."""

    MSS = "https://mss.cpc.getswish.net"
    SANDBOX = "https://staging.getswish.pub.tds.tieto.com"
    PRODUCTION = "https://cpc.getswish.net"

    def display_name(self) -> str:
        """Return a human-readable name for this environment."""
        if self == SwishEnvironment.MSS:
            return "MSS (Test)"
        if self == SwishEnvironment.SANDBOX:
            return "Sandbox"
        if self == SwishEnvironment.PRODUCTION:
            return "Production"
        return self.value.replace("_", " ").title()

    @staticmethod
    def from_value(value: str) -> "SwishEnvironment":
        """Get the enum member for a given URL, defaulting to MSS."""
        for member in SwishEnvironment:
            if member.value == value:
                return member
        return SwishEnvironment.MSS


def get_presentable_setting_name(settingName: SettingName):
    return settingName.value.replace("_", " ").title()


class SettingDataType(Enum):
    INT = "int"
    FLOAT = "float"
    BOOL = "bool"
    STRING = "string"


class SettingsManager:
    def __init__(self, file_path):
        self.file_path = file_path
        self.settings = {}
        self.callbacks: Dict[str, Callable[[Any], None]] = {}
        self.load_settings()

    def add_setting_if_undefined(
        self,
        settingName: SettingName,
        default_value,
        datatype: SettingDataType,
        min_value,
        max_value,
    ):
        if settingName.value not in self.settings:
            self.settings[settingName.value] = {
                "value": default_value,
                "default_value": default_value,
                "datatype": datatype.value,
                "min_value": min_value,
                "max_value": max_value,
            }

    def get_setting_value(self, settingName: SettingName):
        return self.settings[settingName.value]["value"]

    def is_value_within_range(self, settingName: SettingName, value):
        return (
            self.settings[settingName.value]["min_value"]
            <= value
            <= self.settings[settingName.value]["max_value"]
        )

    def set_setting_value(self, settingName: SettingName, value):
        if settingName.value in self.settings:
            setting = self.settings[settingName.value]
            datatype = setting["datatype"]
            min_value = setting["min_value"]
            max_value = setting["max_value"]

            if datatype == SettingDataType.INT.value:
                if not isinstance(value, int):
                    raise ValueError(
                        f"Value for {get_presentable_setting_name(settingName)} must be an integer"
                    )
                if not self.is_value_within_range(settingName, value):
                    raise ValueError(
                        f"Value for {get_presentable_setting_name(settingName)} must be between {min_value} and {max_value}"
                    )
            elif datatype == SettingDataType.FLOAT.value:
                if not isinstance(value, (float, int)):
                    raise ValueError(
                        f"Value for {get_presentable_setting_name(settingName)} must be a float"
                    )
                if not self.is_value_within_range(settingName, value):
                    raise ValueError(
                        f"Value for {get_presentable_setting_name(settingName)} must be between {min_value} and {max_value}"
                    )
            elif datatype == SettingDataType.BOOL.value:
                if not isinstance(value, bool):
                    raise ValueError(
                        f"Value for {get_presentable_setting_name(settingName)} must be a boolean"
                    )
            elif datatype == SettingDataType.STRING.value:
                if not isinstance(value, str):
                    raise ValueError(
                        f"Value for {get_presentable_setting_name(settingName)} must be a string"
                    )

            self.settings[settingName.value]["value"] = value
            self.save_settings()
            self._notify_setting_change(settingName, value)
        else:
            raise KeyError(f"Setting {settingName.value} not found")

    def load_settings(self):
        if os.path.exists(self.file_path):
            with open(self.file_path, "r", encoding="utf-8") as file:
                self.settings = json.load(file)
        else:
            self.settings = {}

    def save_settings(self):
        with open(self.file_path, "w", encoding="utf-8") as file:
            json.dump(self.settings, file, indent=4)

    def reset_setting(self, key: SettingName):
        if key.value in self.settings:
            self.settings[key.value]["value"] = self.settings[key.value][
                "default_value"
            ]
            self.save_settings()
            self._notify_setting_change(key, self.settings[key.value]["value"])

    def register_on_setting_change_callback(
        self, settingName: SettingName, callback: Callable[[Any], None]
    ):
        self.callbacks[settingName.value] = callback

    def _notify_setting_change(self, settingName: SettingName, value):
        if settingName.value in self.callbacks:
            self.callbacks[settingName.value](value)

    def is_payment_method_ready(self) -> bool:
        """Check whether the currently selected payment method is fully configured.

        Dispatches to method-specific checks so each payment type can define
        what "ready" means (e.g. Swish needs a phone number, Swish Online
        needs API credentials).
        """
        method = self.get_setting_value(settingName=SettingName.PAYMENT_METHOD)
        if method == PaymentMethodType.SWISH.value:
            if self.get_setting_value(settingName=SettingName.ENABLE_SWISH_COMMERCE):
                # Commerce mode: check for certificates
                detected = SwishApiClient.detect_certificates()
                return bool(detected.get("cert_path"))
            # Manual mode: check for Swish number
            return bool(
                self.get_setting_value(settingName=SettingName.PAYMENT_SWISH_NUMBER)
            )
        # Unknown / unset method → not ready
        return False


# Example usage
if __name__ == "__main__":

    def on_spill_factor_change(new_value):
        print(f"Spill factor changed to {new_value}")

    settings_manager = SettingsManager("settings.json")
    settings_manager.register_on_setting_change_callback(
        SettingName.SPILL_FACTOR, on_spill_factor_change
    )
    settings_manager.set_setting_value(SettingName.SPILL_FACTOR, 10)
