from kivy.uix.boxlayout import BoxLayout
from kivy.clock import Clock

from functools import partial

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
