from kivy.uix.boxlayout import BoxLayout


class SplashScreenWidget(BoxLayout):
    def __init__(self, **kwargs):
        super(SplashScreenWidget, self).__init__(**kwargs)

    def OnScreenTouch(self, *largs):
        print("Screen touched")
