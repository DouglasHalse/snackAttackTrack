"""
Create User Screen — registration form with RFID card support.

Replaces the Kivy ``CreateUserScreen``.
"""

import sys
import os

_gui_app_dir = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "..", "..", "GuiApp"
)
if _gui_app_dir not in sys.path:
    sys.path.insert(0, os.path.abspath(_gui_app_dir))

# pylint: disable=wrong-import-position,too-many-instance-attributes,too-many-statements,duplicate-code

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from logger import get_logger

logger = get_logger(__name__)


class CreateUserScreen(QWidget):
    """User registration screen with form fields and RFID support.

    ``objectName`` is ``"createUserScreen"``.

    Widget ``objectName`` values for test access:
        - ``firstNameInput``
        - ``lastNameInput``
        - ``cardIdInput``
        - ``cancelButton``
        - ``registerButton``
    """

    def __init__(self, state_manager, parent=None):
        super().__init__(parent)
        self.setObjectName("createUserScreen")
        self._state_manager = state_manager
        self._rfid_callback = None
        self._setup_ui()

    def _setup_ui(self):
        """Build the widget tree matching Kivy proportions:
        10% spacers, 20% title, auto-height form, button row.
        """
        self.setStyleSheet("background-color: #A5E7EA;")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # ── 10% top spacer ──────────────────────────────────────────────────
        self._top_spacer = QWidget(self)
        self._top_spacer.setObjectName("topSpacer")
        self._top_spacer.setStyleSheet("background-color: transparent;")
        self._top_spacer.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )
        layout.addWidget(self._top_spacer)

        # ── Title (20% height in Kivy) ──────────────────────────────────────
        self._title_label = QLabel("Create New User", self)
        self._title_label.setObjectName("titleLabel")
        self._title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._title_label.setStyleSheet(
            "font-weight: bold; color: black; background-color: transparent;"
        )
        layout.addWidget(self._title_label)

        # ── 10% spacer ───────────────────────────────────────────────────────
        self._mid_top_spacer = QWidget(self)
        self._mid_top_spacer.setStyleSheet("background-color: transparent;")
        self._mid_top_spacer.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )
        layout.addWidget(self._mid_top_spacer)

        # ── Form fields ──────────────────────────────────────────────────────
        form_row = QWidget(self)
        form_row.setObjectName("formRow")
        form_row.setStyleSheet("background-color: transparent;")
        form_row_layout = QHBoxLayout(form_row)
        form_row_layout.setContentsMargins(0, 0, 0, 0)

        # 10% horizontal spacer on left
        self._form_left_spacer = QWidget(form_row)
        self._form_left_spacer.setStyleSheet("background-color: transparent;")
        self._form_left_spacer.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred
        )
        form_row_layout.addWidget(self._form_left_spacer)

        # Form card — rounded rectangle background
        form_card = QWidget(form_row)
        form_card.setObjectName("formCard")
        form_card.setStyleSheet(
            """
            QWidget#formCard {
                background-color: #087F8C; border-radius: 16px;
            }
        """
        )
        form_card_layout = QVBoxLayout(form_card)
        form_card_layout.setSpacing(12)
        form_card_layout.setContentsMargins(30, 24, 30, 24)

        # First name
        self._first_name_input = self._make_input(
            form_card, "firstNameInput", "First name", "Enter first name"
        )
        form_card_layout.addWidget(self._first_name_input)

        # Last name
        self._last_name_input = self._make_input(
            form_card, "lastNameInput", "Last name", "Enter last name"
        )
        form_card_layout.addWidget(self._last_name_input)

        # Card ID (read-only, populated by RFID)
        self._card_id_input = self._make_input(
            form_card, "cardIdInput", "Login card", "Tap card to register (optional)"
        )
        self._card_id_input.setReadOnly(True)
        self._card_id_input.setStyleSheet(
            self._card_id_input.styleSheet()
            + """
            QLineEdit { background-color: #D0F0F2; color: #555; }
        """
        )
        form_card_layout.addWidget(self._card_id_input)

        form_row_layout.addWidget(form_card)

        # 10% horizontal spacer on right
        self._form_right_spacer = QWidget(form_row)
        self._form_right_spacer.setStyleSheet("background-color: transparent;")
        self._form_right_spacer.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred
        )
        form_row_layout.addWidget(self._form_right_spacer)

        layout.addWidget(form_row)

        # ── 10% spacer ───────────────────────────────────────────────────────
        self._mid_bottom_spacer = QWidget(self)
        self._mid_bottom_spacer.setStyleSheet("background-color: transparent;")
        self._mid_bottom_spacer.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )
        layout.addWidget(self._mid_bottom_spacer)

        # ── Buttons ──────────────────────────────────────────────────────────
        self._btn_row = QWidget(self)
        self._btn_row.setObjectName("buttonRow")
        self._btn_row.setStyleSheet("background-color: transparent;")
        btn_row_layout = QHBoxLayout(self._btn_row)
        btn_row_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        btn_row_layout.setSpacing(40)

        # Cancel
        self._cancel_btn = QPushButton("Cancel", self._btn_row)
        self._cancel_btn.setObjectName("cancelButton")
        self._cancel_btn.setStyleSheet(
            """
            QPushButton {
                background-color: #FFC145; border-radius: 12px;
                font-size: 18px; font-weight: bold; color: black;
            }
            QPushButton:hover { background-color: #FFB322; }
        """
        )
        self._cancel_btn.clicked.connect(self._on_cancel)
        btn_row_layout.addWidget(self._cancel_btn)

        # Register
        self._register_btn = QPushButton("Register", self._btn_row)
        self._register_btn.setObjectName("registerButton")
        self._register_btn.setStyleSheet(
            """
            QPushButton {
                background-color: #5CB338; border-radius: 12px;
                font-size: 18px; font-weight: bold; color: white;
            }
            QPushButton:hover { background-color: #4A9A2E; }
        """
        )
        self._register_btn.clicked.connect(self._register_user)
        btn_row_layout.addWidget(self._register_btn)

        layout.addWidget(self._btn_row)

        # ── 10% bottom spacer ────────────────────────────────────────────────
        self._bottom_spacer = QWidget(self)
        self._bottom_spacer.setObjectName("bottomSpacer")
        self._bottom_spacer.setStyleSheet("background-color: transparent;")
        self._bottom_spacer.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )
        layout.addWidget(self._bottom_spacer)

    def resizeEvent(self, event):
        """Scale dimensions to match Kivy proportions."""
        w = self.width()
        h = self.height()

        # Title font: min(height/1.3, width/15) — matching Kivy
        title_font = max(14, min(int(h / 1.3), int(w / 15)))
        self._title_label.setStyleSheet(
            f"font-size: {title_font}px; font-weight: bold; color: black; "
            f"background-color: transparent;"
        )

        # Buttons: width = parent.width/3, height = width/3 (matching Kivy)
        btn_w = max(60, w // 3)
        btn_h = btn_w  # square buttons
        for btn in [self._cancel_btn, self._register_btn]:
            btn.setFixedSize(btn_w, btn_h)
            font_px = max(10, btn_h // 2)
            if "Cancel" in btn.text():
                btn.setStyleSheet(
                    f"""
                    QPushButton {{
                        background-color: #FFC145; border-radius: 12px;
                        font-size: {font_px}px; font-weight: bold; color: black;
                    }}
                    QPushButton:hover {{ background-color: #FFB322; }}
                """
                )
            else:
                btn.setStyleSheet(
                    f"""
                    QPushButton {{
                        background-color: #5CB338; border-radius: 12px;
                        font-size: {font_px}px; font-weight: bold; color: white;
                    }}
                    QPushButton:hover {{ background-color: #4A9A2E; }}
                """
                )

        # Input font size: parent.width / 25 (matching Kivy's size_factor)
        input_font = max(10, w // 25)
        for obj_name in ["firstNameInput", "lastNameInput", "cardIdInput"]:
            inp = self.findChild(QLineEdit, obj_name)
            if inp:
                inp.setStyleSheet(
                    inp.styleSheet()
                    + f"""
                    QLineEdit {{
                        font-size: {input_font}px;
                    }}
                """
                )

        super().resizeEvent(event)

    @staticmethod
    def _make_input(parent, obj_name: str, header: str, placeholder: str) -> QLineEdit:
        """Create a labelled text input."""
        container = QWidget(parent)
        container.setStyleSheet("background-color: transparent;")
        clayout = QVBoxLayout(container)
        clayout.setContentsMargins(0, 0, 0, 0)
        clayout.setSpacing(4)

        label = QLabel(header, container)
        label.setStyleSheet(
            "font-size: 14px; font-weight: bold; color: white; background: transparent;"
        )
        clayout.addWidget(label)

        inp = QLineEdit(container)
        inp.setObjectName(obj_name)
        inp.setPlaceholderText(placeholder)
        inp.setMinimumHeight(40)
        inp.setStyleSheet(
            """
            QLineEdit {
                background-color: white; border-radius: 8px;
                padding: 8px 12px; font-size: 16px; color: black;
                border: 2px solid #065F6A;
            }
            QLineEdit:focus { border-color: #5CB338; }
        """
        )
        clayout.addWidget(inp)

        return inp

    # ---- Lifecycle -----------------------------------------------------------

    def on_show(self):
        """Called just before the screen becomes visible."""
        logger.debug("CreateUserScreen on_show")
        self._rfid_callback = self._on_card_read
        self._state_manager.start_rfid(self._rfid_callback)

    def on_hide(self):
        """Called when transitioning away from this screen."""
        logger.debug("CreateUserScreen on_hide")
        self._state_manager.stop_rfid(self._rfid_callback)
        self._rfid_callback = None
        self._clear_inputs()

    # ---- Public helpers -----------------------------------------------------

    def set_card_id(self, card_id: str):
        """Populate the card ID field (called by RFID or from other screens)."""
        self._card_id_input.setText(str(card_id))

    # ---- Registration -------------------------------------------------------

    def _register_user(self):
        """Validate fields and create the user."""
        first_name = self._first_name_input.text().strip()
        last_name = self._last_name_input.text().strip()
        card_id = self._card_id_input.text().strip()

        # Validation
        if not first_name:
            self._show_error("First Name cannot be empty")
            return
        if not last_name:
            self._show_error("Last Name cannot be empty")
            return
        if card_id:
            existing_patron_id = self._state_manager.database.getPatronIdByCardId(
                card_id
            )
            if existing_patron_id is not None:
                patron = self._state_manager.database.getPatronData(existing_patron_id)
                name = f"{patron.firstName} {patron.lastName}" if patron else "unknown"
                self._show_error(f"Card ID is already used by {name}")
                self._card_id_input.setText("")
                return

        # Create user
        self._state_manager.database.addPatron(first_name, last_name, card_id)
        logger.info(
            "User created: firstName='%s' lastName='%s' cardId='%s'",
            first_name,
            last_name,
            card_id,
        )

        self._state_manager.transition_to_screen("loginScreen")

    # ---- Navigation ---------------------------------------------------------

    def _on_cancel(self):
        """Return to the login screen."""
        self._state_manager.transition_to_screen("loginScreen")

    # ---- RFID ---------------------------------------------------------------

    def _on_card_read(self, card_id: str):
        """Populate the card ID field when a card is scanned."""
        logger.debug("CreateUserScreen card read: %s", card_id)
        self._card_id_input.setText(str(card_id))

    # ---- Helpers ------------------------------------------------------------

    def _clear_inputs(self):
        """Clear all form fields."""
        self._first_name_input.clear()
        self._last_name_input.clear()
        self._card_id_input.clear()

    _active_msg_box = None
    last_error = ""

    def _show_error(self, message: str):
        """Show an error message popup (replaces Kivy ErrorMessagePopup)."""
        self.last_error = message
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Error")
        msg_box.setText(message)
        msg_box.setIcon(QMessageBox.Icon.Warning)
        msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg_box.setModal(False)
        msg_box.show()
