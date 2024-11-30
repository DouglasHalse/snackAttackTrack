from kivy.uix.popup import Popup
from kivy.clock import Clock
from kivy.uix.boxlayout import BoxLayout

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