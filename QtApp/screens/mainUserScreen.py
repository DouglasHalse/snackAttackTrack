"""
Main User Screen — the hub screen with navigation header and 4 option buttons.

Replaces the Kivy ``MainUserScreen``.
"""

import sys
import os

_gui_app_dir = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "..", "..", "GuiApp"
)
if _gui_app_dir not in sys.path:
    sys.path.insert(0, os.path.abspath(_gui_app_dir))

# pylint: disable=wrong-import-position,too-many-instance-attributes,too-many-statements,duplicate-code

from PySide6.QtCore import Qt, QTimer, QSize as QtCoreQSize
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from logger import get_logger
from widgets.settingsManager import SettingName

logger = get_logger(__name__)


class MainUserScreen(QWidget):
    """Hub screen shown after login with navigation and option buttons.

    ``objectName`` is ``"mainUserPage"``.

    Widget ``objectName`` values for test access:
        - ``backButton``
        - ``welcomeLabel``
        - ``creditsLabel``
        - ``debugTimerLabel``
        - ``logoutButton``
        - ``settingsButton``
        - ``gambleButton``
        - ``buyButton``
        - ``topUpButton``
        - ``profileButton``
    """

    def __init__(self, state_manager, parent=None):
        super().__init__(parent)
        self.setObjectName("mainUserPage")
        self._state_manager = state_manager
        self._debug_timer = QTimer(self)
        self._debug_timer.setInterval(100)
        self._debug_timer.timeout.connect(self._update_debug_display)
        self._setup_ui()
        self._connect_signals()

    def _setup_ui(self):
        """Build the full widget tree."""
        self.setStyleSheet("background-color: #A5E7EA;")

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # ── Navigation header (20% of screen height, matching Kivy) ─────────
        self._header = QWidget(self)
        self._header.setObjectName("navigationHeader")
        self._header.setStyleSheet("background-color: #64D6DB;")
        header_layout = QHBoxLayout(self._header)
        header_layout.setContentsMargins(10, 5, 10, 5)

        # Back button (square, uses leftArrow.png like Kivy)
        self._back_btn = QPushButton(self._header)
        self._back_btn.setObjectName("backButton")
        self._set_header_back_button_icon()
        header_layout.addWidget(self._back_btn)

        # Welcome + Credits labels
        labels_widget = QWidget(self._header)
        labels_widget.setStyleSheet("background-color: transparent;")
        labels_layout = QVBoxLayout(labels_widget)
        labels_layout.setContentsMargins(10, 0, 0, 0)
        labels_layout.setSpacing(2)

        self._welcome_label = QLabel("Welcome, Guest", labels_widget)
        self._welcome_label.setObjectName("welcomeLabel")
        self._welcome_label.setStyleSheet(
            "font-weight: bold; color: black; background: transparent;"
        )
        labels_layout.addWidget(self._welcome_label)

        self._credits_label = QLabel("Your credits: 0.00", labels_widget)
        self._credits_label.setObjectName("creditsLabel")
        self._credits_label.setStyleSheet(
            "font-weight: bold; color: black; background: transparent;"
        )
        labels_layout.addWidget(self._credits_label)

        header_layout.addWidget(labels_widget, stretch=1)

        # Debug timer label (hidden by default)
        self._debug_timer_label = QLabel("", self._header)
        self._debug_timer_label.setObjectName("debugTimerLabel")
        self._debug_timer_label.setStyleSheet(
            "font-weight: bold; color: #FF3333; background: transparent;"
        )
        self._debug_timer_label.setFixedWidth(160)
        self._debug_timer_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._debug_timer_label.setVisible(False)
        header_layout.addWidget(self._debug_timer_label)

        # Settings button (wrench icon, matching Kivy NavigationSettingsButton)
        self._settings_btn = QPushButton(self._header)
        self._settings_btn.setObjectName("settingsButton")
        self._set_settings_button_icon()
        header_layout.addWidget(self._settings_btn)

        # Logout button (RedButton, matching Kivy)
        self._logout_btn = QPushButton("Log out", self._header)
        self._logout_btn.setObjectName("logoutButton")
        self._logout_btn.setStyleSheet(
            """
            QPushButton {
                background-color: #FB4141; border-radius: 12px;
                font-size: 14px; font-weight: bold; color: white;
            }
            QPushButton:hover { background-color: #D93434; }
        """
        )
        header_layout.addWidget(self._logout_btn)

        main_layout.addWidget(self._header)

        # ── Option buttons grid (matching Kivy padding:30, spacing:30) ──────
        options_widget = QWidget(self)
        options_widget.setStyleSheet("background-color: transparent;")
        grid = QGridLayout(options_widget)
        grid.setContentsMargins(30, 30, 30, 30)
        grid.setSpacing(30)

        # Gamble
        self._gamble_btn = self._make_option_button(
            "gambleButton",
            "Gamble",
            "#FCACC4",
            os.path.join(self._images_dir(), "roulette.png"),
        )
        grid.addWidget(self._gamble_btn, 0, 0)

        # Buy
        self._buy_btn = self._make_option_button(
            "buyButton",
            "Buy",
            "#5CB338",
            os.path.join(self._images_dir(), "cart-shopping-fast.png"),
        )
        grid.addWidget(self._buy_btn, 0, 1)

        # Top-up
        self._top_up_btn = self._make_option_button(
            "topUpButton",
            "Top-up",
            "#FFC145",
            os.path.join(self._images_dir(), "money-income.png"),
        )
        grid.addWidget(self._top_up_btn, 1, 0)

        # Profile
        self._profile_btn = self._make_option_button(
            "profileButton",
            "Profile",
            "#087F8C",
            os.path.join(self._images_dir(), "user.png"),
        )
        grid.addWidget(self._profile_btn, 1, 1)

        main_layout.addWidget(options_widget, stretch=1)

    def resizeEvent(self, event):
        """Scale the navigation header and labels proportionally."""
        # Navigation header: 20% of screen height (matching Kivy's size_hint: 1, 0.2)
        header_h = max(40, int(self.height() * 0.2))
        self._header.setFixedHeight(header_h)

        # Back button square
        self._back_btn.setFixedSize(header_h, header_h)

        # Welcome/credits font: min(height/1.3, width/20) — matching Kivy
        label_font = max(10, min(int(header_h / 1.3), int(self.width() / 20)))
        self._welcome_label.setStyleSheet(
            f"font-size: {label_font}px; font-weight: bold; color: black; "
            f"background: transparent;"
        )
        self._credits_label.setStyleSheet(
            f"font-size: {label_font}px; font-weight: bold; color: black; "
            f"background: transparent;"
        )

        # Debug timer font: height / 5 — matching Kivy
        debug_font = max(8, header_h // 5)
        self._debug_timer_label.setStyleSheet(
            f"font-size: {debug_font}px; font-weight: bold; color: #FF3333; "
            f"background: transparent;"
        )

        # Settings button square
        self._settings_btn.setFixedSize(header_h, header_h)

        # Logout button: width = height * 2, font = height / 2 (matching Kivy)
        self._logout_btn.setFixedSize(header_h * 2, header_h)
        logout_font = max(8, header_h // 2)
        self._logout_btn.setStyleSheet(
            f"""
            QPushButton {{
                background-color: #FB4141; border-radius: 12px;
                font-size: {logout_font}px; font-weight: bold; color: white;
            }}
            QPushButton:hover {{ background-color: #D93434; }}
        """
        )

        super().resizeEvent(event)

    def _set_header_back_button_icon(self):
        """Set the back button icon from leftArrow.png like Kivy's NavigationBackButton."""
        base = os.path.dirname(os.path.abspath(__file__))
        arrow_path = os.path.abspath(
            os.path.join(base, "..", "..", "GuiApp", "Images", "leftArrow.png")
        )
        if os.path.exists(arrow_path):
            self._back_btn.setIcon(QIcon(arrow_path))
            self._back_btn.setText("")
        else:
            self._back_btn.setText("\u2190")

    def _set_settings_button_icon(self):
        """Set the settings button icon from wrench-alt.png like Kivy."""
        base = os.path.dirname(os.path.abspath(__file__))
        icon_path = os.path.abspath(
            os.path.join(base, "..", "..", "GuiApp", "Images", "wrench-alt.png")
        )
        if os.path.exists(icon_path):
            self._settings_btn.setIcon(QIcon(icon_path))
            self._settings_btn.setText("")
        else:
            self._settings_btn.setText("\u2699")

    @staticmethod
    def _images_dir() -> str:
        """Return the absolute path to the GuiApp/Images directory."""
        base = os.path.dirname(os.path.abspath(__file__))
        return os.path.abspath(os.path.join(base, "..", "..", "GuiApp", "Images"))

    @staticmethod
    def _make_option_button(
        obj_name: str, text: str, color: str, icon_path: str
    ) -> QPushButton:
        """Create a large styled option button with icon and text."""

        btn = QPushButton()
        btn.setObjectName(obj_name)
        btn.setMinimumSize(180, 160)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)

        # Set icon if the file exists
        if os.path.exists(icon_path):
            icon = QIcon(icon_path)
            btn.setIcon(icon)
            btn.setIconSize(QtCoreQSize(48, 48))

        btn.setStyleSheet(
            f"""
            QPushButton {{
                background-color: {color};
                border-radius: 20px;
                font-size: 18px;
                font-weight: bold;
                color: black;
                padding: 10px;
            }}
            QPushButton:hover {{
                background-color: #D0D0D0;
            }}
            QPushButton:disabled {{
                background-color: #CCCCCC;
                color: #888888;
            }}
        """
        )
        btn.setText(text)

        return btn

    def _connect_signals(self):
        """Wire up button clicks and state signals."""
        self._back_btn.clicked.connect(self._on_back)
        self._logout_btn.clicked.connect(self._on_logout)
        self._settings_btn.clicked.connect(self._on_settings)

        self._gamble_btn.clicked.connect(lambda: self._show_stub("Gamble"))
        self._buy_btn.clicked.connect(lambda: self._show_stub("Buy"))
        self._top_up_btn.clicked.connect(lambda: self._show_stub("Top-up"))
        self._profile_btn.clicked.connect(lambda: self._show_stub("Profile"))

        # Listen for state changes
        self._state_manager.logged_in_user_changed.connect(self._on_user_changed)

    # ---- Lifecycle -----------------------------------------------------------

    def on_show(self):
        """Refresh data when the screen becomes visible."""
        logger.debug("MainUserScreen on_show")
        self._state_manager.refresh_current_patron()
        self._update_gamble_state()

        # Start debug timer if enabled
        if self._state_manager.settings_manager.get_setting_value(
            SettingName.DEBUG_AUTO_LOGOUT_TIMER
        ):
            self._debug_timer_label.setVisible(True)
            self._debug_timer.start()

    def on_hide(self):
        """Clean up when leaving this screen."""
        logger.debug("MainUserScreen on_hide")
        self._debug_timer.stop()
        self._debug_timer_label.setVisible(False)

    # ---- State reactions ----------------------------------------------------

    def _on_user_changed(self, patron):
        """Update welcome and credits labels when the user changes."""
        if patron is not None:
            self._welcome_label.setText(f"Welcome, {patron.firstName}")
            self._credits_label.setText(f"Your credits: {patron.totalCredits}")
        else:
            self._welcome_label.setText("Welcome, Guest")
            self._credits_label.setText("Your credits: 0.00")

    def _update_gamble_state(self):
        """Enable/disable the gamble button based on settings and snack count."""
        gamble_enabled = self._state_manager.settings_manager.get_setting_value(
            SettingName.ENABLE_GAMBLING
        )
        if not gamble_enabled:
            self._gamble_btn.setEnabled(False)
            return
        snacks = self._state_manager.database.getAllSnacks()
        self._gamble_btn.setEnabled(len(snacks) >= 2)

    # ---- Navigation ---------------------------------------------------------

    def _on_back(self):
        """Go back to login screen (also logs out)."""
        self._state_manager.logout()
        self._state_manager.transition_to_screen("loginScreen")

    def _on_logout(self):
        """Log out and return to login screen."""
        self._state_manager.logout()
        self._state_manager.transition_to_screen("loginScreen")

    def _on_settings(self):
        """Settings button — stub for PoC."""
        self._show_stub("Settings")

    def _show_stub(self, feature: str):
        """Show a stub message for unimplemented features."""
        QMessageBox.information(
            self,
            "Not Implemented",
            f"{feature} is not implemented in this proof of concept.",
        )

    # ---- Debug timer display ------------------------------------------------

    def _update_debug_display(self):
        """Update the debug auto-logout countdown label."""
        remaining = self._state_manager.debug_remaining
        if remaining > 0:
            self._debug_timer_label.setText(f"Auto-logout: {remaining:.0f}s")
            self._debug_timer_label.setVisible(True)
        else:
            self._debug_timer_label.setVisible(False)
