from kivy.uix.modalview import ModalView


class AdminPinEntryPopup(ModalView):
    """Popup for entering admin PIN to access admin panel."""

    ADMIN_PIN = "4444"  # Admin PIN

    def __init__(self, screen_manager, on_success_callback=None, **kwargs):
        super().__init__(**kwargs)
        self.screen_manager = screen_manager
        self.on_success_callback = on_success_callback
        self.entered_pin = ""

    def on_number_pressed(self, number):
        """Handle numeric button presses."""
        if len(self.entered_pin) < 4:
            self.entered_pin += str(number)
            self.update_pin_display()

            # Auto-verify when 4 digits entered
            if len(self.entered_pin) == 4:
                self.verify_pin()

    def on_backspace_pressed(self):
        """Handle backspace button press."""
        if len(self.entered_pin) > 0:
            self.entered_pin = self.entered_pin[:-1]
            self.update_pin_display()

    def on_clear_pressed(self):
        """Clear the entered PIN."""
        self.entered_pin = ""
        self.update_pin_display()

    def update_pin_display(self):
        """Update the PIN display with dots."""
        self.ids.pin_display.text = "•" * len(self.entered_pin)
        self.ids.error_label.text = ""

    def verify_pin(self):
        """Verify the entered PIN against the admin PIN."""
        if self.entered_pin == self.ADMIN_PIN:
            # PIN is correct
            self.dismiss()
            if self.on_success_callback:
                self.on_success_callback()
        else:
            # PIN is incorrect
            self.ids.error_label.text = "Incorrect Admin PIN. Access Denied."
            self.entered_pin = ""
            self.update_pin_display()

    def on_cancel_pressed(self):
        """Handle cancel button press."""
        self.dismiss()
