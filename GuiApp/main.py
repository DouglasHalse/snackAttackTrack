"""
SnackAttack Track - Main Application Entry Point

This is the main file that initializes and runs the SnackAttack Track application.
It sets up the Kivy app, loads all screens, configures settings, and handles keyboard shortcuts.

Key Components:
- snackAttackTrackApp: Main application class
- Settings management: Configurable app behavior
- Screen management: Navigation between different UI screens
- Color theming: Centralized color definitions
"""

import argparse

# Disable pylint warnings for imports that are used by .kv layout files
# These imports are necessary even though they're not explicitly called in Python
# pylint: disable=unused-import
import widgets.clickableTable  # Used in various .kv files for table displays
import widgets.uiElements.buttons  # Custom button widgets used in .kv files
import widgets.uiElements.layouts  # Custom layout widgets
import widgets.uiElements.navigationHeader  # Navigation header component
import widgets.uiElements.ParticleEmitter  # Particle effects for animations
import widgets.uiElements.StatsWidgets  # Statistics display widgets
import widgets.uiElements.textInputs  # Custom text input fields
import widgets.uiElements.WheelOfSnacksWidget  # Gambling wheel widget
from database import DatabaseConnector  # SQLite database interface
from kivy.app import App  # Kivy application base class
from kivy.core.window import Window  # Window management
from kivy.lang import Builder  # KV language file loader
from kivy.modules import inspector  # Debug inspector (Ctrl+E)
from kivy.resources import resource_add_path  # Resource path configuration

# Import all screen widgets
# Each screen represents a different page in the application
from widgets.addSnackScreen import AddSnackScreen  # Add new snacks to inventory
from widgets.adminScreen import AdminScreen  # Admin control panel
from widgets.buyScreen import BuyScreen  # Purchase snacks screen
from widgets.createUserScreen import CreateUserScreen  # New user registration
from widgets.customScreenManager import CustomScreenManager  # Screen navigation manager
from widgets.editSnackScreen import EditSnackScreen  # Modify existing snack details
from widgets.editSnacksScreen import EditSnacksScreen  # View/manage all snacks
from widgets.editSystemSettingsScreen import (
    EditSystemSettingsScreen,  # System configuration
)
from widgets.editUserScreen import EditUserScreen  # Modify user details
from widgets.editUsersScreen import EditUsersScreen  # View/manage all users
from widgets.historyScreen import HistoryScreen  # Transaction history per user
from widgets.linkCardScreen import LinkCardScreen  # Link RFID card to account
from widgets.loginScreen import LoginScreen  # User login/authentication
from widgets.mainUserScreen import MainUserScreen  # Main menu after login
from widgets.ProfileScreen import ProfileScreen  # User profile and settings
from widgets.salesHistoryScreen import SalesHistoryScreen  # Store-wide sales history
from widgets.settingsManager import (  # App settings
    SettingDataType,
    SettingName,
    SettingsManager,
)
from widgets.splashScreen import SplashScreenWidget  # Startup splash screen
from widgets.StoreStatisticsScreen import StoreStatisticsScreen  # Store analytics
from widgets.topUpAmountScreen import TopUpAmountScreen  # Select top-up amount
from widgets.topUpPaymentScreen import TopUpPaymentScreen  # Payment confirmation
from widgets.UserStatisticsScreen import UserStatisticsScreen  # User analytics
from widgets.wheelOfSnacksScreen import WheelOfSnacksScreen  # Gambling/lucky wheel

# pylint: enable=unused-import

# Add GuiApp directory to resource path so Kivy can find assets
resource_add_path("GuiApp")


class snackAttackTrackApp(App):
    """
    Main application class for SnackAttack Track.

    This class initializes the entire application including:
    - Database connection
    - Settings management
    - Screen navigation
    - Color theme
    - Keyboard shortcuts

    Parameters:
        use_inspector (bool): Enable Kivy inspector for debugging (Ctrl+E)
        settings_path (str): Path to settings.json file
        database_path (str): Path to SQLite database file
    """

    def __init__(
        self,
        use_inspector=True,
        settings_path="settings.json",
        database_path="database.db",
    ):
        # Set application title (shown in window title bar)
        self.title = "Snack Attack Track"

        # Initialize settings manager with configuration file
        self.settingsManager = self.create_settings_manager(settings_path)

        # Initialize database connection
        self.database = DatabaseConnector(database_path=database_path)

        # Initialize screen manager for navigation between screens
        self.screenManager = CustomScreenManager(
            settingsManager=self.settingsManager, database=self.database
        )

        # Store inspector flag for debug mode
        self.use_inspector = use_inspector

        # Bind keyboard event handler for shortcuts
        Window.bind(on_key_down=self._on_keyboard_down)

        # Define color theme used throughout the application
        # Colors are in RGBA format (Red, Green, Blue, Alpha) with values 0-1
        # To change colors, modify the values below (e.g., for red: (1, 0, 0, 1))
        self.colors = {
            "background": (165 / 255, 231 / 255, 234 / 255, 1),  # Light cyan background
            "secondary_background": (8 / 255, 127 / 255, 140 / 255, 1),  # Dark teal
            "button": (252 / 255, 172 / 255, 196 / 255, 1),  # Pink for standard buttons
            "green_button": (
                92 / 255,
                179 / 255,
                56 / 255,
                1,
            ),  # Green for confirm actions
            "yellow_button": (236 / 255, 232 / 255, 82 / 255, 1),  # Yellow for warnings
            "orange_button": (255 / 255, 193 / 255, 69 / 255, 1),  # Orange for alerts
            "red_button": (251 / 255, 65 / 255, 65 / 255, 1),  # Red for cancel/delete
        }
        super().__init__()

    def _on_keyboard_down(self, _, keycode, _1, _2, _3):
        """
        Handle keyboard shortcuts for development and testing.

        Keyboard shortcuts:
        - F12: Take screenshot of current screen
        - F11: Trigger fake RFID card read (for testing without hardware)
        - F10: Toggle between window sizes (1280x800 and 800x480)

        To add new shortcuts, add another if statement with the keycode.
        """
        # F12 - Screenshot current screen
        if keycode == 293:
            Window.screenshot(name=self.screenManager.current + ".png")
            return True

        # F11 - Simulate RFID card read (useful for testing without RFID reader)
        if keycode == 292:
            self.screenManager.RFIDReader.triggerFakeRead()
            return True

        # F10 - Toggle window size (for testing different display sizes)
        if keycode == 291:
            if Window.size == (1280, 800):
                Window.size = (800, 480)  # Raspberry Pi touchscreen size
            else:
                Window.size = (1280, 800)  # Development size
            return True
        return False

    def create_settings_manager(self, settings_path: str) -> SettingsManager:
        """
        Initialize settings manager with all application settings.

        This method creates all configurable settings with their default values,
        data types, and allowed ranges. Settings are stored in settings.json.

        Parameters:
            settings_path: Path to JSON file for storing settings

        Returns:
            SettingsManager: Configured settings manager instance
        """
        sm = SettingsManager(settings_path)

        # SPILL_FACTOR: Multiplier for expected vs actual inventory usage
        # Used to account for spillage, waste, or theft
        # Example: 1.05 means 5% extra expected loss
        sm.add_setting_if_undefined(
            settingName=SettingName.SPILL_FACTOR,
            default_value=1.05,
            datatype=SettingDataType.FLOAT,
            min_value=1.0,  # 1.0 = no spillage
            max_value=10.0,  # 10.0 = 1000% spillage (extreme case)
        )

        # PURCHASE_FEE: Transaction fee as percentage (0.05 = 5%)
        # Applied to each purchase to cover operating costs
        sm.add_setting_if_undefined(
            settingName=SettingName.PURCHASE_FEE,
            default_value=0.05,  # 5% fee
            datatype=SettingDataType.FLOAT,
            min_value=0.0,  # No fee
            max_value=1.0,  # 100% fee
        )

        # AUTO_LOGOUT_ON_IDLE_ENABLE: Enable automatic logout after inactivity
        # Security feature to prevent unauthorized access
        sm.add_setting_if_undefined(
            settingName=SettingName.AUTO_LOGOUT_ON_IDLE_ENABLE,
            default_value=True,
            datatype=SettingDataType.BOOL,
            min_value=0,  # False
            max_value=1,  # True
        )

        # AUTO_LOGOUT_ON_IDLE_TIME: Seconds of inactivity before auto-logout
        # Only used if AUTO_LOGOUT_ON_IDLE_ENABLE is True
        sm.add_setting_if_undefined(
            settingName=SettingName.AUTO_LOGOUT_ON_IDLE_TIME,
            default_value=120.0,  # 2 minutes
            datatype=SettingDataType.FLOAT,
            min_value=20.0,  # 20 seconds minimum
            max_value=600.0,  # 10 minutes maximum
        )

        # AUTO_LOGOUT_AFTER_PURCHASE: Logout immediately after purchase
        # Useful for high-traffic environments
        sm.add_setting_if_undefined(
            settingName=SettingName.AUTO_LOGOUT_AFTER_PURCHASE,
            default_value=False,
            datatype=SettingDataType.BOOL,
            min_value=0,
            max_value=1,
        )

        # PAYMENT_SWISH_NUMBER: Phone number for Swish mobile payments
        # Used to generate QR code for top-up payments
        sm.add_setting_if_undefined(
            settingName=SettingName.PAYMENT_SWISH_NUMBER,
            default_value="0723071057",  # Swedish format
            datatype=SettingDataType.STRING,
            min_value=0,
            max_value=0,
        )

        # GO_TO_SPLASH_SCREEN_ON_IDLE_ENABLE: Return to splash screen when idle
        # Shows welcome screen when nobody is using the system
        sm.add_setting_if_undefined(
            settingName=SettingName.GO_TO_SPLASH_SCREEN_ON_IDLE_ENABLE,
            default_value=True,
            datatype=SettingDataType.BOOL,
            min_value=0,
            max_value=1,
        )

        # GO_TO_SPLASH_SCREEN_ON_IDLE_TIME: Seconds before returning to splash
        # Only used if GO_TO_SPLASH_SCREEN_ON_IDLE_ENABLE is True
        sm.add_setting_if_undefined(
            settingName=SettingName.GO_TO_SPLASH_SCREEN_ON_IDLE_TIME,
            default_value=10.0,  # 10 seconds
            datatype=SettingDataType.FLOAT,
            min_value=5.0,  # 5 seconds minimum
            max_value=600.0,  # 10 minutes maximum
        )

        # ORDER_INVENTORY_BY_MOST_PURCHASED: Sort snacks by popularity
        # If True, most-purchased items appear first in buy screen
        sm.add_setting_if_undefined(
            settingName=SettingName.ORDER_INVENTORY_BY_MOST_PURCHASED,
            default_value=True,
            datatype=SettingDataType.BOOL,
            min_value=0,
            max_value=1,
        )

        # ENABLE_GAMBLING: Allow users to gamble credits for random snacks
        # Enables "Wheel of Snacks" feature
        sm.add_setting_if_undefined(
            settingName=SettingName.ENABLE_GAMBLING,
            default_value=True,
            datatype=SettingDataType.BOOL,
            min_value=0,
            max_value=1,
        )

        # EXCITING_GAMBLING: Add spinning animation to gambling wheel
        # If False, wheel picks result instantly
        sm.add_setting_if_undefined(
            settingName=SettingName.EXCITING_GAMBLING,
            default_value=True,
            datatype=SettingDataType.BOOL,
            min_value=0,
            max_value=1,
        )

        # LOW_INVENTORY_THRESHOLD: Alert when stock falls below this number
        # Used to notify when reordering is needed
        sm.add_setting_if_undefined(
            settingName=SettingName.LOW_INVENTORY_THRESHOLD,
            default_value=5,  # Alert when 5 or fewer items remain
            datatype=SettingDataType.INT,
            min_value=0,  # No alerts
            max_value=100,  # Alert at 100 items
        )

        return sm

    def build(self):
        """
        Build and initialize the application UI.

        This method:
        1. Loads the main KV file for UI layout
        2. Registers all screens with the screen manager
        3. Enables Kivy inspector for debugging (if enabled)

        Returns:
            CustomScreenManager: The root widget containing all screens
        """
        # Load main KV file which imports all other KV layouts
        Builder.load_file("kv/main.kv")

        # Register all application screens
        # Each screen represents a different page/functionality
        self.screenManager.add_widget(
            SplashScreenWidget(name="splashScreen")
        )  # Welcome screen
        self.screenManager.add_widget(
            LoginScreen(name="loginScreen")
        )  # Login/RFID scan
        self.screenManager.add_widget(MainUserScreen(name="mainUserPage"))  # Main menu
        self.screenManager.add_widget(
            CreateUserScreen(name="createUserScreen")
        )  # Register account
        self.screenManager.add_widget(
            AdminScreen(name="adminScreen")
        )  # Admin dashboard
        self.screenManager.add_widget(
            EditSnacksScreen(name="editSnacksScreen")
        )  # Manage inventory
        self.screenManager.add_widget(
            EditUsersScreen(name="editUsersScreen")
        )  # Manage users
        self.screenManager.add_widget(
            AddSnackScreen(name="addSnackScreen")
        )  # Add new snack
        self.screenManager.add_widget(
            TopUpAmountScreen(name="topUpAmountScreen")
        )  # Select amount
        self.screenManager.add_widget(
            TopUpPaymentScreen(name="topUpPaymentScreen")
        )  # Payment QR
        self.screenManager.add_widget(BuyScreen(name="buyScreen"))  # Purchase snacks
        self.screenManager.add_widget(
            EditUserScreen(name="editUserScreen")
        )  # Edit user details
        self.screenManager.add_widget(
            HistoryScreen(name="historyScreen")
        )  # User transactions
        self.screenManager.add_widget(
            EditSnackScreen(name="editSnackScreen")
        )  # Edit snack details
        self.screenManager.add_widget(
            EditSystemSettingsScreen(name="editSystemSettingsScreen")  # System config
        )
        self.screenManager.add_widget(
            LinkCardScreen(name="linkCardScreen")
        )  # Link RFID card
        self.screenManager.add_widget(
            WheelOfSnacksScreen(name="wheelOfSnacksScreen")
        )  # Gambling
        self.screenManager.add_widget(
            ProfileScreen(name="profileScreen")
        )  # User profile
        self.screenManager.add_widget(
            UserStatisticsScreen(name="userStatisticsScreen")
        )  # User stats
        self.screenManager.add_widget(
            StoreStatisticsScreen(name="storeStatsScreen")
        )  # Store analytics
        self.screenManager.add_widget(
            SalesHistoryScreen(name="salesHistoryScreen")
        )  # All transactions

        # Enable Kivy inspector for debugging (Ctrl+E to toggle)
        if self.use_inspector:
            inspector.create_inspector(Window, self.screenManager)
        return self.screenManager

    def on_stop(self):
        """
        Cleanup when application is closing.

        Ensures database connection is properly closed to prevent corruption.
        """
        self.screenManager.database.close()
        return super().on_stop()


def main():
    """
    Main entry point for the application.

    Parses command-line arguments and starts the Kivy app.

    Command-line options:
        --no-inspector: Disable Kivy inspector (Ctrl+E)
        --rotate-screen: Rotate display 180 degrees (for upside-down mounting)
    """
    parser = argparse.ArgumentParser(description="Snack Attack Track Application")
    parser.add_argument(
        "--no-inspector", action="store_true", help="Run the app without the inspector"
    )
    parser.add_argument(
        "--rotate-screen",
        type=int,
        choices=range(0, 361),
        default=0,
        help="Rotate the screen by an angle between 0 and 360 degrees",
    )
    parser.add_argument("--hide-cursor", action="store_true", help="Hide the cursor")

    args = parser.parse_args()

    # Configure window for Raspberry Pi touchscreen (800x480)
    # This is the native resolution of the official Raspberry Pi 7" touchscreen
    Window.size = (800, 480)

    # Apply rotation if specified (useful for different mounting orientations)
    # Common values: 0 (normal), 90, 180 (upside-down), 270
    Window.rotation = args.rotate_screen

    # Hide/show cursor based on argument (typically hidden for touchscreen kiosk)
    Window.show_cursor = not args.hide_cursor

    # Create app instance with or without inspector
    if args.no_inspector:
        app = snackAttackTrackApp(use_inspector=False)
    else:
        app = snackAttackTrackApp(use_inspector=True)

    # Start the application main loop
    app.run()


if __name__ == "__main__":
    main()

    # Start the application main loop
    app.run()


if __name__ == "__main__":
    main()
