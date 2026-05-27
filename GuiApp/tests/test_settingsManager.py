import json

import pytest

from GuiApp.widgets.settingsManager import (
    PaymentMethodType,
    SettingDataType,
    SettingName,
    SettingsManager,
)

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


class TestPaymentMethodType:
    def test_swish_display_name(self):
        assert PaymentMethodType.SWISH.display_name() == "Swish"

    def test_from_value_swish(self):
        assert PaymentMethodType.from_value("swish") == PaymentMethodType.SWISH

    def test_from_value_unknown_defaults_to_swish(self):
        assert PaymentMethodType.from_value("klarna") == PaymentMethodType.SWISH

    def test_from_value_empty_defaults_to_swish(self):
        assert PaymentMethodType.from_value("") == PaymentMethodType.SWISH


# --- SettingsManager.is_payment_method_ready tests ---


@pytest.fixture
def settings_manager_with_payment_methods(settings_manager):
    settings_manager.add_setting_if_undefined(
        SettingName.PAYMENT_METHOD, "swish", SettingDataType.STRING, 0, 0
    )
    settings_manager.add_setting_if_undefined(
        SettingName.PAYMENT_SWISH_NUMBER, "", SettingDataType.STRING, 0, 0
    )
    settings_manager.add_setting_if_undefined(
        SettingName.ENABLE_SWISH_COMMERCE, False, SettingDataType.BOOL, 0, 1
    )
    return settings_manager


class TestIsPaymentMethodReady:
    def test_swish_with_number(self, settings_manager_with_payment_methods):
        sm = settings_manager_with_payment_methods
        sm.set_setting_value(SettingName.PAYMENT_SWISH_NUMBER, "1234567890")
        assert sm.is_payment_method_ready() is True

    def test_swish_without_number(self, settings_manager_with_payment_methods):
        sm = settings_manager_with_payment_methods
        sm.set_setting_value(SettingName.PAYMENT_SWISH_NUMBER, "")
        assert sm.is_payment_method_ready() is False

    def test_unknown_method(self, settings_manager):
        settings_manager.add_setting_if_undefined(
            SettingName.PAYMENT_METHOD, "unknown", SettingDataType.STRING, 0, 0
        )
        settings_manager.add_setting_if_undefined(
            SettingName.PAYMENT_SWISH_NUMBER, "1234567890", SettingDataType.STRING, 0, 0
        )
        assert settings_manager.is_payment_method_ready() is False

    def test_unset_method_with_number(self, settings_manager):
        settings_manager.add_setting_if_undefined(
            SettingName.PAYMENT_METHOD, "", SettingDataType.STRING, 0, 0
        )
        settings_manager.add_setting_if_undefined(
            SettingName.PAYMENT_SWISH_NUMBER, "1234567890", SettingDataType.STRING, 0, 0
        )
        assert settings_manager.is_payment_method_ready() is False


class TestIsPaymentMethodReadyCommerce:
    def test_commerce_with_certs(self, settings_manager):
        """Commerce mode with certificates present is ready."""
        settings_manager.add_setting_if_undefined(
            SettingName.PAYMENT_METHOD, "swish", SettingDataType.STRING, 0, 0
        )
        settings_manager.add_setting_if_undefined(
            SettingName.ENABLE_SWISH_COMMERCE, True, SettingDataType.BOOL, 0, 1
        )
        settings_manager.add_setting_if_undefined(
            SettingName.PAYMENT_SWISH_NUMBER, "", SettingDataType.STRING, 0, 0
        )
        # Certs are present in the test environment → ready
        assert settings_manager.is_payment_method_ready() is True

    def test_commerce_without_commerce_flag(self, settings_manager):
        """Commerce flag off with Swish number set is ready (manual mode)."""
        settings_manager.add_setting_if_undefined(
            SettingName.PAYMENT_METHOD, "swish", SettingDataType.STRING, 0, 0
        )
        settings_manager.add_setting_if_undefined(
            SettingName.ENABLE_SWISH_COMMERCE, False, SettingDataType.BOOL, 0, 1
        )
        settings_manager.add_setting_if_undefined(
            SettingName.PAYMENT_SWISH_NUMBER, "1234567890", SettingDataType.STRING, 0, 0
        )
        assert settings_manager.is_payment_method_ready() is True
