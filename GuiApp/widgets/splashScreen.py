from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.behaviors import ButtonBehavior


class BoxLayoutButton(ButtonBehavior, BoxLayout):
    pass


class SplashScreenWidget(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def onPress(self):
        self.manager.current = "loginScreen"
