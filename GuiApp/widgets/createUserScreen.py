import threading
# import RPi.GPIO as GPIO
# from mfrc522 import SimpleMFRC522
from kivy.uix.screenmanager import Screen
from widgets.popups.errorMessagePopup import ErrorMessagePopup
from database import addPatron

class CreateUserScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.reader_thread = None
        self.running = False
        self.cardId = None

    def start_reader(self):
        """Start the RFID reader in a separate thread."""
        def reader_task():
            # reader = SimpleMFRC522()
            try:
                while self.running:
                    # id, text = reader.read()
                    self.cardId = id
                    self.ids.cardIdInput.setText(str(id))  # Update the UI with the card ID
            except Exception as e:
                 print(f"Error reading RFID: {e}")
            # finally:
            #     GPIO.cleanup()

        self.running = True
        self.reader_thread = threading.Thread(target=reader_task, daemon=True)
        self.reader_thread.start()

    def stop_reader(self):
        """Stop the RFID reader."""
        self.running = False
        if self.reader_thread and self.reader_thread.is_alive():
            self.reader_thread.join()

    def on_enter(self, *args):
        """Start the RFID reader when the screen is entered."""
        super().on_enter(*args)
        self.start_reader()

    def registerUser(self):
        """Handle the registration logic."""
        firstName = self.ids.firstNameInput.getText()
        lastName = self.ids.lastNameInput.getText()
        cardId = self.cardId or self.ids.cardIdInput.getText()
        if firstName == "":
            ErrorMessagePopup(errorMessage="First Name cannot be empty").open()
            return

        if lastName == "":
            ErrorMessagePopup(errorMessage="Last Name cannot be empty").open()
            return
        #TODO: As an admin of the application register all the card that can be use to buy candies
        # and check here that the registered cardId match the save in the database.

        addPatron(firstName, lastName, cardId)

        self.manager.transitionToScreen("loginScreen", transitionDirection="right")

    def cancel(self):
        """Handle the cancel action."""
        self.manager.transitionToScreen("loginScreen", transitionDirection="right")

    def on_leave(self, *args):
        """Stop the RFID reader and clear the input fields when leaving the screen."""
        self.stop_reader()
        self.ids.firstNameInput.clearText()
        self.ids.lastNameInput.clearText()
        self.ids.cardIdInput.clearText()
        return super().on_leave(*args)


