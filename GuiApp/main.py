from kivy.app import App
from kivy.core.window import Window
from kivy.modules import inspector
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.image import Image
from kivy.lang import Builder

from widgets.snackAttackTrack import SnackAttackTrackWidget
from database import createAllTables, closeDatabase

# Size of Raspberry pi touchscreen
Window.size = (800, 480)


class ImageButton(ButtonBehavior, Image):
    pass


class BoxLayoutButton(ButtonBehavior, BoxLayout):
    pass


class snackAttackTrackApp(App):
    def build(self):
        self.title = 'Snack Attack Track'
        Builder.load_file("kv/main.kv")
        createAllTables()
        snackAttackTrackWidget = SnackAttackTrackWidget()
        inspector.create_inspector(Window, snackAttackTrackWidget)
        return snackAttackTrackWidget

    def on_stop(self):
        closeDatabase()
        return super().on_stop()


if __name__ == '__main__':
    snackAttackTrackApp().run()
