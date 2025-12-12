from kivy.uix.modalview import ModalView


class ChangePinPopup(ModalView):
    """Popup for changing user PIN."""

    def __init__(self, patron_id, screen_manager, **kwargs):
        super().__init__(**kwargs)
        self.patron_id = patron_id
        self.screen_manager = screen_manager
        self.current_pin = ""
        self.new_pin = ""
        self.confirm_pin = ""
        self.step = "current"  # current -> new -> confirm

    def on_number_pressed(self, number):
        """Handle numeric button presses."""
        if self.step == "current":
            if len(self.current_pin) < 4:
                self.current_pin += str(number)
                self.update_display()
                if len(self.current_pin) == 4:
                    self.verify_current_pin()
        elif self.step == "new":
            if len(self.new_pin) < 4:
                self.new_pin += str(number)
                self.update_display()
                if len(self.new_pin) == 4:
                    self.move_to_confirm()
        elif self.step == "confirm":
            if len(self.confirm_pin) < 4:
                self.confirm_pin += str(number)
                self.update_display()
                if len(self.confirm_pin) == 4:
                    self.verify_and_save()

    def on_backspace_pressed(self):
        """Handle backspace button press."""
        if self.step == "current" and len(self.current_pin) > 0:
            self.current_pin = self.current_pin[:-1]
        elif self.step == "new" and len(self.new_pin) > 0:
            self.new_pin = self.new_pin[:-1]
        elif self.step == "confirm" and len(self.confirm_pin) > 0:
            self.confirm_pin = self.confirm_pin[:-1]
        self.update_display()

    def on_clear_pressed(self):
        """Clear the entered PIN."""
        if self.step == "current":
            self.current_pin = ""
        elif self.step == "new":
            self.new_pin = ""
        elif self.step == "confirm":
            self.confirm_pin = ""
        self.update_display()

    def update_display(self):
        """Update the PIN display with dots."""
        if self.step == "current":
            self.ids.pin_display.text = "•" * len(self.current_pin)
            self.ids.title.text = "Enter Current PIN"
        elif self.step == "new":
            self.ids.pin_display.text = "•" * len(self.new_pin)
            self.ids.title.text = "Enter New PIN"
        elif self.step == "confirm":
            self.ids.pin_display.text = "•" * len(self.confirm_pin)
            self.ids.title.text = "Confirm New PIN"
        self.ids.error_label.text = ""

    def verify_current_pin(self):
        """Verify the current PIN is correct."""
        if self.screen_manager.database.verifyPatronPin(
            self.patron_id, self.current_pin
        ):
            # Current PIN is correct, move to new PIN entry
            self.step = "new"
            self.update_display()
        else:
            # Current PIN is incorrect
            self.ids.error_label.text = "Incorrect PIN. Try again."
            self.current_pin = ""
            self.update_display()

    def move_to_confirm(self):
        """Move to confirm PIN step."""
        self.step = "confirm"
        self.update_display()

    def verify_and_save(self):
        """Verify new PIN matches confirmation and save."""
        if self.new_pin != self.confirm_pin:
            self.ids.error_label.text = "PINs don't match. Try again."
            self.new_pin = ""
            self.confirm_pin = ""
            self.step = "new"
            self.update_display()
            return

        # Update PIN in database
        success = self.screen_manager.database.updatePatronPin(
            self.patron_id, self.new_pin
        )

        if success:
            self.dismiss()
            # Show success message
            from widgets.popups.errorMessagePopup import ErrorMessagePopup

            ErrorMessagePopup(errorMessage="PIN changed successfully!").open()
        else:
            self.ids.error_label.text = "Error updating PIN. Try again."
            self.new_pin = ""
            self.confirm_pin = ""
            self.step = "new"
            self.update_display()

    def on_cancel_pressed(self):
        """Handle cancel button press."""
        self.dismiss()
