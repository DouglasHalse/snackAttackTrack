from kivy.uix.screenmanager import Screen


class SplashScreenWidget(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def onPressed(self):
        self.manager.transitionToScreen("loginScreen")
