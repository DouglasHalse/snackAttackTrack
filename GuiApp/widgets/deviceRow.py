from kivy.uix.boxlayout import BoxLayout

from widgets.baseDevice import BaseDeviceInfoWidget
from widgets.genericDevice import GenericDeviceWidget


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
