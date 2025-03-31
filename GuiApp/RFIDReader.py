import threading
import platform
import time
import os

if platform.system() == "Windows" or os.getenv("GITHUB_ACTIONS") == "true":
    # Fake class for emulation
    class SimpleMFRC522:
        def read_id_no_block(self):
            time.sleep(1)

    class GPIO:
        def cleanup(self):
            print("GPIO::cleanup")

else:
    from RPi import GPIO
    from mfrc522 import SimpleMFRC522


class RFIDReader:
    def __init__(self):
        self.reader_thread = None
        self.running = threading.Event()
        self.last_read_id = None
        self.callback = None

    def registerCallbackFunction(self, function):
        self.callback = function

    def triggerFakeRead(self):
        """Trigger a fake RFID read."""
        card_id = "12345678"
        print("triggering fake read with id 12345678")
        if card_id is not None and card_id != self.last_read_id and self.callback:
            self.callback(card_id)
            self.last_read_id = card_id

    def start(self):
        """Start the RFID reader in a separate thread."""

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
        self.last_read_id = None

    def clearLastReadId(self):
        self.last_read_id = None
