import json

import pytest

from GuiApp.widgets.settingsManager import SettingDataType, SettingName, SettingsManager

# Fixtures are counted as redefine-outer-name
# pylint: disable=redefined-outer-name


@pytest.fixture
def settings_file(tmp_path):
    return tmp_path / "settings.json"


@pytest.fixture
def settings_manager(settings_file):
    return SettingsManager(settings_file)


def test_add_setting_if_undefined(settings_manager):
    settings_manager.add_setting_if_undefined(
        SettingName.SPILL_FACTOR, 1.0, SettingDataType.FLOAT, 0.0, 10.0
    )
    assert settings_manager.get_setting_value(SettingName.SPILL_FACTOR) == 1.0


def test_get_setting_value(settings_manager):
    settings_manager.add_setting_if_undefined(
        SettingName.AUTO_LOGOUT_ON_IDLE_ENABLE, True, SettingDataType.BOOL, False, True
    )
    assert (
        settings_manager.get_setting_value(SettingName.AUTO_LOGOUT_ON_IDLE_ENABLE)
        is True
    )


def test_set_setting_value(settings_manager):
    settings_manager.add_setting_if_undefined(
        SettingName.AUTO_LOGOUT_ON_IDLE_TIME, 30, SettingDataType.INT, 10, 60
    )
    settings_manager.set_setting_value(SettingName.AUTO_LOGOUT_ON_IDLE_TIME, 45)
    assert (
        settings_manager.get_setting_value(SettingName.AUTO_LOGOUT_ON_IDLE_TIME) == 45
    )


def test_set_setting_value_invalid_type(settings_manager):
    settings_manager.add_setting_if_undefined(
        SettingName.AUTO_LOGOUT_ON_IDLE_TIME, 30, SettingDataType.INT, 10, 60
    )
    with pytest.raises(ValueError):
        settings_manager.set_setting_value(
            SettingName.AUTO_LOGOUT_ON_IDLE_TIME, "invalid"
        )


def test_set_setting_value_out_of_range(settings_manager):
    settings_manager.add_setting_if_undefined(
        SettingName.AUTO_LOGOUT_ON_IDLE_TIME, 30, SettingDataType.INT, 10, 60
    )
    with pytest.raises(ValueError):
        settings_manager.set_setting_value(SettingName.AUTO_LOGOUT_ON_IDLE_TIME, 70)


def test_reset_setting(settings_manager):
    settings_manager.add_setting_if_undefined(
        SettingName.AUTO_LOGOUT_ON_IDLE_TIME, 30, SettingDataType.INT, 10, 60
    )
    settings_manager.set_setting_value(SettingName.AUTO_LOGOUT_ON_IDLE_TIME, 45)
    settings_manager.reset_setting(SettingName.AUTO_LOGOUT_ON_IDLE_TIME)
    assert (
        settings_manager.get_setting_value(SettingName.AUTO_LOGOUT_ON_IDLE_TIME) == 30
    )


def test_load_settings(settings_file):
    settings = {
        SettingName.SPILL_FACTOR.value: {
            "value": 1.0,
            "default_value": 1.0,
            "datatype": SettingDataType.FLOAT.value,
            "min_value": 0.0,
            "max_value": 10.0,
        }
    }
    with open(settings_file, "w", encoding="utf-8") as file:
        json.dump(settings, file)

    settings_manager = SettingsManager(settings_file)
    assert settings_manager.get_setting_value(SettingName.SPILL_FACTOR) == 1.0


def test_save_settings(settings_manager, settings_file):
    settings_manager.add_setting_if_undefined(
        SettingName.SPILL_FACTOR, 1.0, SettingDataType.FLOAT, 0.0, 10.0
    )
    settings_manager.save_settings()

    with open(settings_file, "r", encoding="utf-8") as file:
        settings = json.load(file)
        assert settings[SettingName.SPILL_FACTOR.value]["value"] == 1.0


def test_register_on_setting_change_callback(settings_manager):
    callback_called = False

    def callback(value):
        nonlocal callback_called
        callback_called = True

    settings_manager.register_on_setting_change_callback(
        SettingName.SPILL_FACTOR, callback
    )
    settings_manager.add_setting_if_undefined(
        SettingName.SPILL_FACTOR, 1.0, SettingDataType.FLOAT, 0.0, 10.0
    )
    settings_manager.set_setting_value(SettingName.SPILL_FACTOR, 2.0)
    assert callback_called


def test_callback_invoked_with_correct_value(settings_manager):
    callback_value = None

    def callback(value):
        nonlocal callback_value
        callback_value = value

    settings_manager.register_on_setting_change_callback(
        SettingName.SPILL_FACTOR, callback
    )
    settings_manager.add_setting_if_undefined(
        SettingName.SPILL_FACTOR, 1.0, SettingDataType.FLOAT, 0.0, 10.0
    )
    settings_manager.set_setting_value(SettingName.SPILL_FACTOR, 2.0)
    assert callback_value == 2.0


def test_callback_not_invoked_for_different_setting(settings_manager):
    callback_called = False

    def callback(value):
        nonlocal callback_called
        callback_called = True

    settings_manager.register_on_setting_change_callback(
        SettingName.SPILL_FACTOR, callback
    )
    settings_manager.add_setting_if_undefined(
        SettingName.AUTO_LOGOUT_ON_IDLE_ENABLE, True, SettingDataType.BOOL, False, True
    )
    settings_manager.set_setting_value(SettingName.AUTO_LOGOUT_ON_IDLE_ENABLE, False)
    assert not callback_called
