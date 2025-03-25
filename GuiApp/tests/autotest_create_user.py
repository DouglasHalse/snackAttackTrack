import pytest
import asyncio
from autotest_utils import *
from database import *


@pytest.mark.asyncio
async def test_create_user_with_card(app_instance):
    """
    Test case to verify user creation functionality.
    """
    try:
        # Launch and configure the app
        await launch_and_configure_app(app_instance)

        # Perform actions in the app (e.g., tap on splash screen)
        await tap_on_splash_screen(app_instance)

        # Tap on the create user button
        await tap_on_create_user_button(app_instance)

        await focus_on_text_input_with_header(app_instance, "firstNameInput")
        await enter_text_in_text_input_with_header_popup(
            app_instance, "firstNameInput", "John"
        )
        await dismiss_text_input_with_header_popup(app_instance, "firstNameInput")
        assert (
            await get_text_from_input_with_header(app_instance, "firstNameInput")
            == "John"
        )

        await focus_on_text_input_with_header(app_instance, "lastNameInput")
        await enter_text_in_text_input_with_header_popup(
            app_instance, "lastNameInput", "Doe"
        )
        await dismiss_text_input_with_header_popup(app_instance, "lastNameInput")
        assert (
            await get_text_from_input_with_header(app_instance, "lastNameInput")
            == "Doe"
        )

        await fake_rfid_read(app_instance, "1234")
        assert (
            await get_text_from_input_with_header(app_instance, "cardIdInput") == "1234"
        )

        await tap_on_register_button(app_instance)

        patrons = getAllPatrons()

        assert len(patrons) == 1
        assert patrons[0].firstName == "John"
        assert patrons[0].lastName == "Doe"
        assert patrons[0].employeeID == "1234"
    finally:
        # Ensure the app is stopped
        await stop_app(app_instance)


@pytest.mark.asyncio
async def test_create_user_with_out_card(app_instance):
    """
    Test case to verify user creation functionality.
    """
    try:
        # Launch and configure the app
        await launch_and_configure_app(app_instance)

        # Perform actions in the app (e.g., tap on splash screen)
        await tap_on_splash_screen(app_instance)

        # Tap on the create user button
        await tap_on_create_user_button(app_instance)

        await focus_on_text_input_with_header(app_instance, "firstNameInput")
        await enter_text_in_text_input_with_header_popup(
            app_instance, "firstNameInput", "John"
        )
        await dismiss_text_input_with_header_popup(app_instance, "firstNameInput")
        assert (
            await get_text_from_input_with_header(app_instance, "firstNameInput")
            == "John"
        )

        await focus_on_text_input_with_header(app_instance, "lastNameInput")
        await enter_text_in_text_input_with_header_popup(
            app_instance, "lastNameInput", "Doe"
        )
        await dismiss_text_input_with_header_popup(app_instance, "lastNameInput")
        assert (
            await get_text_from_input_with_header(app_instance, "lastNameInput")
            == "Doe"
        )

        await tap_on_register_button(app_instance)

        patrons = getAllPatrons()

        assert len(patrons) == 1
        assert patrons[0].firstName == "John"
        assert patrons[0].lastName == "Doe"
    finally:
        # Ensure the app is stopped
        await stop_app(app_instance)
