from kivy.uix.popup import Popup
from kivy.clock import Clock

from database import addPatron


class AddPatronPopup(Popup):
    def __init__(self, managePatronsPopup, snackAttackTrackWidget, **kwargs):
        super().__init__(**kwargs)
        self.managePatronsPopup = managePatronsPopup
        self.snackAttackTrackWidget = snackAttackTrackWidget

    def focus_text_input(self):
        self.ids.addPatronFirstNameInput.focus = True

    def on_open(self):
        self.ids.addPatronFirstNameInput.text = "EMFReader1"
        self.ids.addPatronLastNameInput.text = "LastName"
        self.ids.addPatronEmployeeIDInput.text = "1"
        Clock.schedule_once(self.focus_text_input, 0)

    def on_dismiss(self):
        self.managePatronsPopup.populatePatronsList()  # TODO inefficient but works
        return super().on_dismiss()

    def AddPatron(self):
        patronFirstName = self.ids.addPatronFirstNameInput.text
        patronLastName = self.ids.addPatronLastNameInput.text
        patronEmployeeID = self.ids.addPatronEmployeeIDInput.text
        print("Adding patron " + patronFirstName)
        addPatron(patronFirstName, patronLastName, patronEmployeeID)
