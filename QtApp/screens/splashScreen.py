"""
Splash Screen — the initial landing page of the Qt Snack Attack Track.

Displays an animated GIF background, the app logo, and a "Tap to login"
prompt.  Also listens for RFID card reads for automatic login or the
create/link-card dialog.

Replaces the Kivy ``SplashScreenWidget``.
"""

import sys
import os

_gui_app_dir = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "..", "..", "GuiApp"
)
if _gui_app_dir not in sys.path:
    sys.path.insert(0, os.path.abspath(_gui_app_dir))

# pylint: disable=wrong-import-position

from PySide6.QtCore import Qt
from PySide6.QtGui import QMovie, QPixmap
from PySide6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from logger import get_logger

logger = get_logger(__name__)


class SplashScreen(QWidget):
    """Splash screen with GIF background, logo, and RFID detection.

    ``objectName`` is ``"splashScreen"``.
    """

    def __init__(self, state_manager, parent=None):
        super().__init__(parent)
        self.setObjectName("splashScreen")
        self._state_manager = state_manager
        self._movie = None
        self._setup_ui()
        self._rfid_callback = None

    def _setup_ui(self):
        """Build the widget tree."""
        self.setStyleSheet("background-color: #A5E7EA;")

        # Determine image directory relative to this file
        base = os.path.dirname(os.path.abspath(__file__))
        # QtApp/screens/  ->  GuiApp/Images/
        images_dir = os.path.join(base, "..", "..", "GuiApp", "Images")
        self._images_dir = os.path.abspath(images_dir)
        bg_path = os.path.join(self._images_dir, "background.gif")
        logo_path = os.path.join(self._images_dir, "logo_type.png")

        # Main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Background GIF using QLabel with QMovie
        self._bg_label = QLabel(self)
        self._bg_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        if os.path.exists(bg_path):
            self._movie = QMovie(bg_path)
            self._bg_label.setMovie(self._movie)
            self._movie.start()
        else:
            self._bg_label.setText("(background.gif not found)")
            self._bg_label.setStyleSheet("color: black; font-size: 16px;")
        layout.addWidget(self._bg_label, stretch=1)

        # Overlay content centered
        overlay = QWidget(self)
        overlay.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, False)
        overlay_layout = QVBoxLayout(overlay)
        overlay_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Logo — scale to fill available width
        self._logo_label = QLabel(overlay)
        self._logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._logo_label.setStyleSheet("background-color: transparent;")
        if os.path.exists(logo_path):
            pixmap = QPixmap(logo_path)
            self._logo_label.setPixmap(
                pixmap.scaledToWidth(400, Qt.TransformationMode.SmoothTransformation)
            )
        else:
            self._logo_label.setText("(logo_type.png not found)")
        overlay_layout.addWidget(self._logo_label)

        # Vertical spacer (matches Kivy's Widget with size_hint: (1, 1))
        overlay_layout.addStretch(1)

        # Prompt text — font_size matches Kivy's self.width/28
        self._prompt_label = QLabel("Tap to login or create user...", overlay)
        self._prompt_label.setObjectName("promptLabel")
        self._prompt_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._prompt_label.setStyleSheet(
            "color: black; font-weight: bold; background-color: transparent;"
        )
        overlay_layout.addWidget(self._prompt_label)

        # Bottom spacer (matches Kivy's second Widget with size_hint: (1, 1))
        overlay_layout.addStretch(1)

        # Add overlay on top of background
        layout.addWidget(overlay, stretch=1)

    # ---- Lifecycle -----------------------------------------------------------

    def on_show(self):
        """Called just before the screen becomes visible.

        Starts the RFID reader and connects its signal.
        """
        logger.debug("SplashScreen on_show")
        if self._movie:
            self._movie.start()

        self._rfid_callback = self._on_card_read
        self._state_manager.start_rfid(self._rfid_callback)

    def on_hide(self):
        """Called when transitioning away from this screen.

        Stops the RFID reader and disconnects the callback.
        """
        logger.debug("SplashScreen on_hide")
        if self._movie:
            self._movie.stop()
        self._state_manager.stop_rfid(self._rfid_callback)
        self._rfid_callback = None

    # ---- Events --------------------------------------------------------------

    def resizeEvent(self, event):
        """Scale the prompt text font with the screen width, matching Kivy's
        ``font_size: self.width/28``."""
        font_size = max(12, self.width() // 28)
        self._prompt_label.setStyleSheet(
            f"color: black; font-size: {font_size}px; font-weight: bold; "
            f"background-color: transparent;"
        )
        super().resizeEvent(event)

    def mousePressEvent(self, event):
        """Handle taps/clicks — navigate to the login screen."""
        logger.debug("SplashScreen clicked — navigating to loginScreen")
        self._state_manager.transition_to_screen("loginScreen")
        super().mousePressEvent(event)

    # ---- RFID handling -------------------------------------------------------

    def _on_card_read(self, card_id: str):
        """Called when an RFID card is detected.

        If the card is known, log the user in and go to mainUserPage.
        If not, show the CreateUserOrLinkCardDialog.
        """
        logger.debug("SplashScreen card read: %s", card_id)
        patron_id = self._state_manager.database.getPatronIdByCardId(card_id)
        if patron_id is not None:
            self._state_manager.login(patron_id)
            self._state_manager.transition_to_screen("mainUserPage")
        else:
            self._show_create_or_link_dialog(card_id)

    def _show_create_or_link_dialog(self, card_id: str):
        """Show a dialog asking the user to create a new account or link the card."""
        dialog = QDialog(self)
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
        # Use show() instead of exec() to avoid blocking
        dialog.setModal(False)
        dialog.show()

    def _dialog_create_user(self, dialog: QDialog, card_id: str):
        """User chose to create a new account with the scanned card."""
        dialog.accept()
        create_screen = self._state_manager.get_screen("createUserScreen")
        if create_screen and hasattr(create_screen, "set_card_id"):
            create_screen.set_card_id(card_id)
        self._state_manager.transition_to_screen("createUserScreen")

    def _dialog_link_card(self, dialog: QDialog, card_id: str):
        """User chose to link the card to an existing account (stub)."""
        dialog.accept()
        logger.info("Link card %s — not yet implemented in PoC", card_id)
