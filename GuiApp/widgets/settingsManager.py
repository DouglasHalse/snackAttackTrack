import json
import os
from enum import Enum
from typing import Callable, Dict, Any


class SettingName(Enum):
    SPILL_FACTOR = "spill_factor"
    AUTO_LOGOUT_ON_IDLE_ENABLE = "auto_logout_on_idle_enable"
    AUTO_LOGOUT_ON_IDLE_TIME = "auto_logout_on_idle_time"
    AUTO_LOGOUT_AFTER_PURCHASE = "auto_logout_after_purchase"


def get_presentable_setting_name(settingName: SettingName):
    return settingName.value.replace("_", " ").title()


class SettingDataType(Enum):
    INT = "int"
    FLOAT = "float"
    BOOL = "bool"


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
            elif datatype == SettingDataType.FLOAT.value:
                if not isinstance(value, (float, int)):
                    raise ValueError(
                        f"Value for {get_presentable_setting_name(settingName)} must be a float"
                    )
            elif datatype == SettingDataType.BOOL.value:
                if not isinstance(value, bool):
                    raise ValueError(
                        f"Value for {get_presentable_setting_name(settingName)} must be a boolean"
                    )

            if not min_value <= value <= max_value:
                raise ValueError(
                    f"Value for {get_presentable_setting_name(settingName)} must be between {min_value} and {max_value}"
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


# Example usage
if __name__ == "__main__":

    def on_spill_factor_change(new_value):
        print(f"Spill factor changed to {new_value}")

    settings_manager = SettingsManager("settings.json")
    settings_manager.register_on_setting_change_callback(
        SettingName.SPILL_FACTOR, on_spill_factor_change
    )
    settings_manager.set_setting_value(SettingName.SPILL_FACTOR, 10)
