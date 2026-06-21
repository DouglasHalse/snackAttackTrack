"""
Login Screen — user selection with horizontal carousel and alphabet quick-scroll.

Replaces the Kivy ``LoginScreen`` and ``LoginScreenUserWidget``.
"""

import sys
import os

_gui_app_dir = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "..", "..", "GuiApp"
)
if _gui_app_dir not in sys.path:
    sys.path.insert(0, os.path.abspath(_gui_app_dir))

# pylint: disable=wrong-import-position,too-many-instance-attributes,too-many-statements,duplicate-code

from PySide6.QtCore import Qt, QPropertyAnimation, QEvent
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from app_types import UserData
from logger import get_logger
from widgets.settingsManager import SettingName

logger = get_logger(__name__)

# ──────────────────────────────────────────────────────────────────────
# Constants
# ──────────────────────────────────────────────────────────────────────

_SCROLL_PX_THRESHOLD = 5  # pixels — distinguish tap from scroll
_ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"


# ──────────────────────────────────────────────────────────────────────
# UserWidget — a single user in the carousel
# ──────────────────────────────────────────────────────────────────────


class UserWidget(QPushButton):
    """A round-rectangle button showing a user's first and last name.

    Stores ``userData: UserData`` as an attribute for test access.
    Size is square (width = height) matching Kivy's ``width: self.height``.
    """

    def __init__(self, user_data: UserData, parent=None):
        super().__init__(parent)
        self.userData = user_data
        self.setObjectName(f"user_{user_data.patronId}")
        # Square size — will be updated when added to the carousel layout
        self.setFixedSize(140, 140)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setStyleSheet(
            """
            UserWidget {
                background-color: #087F8C;
                border-radius: 16px;
                border: 2px solid #065F6A;
                color: white;
                font-weight: bold;
            }
            UserWidget:hover {
                background-color: #0A9DA8;
            }
            UserWidget:pressed {
                background-color: #065F6A;
            }
        """
        )

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(2)

        self._first_name_label = QLabel(user_data.firstName, self)
        self._first_name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._first_name_label.setStyleSheet(
            "font-size: 14px; color: white; background: transparent; font-weight: bold;"
        )
        self._first_name_label.setWordWrap(True)
        layout.addWidget(self._first_name_label)

        self._last_name_label = QLabel(user_data.lastName, self)
        self._last_name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._last_name_label.setStyleSheet(
            "font-size: 12px; color: #D0F0F2; background: transparent; font-weight: bold;"
        )
        self._last_name_label.setWordWrap(True)
        layout.addWidget(self._last_name_label)


# ──────────────────────────────────────────────────────────────────────
# LoginScreen
# ──────────────────────────────────────────────────────────────────────


class LoginScreen(QWidget):
    """User selection screen with horizontal carousel and alphabet strip.

    ``objectName`` is ``"loginScreen"``.
    """

    def __init__(self, state_manager, parent=None):
        super().__init__(parent)
        self.setObjectName("loginScreen")
        self._state_manager = state_manager

        # Scroll-vs-tap detection state
        self._press_pos = None
        self.scroll_did_occur = False
        self._anim = None

        # Letter-to-widget map for alphabet quick-scroll
        self._letter_widget_map: dict[str, UserWidget] = {}

        # RFID callback reference (for disconnect)
        self._rfid_callback = None

        self._setup_ui()
        self._connect_signals()

    # ---- UI Construction ----------------------------------------------------

    def _setup_ui(self):
        """Build the full widget tree."""
        self.setStyleSheet("background-color: #A5E7EA;")

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 20)
        main_layout.setSpacing(0)

        # ── Top bar ──────────────────────────────────────────────────────────
        self._top_bar = QWidget(self)
        self._top_bar.setStyleSheet("background-color: transparent;")
        top_bar_layout = QHBoxLayout(self._top_bar)
        top_bar_layout.setContentsMargins(10, 0, 10, 0)

        # Back button (size set dynamically in resizeEvent)
        self._back_btn = QPushButton()
        self._back_btn.setObjectName("backButton")
        self._set_back_button_icon()
        top_bar_layout.addWidget(self._back_btn)

        # Title — dynamic font size in resizeEvent
        self._title_label = QLabel("Select user", self._top_bar)
        self._title_label.setObjectName("titleLabel")
        self._title_label.setStyleSheet(
            "font-weight: bold; color: black; "
            "background-color: transparent; padding-left: 20px;"
        )
        self._title_label.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred
        )
        top_bar_layout.addWidget(self._title_label)

        # Create new user button — dynamic width in resizeEvent
        self._create_btn = QPushButton("Create new user", self._top_bar)
        self._create_btn.setObjectName("createNewUserButton")
        top_bar_layout.addWidget(self._create_btn)

        main_layout.addWidget(self._top_bar)

        # ── Spacers around carousel ──────────────────────────────────────────
        self._top_spacer = QWidget(self)
        self._top_spacer.setStyleSheet("background-color: transparent;")
        self._top_spacer.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )
        main_layout.addWidget(self._top_spacer)

        # ── User carousel ────────────────────────────────────────────────────
        self._scroll_area = QScrollArea(self)
        self._scroll_area.setObjectName("userScrollArea")
        self._scroll_area.setWidgetResizable(True)
        self._scroll_area.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )
        self._scroll_area.setVerticalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )
        self._scroll_area.setStyleSheet(
            """
            QScrollArea { background-color: transparent; border: none; }
        """
        )
        # Height set dynamically in resizeEvent (150 * width / 800)
        self._scroll_area.setFixedHeight(150)

        self._carousel_content = QWidget(self._scroll_area)
        self._carousel_content.setStyleSheet("background-color: transparent;")
        self._scroll_area.viewport().installEventFilter(self)
        self._carousel_layout = QHBoxLayout(self._carousel_content)
        self._carousel_layout.setContentsMargins(10, 10, 10, 10)
        self._carousel_layout.setSpacing(15)
        self._carousel_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self._scroll_area.setWidget(self._carousel_content)
        main_layout.addWidget(self._scroll_area)

        # ── Bottom spacer ────────────────────────────────────────────────────
        self._bottom_spacer = QWidget(self)
        self._bottom_spacer.setStyleSheet("background-color: transparent;")
        self._bottom_spacer.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )
        main_layout.addWidget(self._bottom_spacer)

        # ── Alphabet strip ───────────────────────────────────────────────────
        self._alphabet_widget = QWidget(self)
        self._alphabet_widget.setObjectName("alphabetStrip")
        self._alphabet_widget.setStyleSheet("background-color: transparent;")
        alphabet_layout = QHBoxLayout(self._alphabet_widget)
        alphabet_layout.setContentsMargins(5, 5, 5, 5)
        alphabet_layout.setSpacing(2)
        alphabet_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        for letter in _ALPHABET:
            btn = QPushButton(letter, self._alphabet_widget)
            btn.setObjectName(f"letter_{letter}")
            btn.setFixedSize(28, 40)
            btn.setStyleSheet(
                """
                QPushButton {
                    background-color: #087F8C; border-radius: 6px;
                    font-size: 12px; font-weight: bold; color: white;
                }
                QPushButton:hover { background-color: #0A9DA8; }
            """
            )
            btn.clicked.connect(lambda checked, l=letter: self._on_alphabet_letter(l))
            alphabet_layout.addWidget(btn)

        main_layout.addWidget(self._alphabet_widget)

    def resizeEvent(self, event):
        """Scale dimensions proportionally to width, matching Kivy's sizing."""
        w = self.width()
        # Top bar height: width / 10 (matching Kivy's self.width / 10)
        bar_h = max(30, w // 10)
        self._top_bar.setFixedHeight(bar_h)

        # Back button is square
        self._back_btn.setFixedSize(bar_h, bar_h)
        self._back_btn.setStyleSheet(
            f"""
            QPushButton {{
                background-color: #FCACC4; border-radius: {bar_h//4}px;
                font-size: {bar_h//2}px; font-weight: bold; color: black;
            }}
            QPushButton:hover {{ background-color: #FD8EAC; }}
        """
        )

        # Title font size: height * 0.5 (matching Kivy's self.height * 0.5)
        title_font = max(10, int(bar_h * 0.5))
        self._title_label.setStyleSheet(
            f"font-size: {title_font}px; font-weight: bold; color: black; "
            f"background-color: transparent; padding-left: 20px;"
        )

        # Create button: width = height * 3 (matching Kivy)
        self._create_btn.setFixedWidth(max(60, bar_h * 3))
        create_font = max(8, bar_h // 3)
        self._create_btn.setStyleSheet(
            f"""
            QPushButton {{
                background-color: #087F8C; border-radius: 10px;
                font-size: {create_font}px; font-weight: bold; color: white;
                padding: 8px 16px;
            }}
            QPushButton:hover {{ background-color: #0A9DA8; }}
        """
        )

        # Carousel height: 150 * width / 800 (matching Kivy)
        carousel_h = int(150 * w / 800)
        self._scroll_area.setFixedHeight(max(80, carousel_h))

        super().resizeEvent(event)

    def _set_back_button_icon(self):
        """Set the back button icon from leftArrow.png if available."""
        base = os.path.dirname(os.path.abspath(__file__))
        arrow_path = os.path.abspath(
            os.path.join(base, "..", "..", "GuiApp", "Images", "leftArrow.png")
        )
        if os.path.exists(arrow_path):
            self._back_btn.setIcon(QIcon(arrow_path))
            self._back_btn.setText("")
        else:
            self._back_btn.setText("\u2190")

    def _connect_signals(self):
        """Wire up button clicks."""
        self._back_btn.clicked.connect(self._on_back)
        self._create_btn.clicked.connect(self._on_create_user)

    # ---- Lifecycle -----------------------------------------------------------

    def on_show(self):
        """Called just before the screen becomes visible."""
        logger.debug("LoginScreen on_show")
        self._load_users()

        # Start RFID
        self._rfid_callback = self._on_card_read
        self._state_manager.start_rfid(self._rfid_callback)

        # Schedule splash-screen return on idle
        if self._state_manager.settings_manager.get_setting_value(
            SettingName.GO_TO_SPLASH_SCREEN_ON_IDLE_ENABLE
        ):
            timeout = self._state_manager.settings_manager.get_setting_value(
                SettingName.GO_TO_SPLASH_SCREEN_ON_IDLE_TIME
            )
            self._state_manager.reset_splash_return_timer(timeout)

    def on_hide(self):
        """Called when transitioning away from this screen."""
        logger.debug("LoginScreen on_hide")
        self._state_manager.stop_rfid(self._rfid_callback)
        self._rfid_callback = None
        self._state_manager.stop_splash_return_timer()
        self._clear_users()

    # ---- User loading -------------------------------------------------------

    def _load_users(self):
        """Load all patrons from the database and populate the carousel."""
        self._clear_users()
        self._letter_widget_map.clear()

        users = self._state_manager.database.getAllPatrons()
        if not users:
            return

        users.sort(key=lambda u: u.firstName.lower())
        for user_data in users:
            widget = UserWidget(user_data)
            widget.clicked.connect(
                lambda checked, u=user_data: self._on_user_clicked(u)
            )
            self._carousel_layout.addWidget(widget)

            first_letter = user_data.firstName[0].upper()
            if first_letter not in self._letter_widget_map:
                self._letter_widget_map[first_letter] = widget

        self._update_alphabet_strip()

    def _clear_users(self):
        """Remove all user widgets from the carousel."""
        while self._carousel_layout.count():
            item = self._carousel_layout.takeAt(0)
            if item and item.widget():
                item.widget().deleteLater()

    # ---- User click ---------------------------------------------------------

    def _on_user_clicked(self, user_data: UserData):
        """Handle a user widget click — login and navigate to main page."""
        if self.scroll_did_occur:
            logger.debug(
                "Login click REJECTED for %s %s (patronId=%s) — scroll detected",
                user_data.firstName,
                user_data.lastName,
                user_data.patronId,
            )
            return
        logger.debug(
            "Login click ACCEPTED for %s %s (patronId=%s)",
            user_data.firstName,
            user_data.lastName,
            user_data.patronId,
        )
        self._state_manager.login(user_data.patronId)
        self._state_manager.transition_to_screen("mainUserPage")

    # ---- Mouse events — scroll vs tap detection -----------------------------

    def eventFilter(self, obj, event):
        """Intercept mouse events on the scroll area viewport for scroll detection."""
        if obj is self._scroll_area.viewport():
            if event.type() == QEvent.Type.MouseButtonPress:
                self.scroll_did_occur = False
                self._press_pos = event.position().toPoint()
                self._reset_splash_return_timer()
            elif event.type() == QEvent.Type.MouseMove:
                if self._press_pos is not None:
                    pos = event.position().toPoint()
                    dx = abs(pos.x() - self._press_pos.x())
                    if dx > _SCROLL_PX_THRESHOLD and not self.scroll_did_occur:
                        self.scroll_did_occur = True
                        logger.debug(
                            "Scroll flagged (dx=%d px, threshold=%d px)",
                            dx,
                            _SCROLL_PX_THRESHOLD,
                        )
            elif event.type() == QEvent.Type.MouseButtonRelease:
                self._press_pos = None
                self._reset_splash_return_timer()
        return super().eventFilter(obj, event)

    def mousePressEvent(self, event):
        """Record press position for scroll-vs-tap detection (background clicks)."""
        self.scroll_did_occur = False
        self._press_pos = event.position().toPoint()
        # Reset splash return timer
        self._reset_splash_return_timer()
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        """Detect if the drag exceeds the scroll threshold."""
        if self._press_pos is not None:
            pos = event.position().toPoint()
            dx = abs(pos.x() - self._press_pos.x())
            if dx > _SCROLL_PX_THRESHOLD and not self.scroll_did_occur:
                self.scroll_did_occur = True
                logger.debug(
                    "Scroll flagged (dx=%d px, threshold=%d px)",
                    dx,
                    _SCROLL_PX_THRESHOLD,
                )
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        """Reset press position."""
        self._press_pos = None
        # Reset splash return timer
        self._reset_splash_return_timer()
        super().mouseReleaseEvent(event)

    def _reset_splash_return_timer(self):
        """Reset the timer that returns to the splash screen."""
        if self._state_manager.settings_manager.get_setting_value(
            SettingName.GO_TO_SPLASH_SCREEN_ON_IDLE_ENABLE
        ):
            timeout = self._state_manager.settings_manager.get_setting_value(
                SettingName.GO_TO_SPLASH_SCREEN_ON_IDLE_TIME
            )
            self._state_manager.reset_splash_return_timer(timeout)

    # ---- Alphabet quick-scroll ----------------------------------------------

    def _update_alphabet_strip(self):
        """Enable/disable alphabet buttons based on available letters."""
        for letter in _ALPHABET:
            btn = self._alphabet_widget.findChild(QPushButton, f"letter_{letter}")
            if btn:
                has_users = letter in self._letter_widget_map
                btn.setEnabled(has_users)

    def _on_alphabet_letter(self, letter: str):
        """Scroll the carousel to center the first user with the given letter."""
        widget = self._letter_widget_map.get(letter)
        if widget is None:
            return
        logger.debug("Alphabet scroll to letter '%s'", letter)

        # Calculate target scroll position to center the widget
        scroll_bar = self._scroll_area.horizontalScrollBar()
        content_width = self._carousel_content.width()
        viewport_width = self._scroll_area.viewport().width()
        if content_width <= viewport_width:
            return

        widget_center = widget.x() + widget.width() // 2
        target = (widget_center - viewport_width // 2) / max(
            1, content_width - viewport_width
        )
        target = max(0, min(target, 1))
        target_value = int(target * scroll_bar.maximum())

        # Animate
        self._anim = QPropertyAnimation(scroll_bar, b"value")
        self._anim.setDuration(300)
        self._anim.setStartValue(scroll_bar.value())
        self._anim.setEndValue(target_value)
        self._anim.start()

    # ---- RFID ---------------------------------------------------------------

    def _on_card_read(self, card_id: str):
        """RFID callback — lookup user or show create/link dialog."""
        logger.debug("LoginScreen card read: %s", card_id)
        patron_id = self._state_manager.database.getPatronIdByCardId(card_id)
        if patron_id is not None:
            self._state_manager.login(patron_id)
            self._state_manager.transition_to_screen("mainUserPage")
        else:
            self._show_create_or_link_dialog(card_id)

    def _show_create_or_link_dialog(self, card_id: str):
        """Show a dialog for unknown card (same as splash screen)."""
        dialog = QDialog(self)  # pylint: disable=redefined-outer-name
        dialog.setWindowTitle("Card Not Found")
        dialog.setModal(True)
        dialog.setStyleSheet(
            """
            QDialog { background-color: #A5E7EA; }
            QLabel { font-size: 16px; color: black; }
            QPushButton {
                font-size: 14px; padding: 10px 20px; border-radius: 8px;
                font-weight: bold;
            }
        """
        )
        layout = QVBoxLayout(dialog)
        layout.setSpacing(15)

        msg = QLabel(f"No user found for card {card_id}.\nWhat would you like to do?")
        msg.setWordWrap(True)
        msg.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(msg)

        btn_layout = QHBoxLayout()
        create_btn = QPushButton("Create User")
        create_btn.setStyleSheet("background-color: #5CB338; color: white;")
        create_btn.clicked.connect(lambda: self._dialog_create_user(dialog, card_id))
        btn_layout.addWidget(create_btn)

        link_btn = QPushButton("Link Card")
        link_btn.setStyleSheet("background-color: #FCC1AC; color: black;")
        link_btn.clicked.connect(lambda: self._dialog_link_card(dialog, card_id))
        btn_layout.addWidget(link_btn)

        layout.addLayout(btn_layout)
        # Use open/show instead of exec() to avoid blocking
        dialog.setModal(False)
        dialog.show()

    def _dialog_create_user(self, dialog, card_id: str):
        dialog.accept()
        create_screen = self._state_manager.get_screen("createUserScreen")
        if create_screen and hasattr(create_screen, "set_card_id"):
            create_screen.set_card_id(card_id)
        self._state_manager.transition_to_screen("createUserScreen")

    def _dialog_link_card(self, dialog, card_id: str):
        dialog.accept()
        logger.info("Link card %s — not yet implemented in PoC", card_id)

    # ---- Navigation ---------------------------------------------------------

    def _on_back(self):
        """Navigate back to the splash screen."""
        self._state_manager.transition_to_screen("splashScreen")

    def _on_create_user(self):
        """Navigate to the create user screen."""
        self._state_manager.transition_to_screen("createUserScreen")
