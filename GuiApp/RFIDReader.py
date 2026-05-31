import os
import platform
import threading

from kivy.clock import Clock
from logger import get_logger


logger = get_logger(__name__)


# TODO make better
def mock_gpio() -> bool:
    if platform.system() == "Windows":
        return True

    if os.getenv("MOCK_RFID_READER") in [
        "1",
        "y",
        "yes",
        "Y",
        "YES",
        "on",
        "ON",
        "true",
        "True",
        "TRUE",
    ]:
        return True

    if os.getenv("GITHUB_ACTIONS") == "true":
        return True

    return False


if mock_gpio():
    # Fake class for emulation
    class SimpleMFRC522:
        def read_id_no_block(self):
            pass

    class GPIO:
        @staticmethod
        def cleanup():
            logger.debug("GPIO cleanup called")

else:
    from mfrc522 import SimpleMFRC522
    from RPi import GPIO


class RFIDReader:
    def __init__(self):
        self.reader_thread = None
        self.running = threading.Event()
        self.last_read_id = None
        self.callback = None
        self._lock = threading.Lock()

    def triggerFakeRead(self, card_id="12345678"):
        """Trigger a fake RFID read."""
        with self._lock:
            if card_id is None:
                logger.warning("Will not trigger read, card_id is None")
                return

            if card_id == self.last_read_id:
                logger.warning("Will not trigger read, card_id is same as last")
                return

            if not self.callback:
                logger.warning("Will not trigger read, callback is None")
                return

            self.callback(card_id)
            self.last_read_id = card_id

    def start(self, callback_function):
        """Start the RFID reader in a separate thread."""
        self.callback = callback_function

        def reader_task():
            reader = SimpleMFRC522()
            try:
                while not self.running.is_set():
                    card_id = reader.read_id_no_block()
                    if card_id is not None and not isinstance(card_id, str):
                        card_id = str(card_id)
                    if (
                        card_id is not None
                        and card_id != self.last_read_id
                        and self.callback
                    ):
                        Clock.schedule_once(lambda dt: self.callback(card_id), 0)
                        self.last_read_id = card_id
                    self.running.wait(0.1)  # Add a small sleep to reduce CPU load
            except RuntimeError as e:
                logger.error("RFID runtime error: %s", e, exc_info=True)
            except IOError as e:
                logger.error("RFID I/O error: %s", e, exc_info=True)
            finally:
                if platform.system() != "Windows":
                    GPIO.cleanup()

        logger.info("RFID reader thread starting...")
        self.clearLastReadId()
        self.running.clear()
        self.reader_thread = threading.Thread(
            target=reader_task, daemon=True, name="RFID reader thread"
        )
        self.reader_thread.start()
        logger.info("RFID reader thread started")

    def stop(self):
        """Stop the RFID reader."""
        logger.info("Stopping RFID reader...")
        self.running.set()
        if self.reader_thread and self.reader_thread.is_alive():
            self.reader_thread.join()
        if platform.system() != "Windows":
            GPIO.cleanup()
        self.clearLastReadId()
        self.callback = None
        logger.info("RFID reader stopped")

    def clearLastReadId(self):
        self.last_read_id = None
