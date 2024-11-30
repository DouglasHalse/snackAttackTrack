import sys, os, threading
import sqlite3
from functools import partial
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup
from kivy.uix.button import Button
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.image import Image
from kivy.config import Config
from kivy.clock import Clock
Config.set('graphics', 'width', '800')
Config.set('graphics', 'height', '480')
from enum import Enum

def create_patreon_table():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Patrons (
        PatronID INTEGER PRIMARY KEY AUTOINCREMENT,
        FirstName TEXT NOT NULL,
        LastName TEXT NOT NULL,
        EmployeeID TEXT NOT NULL
    )
    """)
    conn.commit()

def add_patron(first_name, last_name, employee_id):
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO Patrons (FirstName, LastName, EmployeeID)
        VALUES (?, ?, ?)
        """, (first_name, last_name, employee_id))
    conn.commit()

def get_all_patrons():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Patrons")
    return cursor.fetchall()

class ImageButton(ButtonBehavior, Image):
    pass


class BoxLayoutButton(ButtonBehavior, BoxLayout):
    pass


class EMFReaderWidget(BoxLayout):
    def __init__(self, deviceName, **kwargs):
        super().__init__(**kwargs)
        self.deviceName = deviceName
        for led in range(1, 5):
            self.ids['led' + str(led)].canvas.opacity = .5
        self.canvasOpacity = 0

        # Make button groups unique
        self.ids.fluctuationButton0.group = "fluctuationButtonGroup" + deviceName
        self.ids.fluctuationButton1.group = "fluctuationButtonGroup" + deviceName
        self.ids.fluctuationButton2.group = "fluctuationButtonGroup" + deviceName
        self.ids.fluctuationRateButton0.group = "fluctuationRateButtonGroup" + deviceName
        self.ids.fluctuationRateButton1.group = "fluctuationRateButtonGroup" + deviceName
        self.ids.fluctuationRateButton2.group = "fluctuationRateButtonGroup" + deviceName

    def SetCanvasLedCanvasOpacity(self, led, opacity, *largs):
        self.ids['led' + str(led)].canvas.opacity = opacity
        self.ids['led' + str(led)].canvas.ask_update()

    def SetLedState(self, ledState):
        for led in range(1, 5):
            opacity = 1 if  led <= ledState else  .5
            Clock.schedule_once(partial(self.SetCanvasLedCanvasOpacity, led, opacity ), -1)

    def SetUseSoundActive(self, useSound, *largs):
        if useSound == True:
            self.ids["muteButton"].text = "Mute"
        else:
            self.ids["muteButton"].text = "Unmute"

    def SetUseSound(self, useSound):
        Clock.schedule_once(partial(self.SetUseSoundActive, useSound), -1)

    def OnFluctuationMagnitudeChanged(self, magnitude):
        print("Magnitude set to " + str(magnitude))

    def OnFluctuationRateChanged(self, rate):
        print("Rate set to " + str(rate))



class GenericDeviceWidget(BoxLayout):
    def __init__(self, deviceName,  **kwargs):
        super().__init__(**kwargs)
        self.deviceWidget = EMFReaderWidget(deviceName=deviceName)
        self.setGrayedOut(grayedOut=True)
        self.add_widget(self.deviceWidget)

    def setGrayedOut(self, grayedOut: bool):
        if grayedOut:
            self.deviceWidget.canvasOpacity = .5
            self.deviceWidget.disabled = True
        else:
            self.deviceWidget.canvasOpacity = 0
            self.deviceWidget.disabled = False


class BaseDeviceInfoLableWidget(BoxLayout):
    def __init__(self, deviceName: str, **kwargs):
        super().__init__(**kwargs)
        self.ids.deviceName.text = deviceName


class BaseDeviceConnectionIndicatorWidget(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
 
#    def SetColor(self, state: SpookStationDeviceConnectionState, *largs):
#        if state == SpookStationDeviceConnectionState.Disconnected:
#            self.ids['deviceConnectionIndicator'].source = "Images/ghost_red.png"
#        elif state == SpookStationDeviceConnectionState.PoorConnection:
#            self.ids['deviceConnectionIndicator'].source = "Images/ghost_yellow.png"
#        elif state == SpookStationDeviceConnectionState.Connected:
#            self.ids['deviceConnectionIndicator'].source = "Images/ghost_green.png"
#        else:
#            print("Unsupported Device state: " + state)


class BaseDeviceInfoWidget(BoxLayout):
    def __init__(self, deviceName: str, **kwargs):
        super().__init__(**kwargs)
        self.labelWidget = BaseDeviceInfoLableWidget(deviceName=deviceName)
        self.add_widget(self.labelWidget)
        self.indicatorWidget = BaseDeviceConnectionIndicatorWidget()
        self.add_widget(self.indicatorWidget)


class DeviceRowWidget(BoxLayout):
    def __init__(self, deviceName: str = "", **kwargs):
        super().__init__(**kwargs)
        self.baseDeviceInfoWidget = BaseDeviceInfoWidget(deviceName=deviceName)
        self.add_widget(self.baseDeviceInfoWidget)
        self.genericDeviceWidget = GenericDeviceWidget(deviceName=deviceName)
        self.add_widget(self.genericDeviceWidget)

#    def ConnectionStateChangeCallback(self, state: SpookStationDeviceConnectionState):
#        Clock.schedule_once(partial(self.baseDeviceInfoWidget.indicatorWidget.SetColor, state), -1)
#        if state == SpookStationDeviceConnectionState.Disconnected:
#            self.genericDeviceWidget.setGrayedOut(grayedOut=True)
#        else:
#            self.genericDeviceWidget.setGrayedOut(grayedOut=False)

    def Remove(self):
        self.parent.remove_widget(self)

class PatronRowWidget(BoxLayout):
    def __init__(self, firstName: str = "", lastName: str = "", employeeID: str = "", **kwargs):
        super().__init__(**kwargs)
        self.firstName = firstName
        self.lastName = lastName
        self.employeeID = employeeID

class ManageDevicePopup(Popup):
    def __init__(self, spookStationWidget, manageDevicesPopup, manageDevicesAddedDevice, deviceName, deviceType, **kwargs):
        self.spookStationWidget = spookStationWidget
        self.manageDevicesAddedDevice = manageDevicesAddedDevice
        self.manageDevicesPopup = manageDevicesPopup
        self.deviceName = deviceName
        self.deviceType = deviceType
        super(ManageDevicePopup, self).__init__(**kwargs)
        
    def focus_text_input(self, *largs):
        self.ids.manageDeviceNameInput.focus = True

    def on_open(self):
        self.ids.manageDeviceNameInput.text = self.deviceName
        #self.ids.manageDeviceTypeSpinner.values = [SpookStationDeviceTypeToString[deviceType] for deviceType in SpookStationDeviceType]
        #self.ids.manageDeviceTypeSpinner.text = SpookStationDeviceTypeToString[self.deviceType]
        Clock.schedule_once(self.focus_text_input, 0)

    def OnConfirmButtonPressed(self, *largs):

        #if not verifyDeviceType(SpookStationDeviceStringToType[self.ids.manageDeviceTypeSpinner.text]):
        #    return
        #if not verifyDeviceName(self.ids.manageDeviceNameInput.text):
        #    return
        # If device name or type changed, remake device
        if self.ids.manageDeviceNameInput.text != self.deviceName:# or self.ids.manageDeviceTypeSpinner.text != SpookStationDeviceTypeToString[self.deviceType]:
            # Update deviceManager entry
            #deviceManager.removeDevice(deviceName=self.deviceName)
            #deviceManager.addDevice(deviceName=self.ids.manageDeviceNameInput.text, deviceType=SpookStationDeviceStringToType[self.ids.manageDeviceTypeSpinner.text])

            # Update main list widget entry
            #self.spookStationWidget.RemoveDeviceInfoWidget(deviceName=self.deviceName)
            #self.spookStationWidget.AddNewDeviceInfoWidget(deviceType=SpookStationDeviceStringToType[self.ids.manageDeviceTypeSpinner.text], deviceName=self.ids.manageDeviceNameInput.text)

            # Update manageDevicesAddedDevice entry
            self.manageDevicesAddedDevice.ids.manageDeviceAddedDeviceName.text = self.ids.manageDeviceNameInput.text
            self.manageDevicesAddedDevice.ids.manageDeviceAddedDeviceType.text = self.ids.manageDeviceTypeSpinner.text
        self.dismiss()

    def OnRemoveButtonPressed(self, *largs):
        # Remove deviceManager entry
        #deviceManager.removeDevice(deviceName=self.deviceName)

        # Remove main list widget entry
        self.spookStationWidget.RemoveDeviceInfoWidget(deviceName=self.deviceName)

        # Remove manageDevicesPopup entry
        self.manageDevicesPopup.ids.manageDevicesAddedDevicesGridListContent.remove_widget(self.manageDevicesAddedDevice)

        # Dismiss Manage device Popup
        self.dismiss()


class ManagePatronsPopup(Popup):
    def __init__(self, snackAttackTrackWidget,  **kwargs):
        super(ManagePatronsPopup, self).__init__(**kwargs)
        self.snackAttackTrackWidget = snackAttackTrackWidget

    def OnAddDeviceButtonPressed(self, *largs):
        addPatronPopup = AddPatronPopup(managePatronsPopup=self, snackAttackTrackWidget=self.snackAttackTrackWidget)
        addPatronPopup.open()


class ManageDevicesPopupDevice(BoxLayout):
    def __init__(self, spookStationWidget, manageDevicesPopup, deviceName, deviceType, **kwargs):
        self.spookStationWidget = spookStationWidget
        self.manageDevicesPopup = manageDevicesPopup
        super(ManageDevicesPopupDevice, self).__init__(**kwargs)
        self.ids.manageDeviceAddedDeviceName.text = deviceName
        #self.ids.manageDeviceAddedDeviceType.text = SpookStationDeviceTypeToString[deviceType]

    def OnManageDeviceButtonPressed(self, deviceName: str,  *largs):
        #deviceType = deviceManager.devices[deviceName].deviceType
        manageDevicePopup = ManageDevicePopup(spookStationWidget=self.spookStationWidget, manageDevicesPopup=self.manageDevicesPopup, manageDevicesAddedDevice=self, deviceName=deviceName, deviceType=deviceType)
        manageDevicePopup.open() 

class AddPatronPopup(Popup):
    def __init__(self, managePatronsPopup, snackAttackTrackWidget, **kwargs):
        super(AddPatronPopup, self).__init__(**kwargs)
        self.managePatronsPopup = managePatronsPopup
        self.snackAttackTrackWidget = snackAttackTrackWidget

    def focus_text_input(self, *largs):
        self.ids.addPatronFirstNameInput.focus = True
        self.ids.addPatronLastNameInput.focus = True
        self.ids.addPatronEmployeeIDInput.focus = True

    def on_open(self):
        self.ids.addPatronFirstNameInput.text = "EMFReader1"
        self.ids.addPatronLastNameInput.text = "LastName"
        self.ids.addPatronEmployeeIDInput.text = "1"
        Clock.schedule_once(self.focus_text_input, 0)

    def AddPatron(self):
        patronFirstName = self.ids.addPatronFirstNameInput.text
        patronLastName = self.ids.addPatronLastNameInput.text
        patronEmployeeID = self.ids.addPatronEmployeeIDInput.text
        print("Adding patron " + patronFirstName)
        add_patron(patronFirstName, patronLastName, patronEmployeeID)

class ErrorMessagePopup(Popup):
    def __init__(self, errorMessage: str, **kwargs):
        super(ErrorMessagePopup, self).__init__(**kwargs)
        self.ids.errorMessagePopupLabel.text = errorMessage

class SnackAttackTrackWidget(BoxLayout):
    def __init__(self, **kwargs):
        super(SnackAttackTrackWidget, self).__init__(**kwargs)
        create_patreon_table()

    def AddNewPatronWidget(self, firstName, lastName, employeeID):
        newPatronWidget = PatronRowWidget(firstName,lastName,employeeID)
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

    def displayaboutpopup(self):
        popup = AboutPopup()
        popup.open()

class snackAttackTrackApp(App):
    def build(self):
        self.title = 'Snack Attack Track'
        return SnackAttackTrackWidget()

    def on_stop(self):
        sqlite3.connect("database.db").cursor().close()
        return super().on_stop()

class AboutPopup(Popup):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

if __name__ == '__main__':
    snackAttackTrackApp().run()
