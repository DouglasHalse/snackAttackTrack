import os
import platform
import threading
import time


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
            time.sleep(1)

    class GPIO:
        @staticmethod
        def cleanup():
            print("GPIO::cleanup")

else:
    from mfrc522 import SimpleMFRC522
    from RPi import GPIO


class RFIDReader:
    def __init__(self):
        self.reader_thread = None
        self.running = threading.Event()
        self.last_read_id = None
        self.callback = None

    def triggerFakeRead(self):
        """Trigger a fake RFID read."""
        card_id = "12345678"
        if card_id is None:
            print("Will not trigger read, card_id is None")
            return

        if card_id == self.last_read_id:
            print("Will not trigger read, card_id is is same as last")
            return

        if not self.callback:
            print("Will not trigger read, callback is None")
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
                    if (
                        card_id is not None
                        and card_id != self.last_read_id
                        and self.callback
                    ):
                        self.callback(card_id)
                        self.last_read_id = card_id
                    time.sleep(0.1)  # Add a small sleep to reduce CPU load
            except RuntimeError as e:
                print(f"Runtime error reading RFID: {e}")
            except IOError as e:
                print(f"I/O error reading RFID: {e}")
            finally:
                if platform.system() != "Windows":
                    GPIO.cleanup()

        self.clearLastReadId()
        self.running.clear()
        self.reader_thread = threading.Thread(
            target=reader_task, daemon=True, name="RFID reader thread"
        )
        self.reader_thread.start()

    def stop(self):
        """Stop the RFID reader."""
        self.running.set()
        if self.reader_thread and self.reader_thread.is_alive():
            self.reader_thread.join()
        if platform.system() != "Windows":
            GPIO.cleanup()
        self.clearLastReadId()
        self.callback = None

    def clearLastReadId(self):
        self.last_read_id = None
