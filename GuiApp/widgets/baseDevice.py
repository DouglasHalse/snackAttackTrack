from kivy.uix.boxlayout import BoxLayout


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
