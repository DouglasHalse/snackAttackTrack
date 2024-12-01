from kivy.app import App
from kivy.core.window import Window
from kivy.modules import inspector
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.image import Image
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager

from widgets.splashScreen import SplashScreenWidget
from widgets.loginScreen import LoginScreenWidget
from widgets.mainUserScreen import MainUserScreenWidget
from database import createAllTables, closeDatabase

# Size of Raspberry pi touchscreen
Window.size = (800, 480)


class ImageButton(ButtonBehavior, Image):
    pass


class BoxLayoutButton(ButtonBehavior, BoxLayout):
    pass


class snackAttackTrackApp(App):
    def __init__(self):
        self.title = "Snack Attack Track"
        super().__init__()

    def build(self):
        Builder.load_file("kv/main.kv")
        createAllTables()
        sm = ScreenManager()
        sm.add_widget(SplashScreenWidget(name="splashScreen"))
        sm.add_widget(LoginScreenWidget(name="loginScreen"))
        sm.add_widget(MainUserScreenWidget(name="mainUserPage"))
        inspector.create_inspector(Window, sm)
        return sm

    def on_stop(self):
        closeDatabase()
        return super().on_stop()


if __name__ == "__main__":
    snackAttackTrackApp().run()
