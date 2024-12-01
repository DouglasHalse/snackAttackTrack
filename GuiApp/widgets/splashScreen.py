from kivy.uix.screenmanager import Screen


class SplashScreenWidget(Screen):
    def __init__(self, **kwargs):
        super(SplashScreenWidget, self).__init__(**kwargs)

    def OnScreenTouch(self, *largs):
        print("Screen touched")
