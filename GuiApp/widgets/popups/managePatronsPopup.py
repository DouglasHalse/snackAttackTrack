from kivy.uix.popup import Popup
from kivy.uix.label import Label

from .addPatronPopup import AddPatronPopup

from database import getAllPatrons


class ManagePatronsPopup(Popup):
    def __init__(self, snackAttackTrackWidget,  **kwargs):
        super(ManagePatronsPopup, self).__init__(**kwargs)
        self.snackAttackTrackWidget = snackAttackTrackWidget

    def OnAddDeviceButtonPressed(self, *largs):
        addPatronPopup = AddPatronPopup(managePatronsPopup=self, snackAttackTrackWidget=self.snackAttackTrackWidget)
        addPatronPopup.open()
    
    def populatePatronsList(self):
        grid = self.ids.manageDevicesAddedDevicesGridListContent
        grid.clear_widgets()

        for patron in getAllPatrons():
            name_label = Label(
                text=f"{patron[1]} {patron[2]}",
                size_hint=(None, None),
                size=(130, 50),
                halign="left",
                valign="middle",
                text_size=(130, 50),
            )
            sub_end_label = Label(
                text="Not known",
                size_hint=(None, None),
                size=(150, 50),
                halign="left",
                valign="middle",
                text_size=(150, 50),
            )
            current_sub_label = Label(
                text="Not known",
                size_hint=(None, None),
                size=(150, 50),
                halign="left",
                valign="middle",
                text_size=(150, 50),
            )

            grid.add_widget(name_label)
            grid.add_widget(sub_end_label)
            grid.add_widget(current_sub_label)
            
