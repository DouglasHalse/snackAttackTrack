from kivy.uix.screenmanager import Screen

from database import addPatron


class CreateUserScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def registerUser(self):
        """Handle the registration logic."""
        registerFirstName = self.ids.registerFirstName.text.strip()
        registerLastName = self.ids.registerLastName.text.strip()
        registerEmployeeID = self.ids.registerEmployeeID.text.strip()

        # Check for empty fields and show error messages
        if not registerFirstName:
            self.ids.errorMessage.text = "First Name cannot be empty!"
            self.ids.errorMessage.opacity = 1
        elif not registerLastName:
            self.ids.errorMessage.text = "Last Name cannot be empty!"
            self.ids.errorMessage.opacity = 1
        else:
            self.ids.errorMessage.opacity = 0
            print(f"Registering user: {registerFirstName} {registerLastName}")
            if registerEmployeeID:
                print(f"Employee ID: {registerEmployeeID}")
            else:
                print("No Employee ID provided.")

            addPatron(registerFirstName, registerLastName, registerEmployeeID)

            self.manager.current = "loginScreen"

    def cancel(self):
        """Handle the cancel action."""

        self.ids.registerFirstName.text = ""
        self.ids.registerLastName.text = ""
        self.ids.registerEmployeeID.text = ""
        self.ids.errorMessage.text = ""
        self.ids.errorMessage.opacity = 0

        self.manager.current = "loginScreen"
