"""
Qt-thread-safe adapter for the existing RFIDReader.

Wraps GuiApp.RFIDReader.RFIDReader so that card-read callbacks are
delivered via a Qt Signal instead of Kivy's ``Clock.schedule_once``.
The signal is automatically delivered on the main thread by Qt's event
loop, making it safe to emit from the reader thread.
"""

import sys
import os

# Ensure GuiApp is importable
_gui_app_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "GuiApp")
if _gui_app_dir not in sys.path:
    sys.path.insert(0, os.path.abspath(_gui_app_dir))

# pylint: disable=wrong-import-position

from PySide6.QtCore import QObject, Signal

from RFIDReader import RFIDReader as _RFIDReader
from logger import get_logger

logger = get_logger(__name__)


class RFIDAdapter(QObject):
    """Qt-aware wrapper around the existing RFIDReader.

    Usage::

        adapter = RFIDAdapter()
        adapter.card_read.connect(my_slot)
        adapter.start()
        ...
        adapter.stop()
    """

    # Emitted on the main thread when a card is read.
    # The payload is the card ID as a string.
    card_read = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._reader = _RFIDReader()
        # The slot that the reader thread calls.  We cannot pass a Python
        # lambda directly into the reader thread as a callback because
        # QObject must live in the creating thread for safe signal emission.
        # Instead we store a reference so triggerFakeRead can use it.
        self._callback = None

    # ---- Public API (mirrors RFIDReader) ---------------------------------

    def start(self, callback=None):
        """Start the RFID reader thread.

        Parameters
        ----------
        callback : callable or None
            If given, this callable is invoked **directly from the reader
            thread** with ``callback(card_id)``.  Prefer connecting to the
            ``card_read`` signal instead.
        """
        self._callback = callback
        if callback is None:
            # No explicit callback — use the signal as the delivery mechanism
            self._reader.start(self._on_card_read_signal)
        else:
            self._reader.start(self._on_card_read_bridge)

    def stop(self):
        """Stop the RFID reader thread."""
        self._reader.stop()

    def triggerFakeRead(self, card_id="12345678"):
        """Synthesize a fake card read (for testing / keyboard shortcut)."""
        self._reader.triggerFakeRead(card_id)

    def clearLastReadId(self):
        """Reset the last-read ID so the next read is not suppressed."""
        self._reader.last_read_id = None

    # ---- Internal helpers ------------------------------------------------

    def _on_card_read_signal(self, card_id: str):
        """Called by the reader thread — emits the Qt signal."""
        logger.debug("RFIDAdapter emitting card_read signal for %s", card_id)
        self.card_read.emit(card_id)

    def _on_card_read_bridge(self, card_id: str):
        """Called by the reader thread — calls the user-provided callback."""
        logger.debug("RFIDAdapter bridging card read %s to callback", card_id)
        if self._callback:
            self._callback(card_id)
