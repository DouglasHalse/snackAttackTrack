from kivy.uix.boxlayout import BoxLayout

from .emfReader import EMFReaderWidget

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