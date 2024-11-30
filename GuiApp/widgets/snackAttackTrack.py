from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup

from .patronRow import PatronRowWidget
from .deviceRow import DeviceRowWidget
from .popups.managePatronsPopup import ManagePatronsPopup
from .popups.abortPopup import AboutPopup

class SnackAttackTrackWidget(BoxLayout):
    def __init__(self, **kwargs):
        super(SnackAttackTrackWidget, self).__init__(**kwargs)

    def AddNewPatronWidget(self, firstName, lastName, employeeID):
        newPatronWidget = PatronRowWidget(firstName, lastName, employeeID)
        self.ids.deviceList.add_widget(newPatronWidget)

    def AddNewDeviceInfoWidget(self, deviceType, deviceName):
        # If no added devices widget is in the list, remove it
        if self.noAddedDeviceWidget in self.ids.deviceList.children:
            self.ids.deviceList.remove_widget(self.noAddedDeviceWidget)
        # Add new device info widget
        newDeviceRowWidget = DeviceRowWidget(deviceName=deviceName)
        self.ids.deviceList.add_widget(newDeviceRowWidget)

    def RemoveDeviceInfoWidget(self, deviceName):
        for deviceRowWidget in self.ids.deviceList.children:
            if deviceRowWidget.baseDeviceInfoWidget.labelWidget.ids.deviceName.text == deviceName:
                self.ids.deviceList.remove_widget(deviceRowWidget)
        if len(self.ids.deviceList.children) == 0:
            self.ids.deviceList.add_widget(self.noAddedDeviceWidget)
        return

    def OnManagePatronsButtonPressed(self, *largs):
        managePatronsPopup = ManagePatronsPopup(snackAttackTrackWidget=self)
        managePatronsPopup.open()
        managePatronsPopup.populatePatronsList()

    def displayAboutPopup(self):
        popup = AboutPopup()
        popup.open()