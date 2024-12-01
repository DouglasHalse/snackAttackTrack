from unittest.mock import patch

from kivy.uix.screenmanager import ScreenManager
from kivy.lang import Builder

import pytest

from GuiApp.widgets.createUserScreen import CreateUserScreen
from GuiApp.widgets.loginScreen import LoginScreenWidget
from GuiApp.database import UserData


Builder.load_file("GuiApp/kv/createUserScreen.kv")
Builder.load_file("GuiApp/kv/loginScreen.kv")


@pytest.fixture(name="screen_manager")
@patch(
    "GuiApp.widgets.loginScreen.getAllPatrons",
    return_value=[UserData("0", "John", "Doe", "12345")],
)
def fixture_screen_manager(mock_get_all_patrons):
    """Fixture to set up a ScreenManager with CreateUserScreen."""
    sm = ScreenManager()

    create_user_screen = CreateUserScreen(name="createUserScreen")
    create_login_screen = LoginScreenWidget(name="loginScreen")

    # mock_get_all_patrons.getAllPatrons.assert_called_once() This should work, i just don't know why

    sm.add_widget(create_user_screen)
    sm.add_widget(create_login_screen)
    return sm


@patch("GuiApp.widgets.createUserScreen.addPatron")
def test_register_user(mock_add_patron, screen_manager):
    """Test the registration logic without touching the real database."""

    create_user_screen = screen_manager.get_screen("createUserScreen")

    # Simulate user input
    create_user_screen.ids.registerFirstName.text = "John"
    create_user_screen.ids.registerLastName.text = "Doe"
    create_user_screen.ids.registerEmployeeID.text = "12345"
    create_user_screen.ids.errorMessage.opacity = 0
    assert create_user_screen.ids.registerFirstName.text == "John"
    assert create_user_screen.ids.registerLastName.text == "Doe"
    assert create_user_screen.ids.registerEmployeeID.text == "12345"
    assert create_user_screen.ids.errorMessage.opacity == 0

    create_user_screen.registerUser()

    mock_add_patron.assert_called_with("John", "Doe", "12345")


@patch("GuiApp.widgets.createUserScreen.addPatron")
def test_register_user_first_name_missing(mock_add_patron, screen_manager):
    """First name is missing"""

    create_user_screen = screen_manager.get_screen("createUserScreen")

    create_user_screen.ids.registerLastName.text = "Doe"
    create_user_screen.ids.registerEmployeeID.text = "12345"
    create_user_screen.ids.errorMessage.opacity = 0
    assert create_user_screen.ids.registerLastName.text == "Doe"
    assert create_user_screen.ids.registerEmployeeID.text == "12345"
    assert create_user_screen.ids.errorMessage.opacity == 0

    create_user_screen.registerUser()

    assert create_user_screen.ids.errorMessage.opacity == 1
    assert create_user_screen.ids.errorMessage.text == "First Name cannot be empty!"


@patch("GuiApp.widgets.createUserScreen.addPatron")
def test_register_user_last_name_missing(mock_add_patron, screen_manager):
    """Last name is missing"""
    create_user_screen = screen_manager.get_screen("createUserScreen")

    create_user_screen.ids.registerFirstName.text = "John"
    create_user_screen.ids.registerEmployeeID.text = "12345"
    create_user_screen.ids.errorMessage.opacity = 0
    assert create_user_screen.ids.registerFirstName.text == "John"
    assert create_user_screen.ids.registerEmployeeID.text == "12345"
    assert create_user_screen.ids.errorMessage.opacity == 0

    create_user_screen.registerUser()

    assert create_user_screen.ids.errorMessage.opacity == 1
    assert create_user_screen.ids.errorMessage.text == "Last Name cannot be empty!"
