import sys, os, threading

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.image import Image
from kivy.config import Config
Config.set('graphics', 'width', '800')
Config.set('graphics', 'height', '480')

from widgets.snackAttackTrack import SnackAttackTrackWidget

from database import createPatreonTable, closeDatabase

class ImageButton(ButtonBehavior, Image):
    pass

class BoxLayoutButton(ButtonBehavior, BoxLayout):
    pass

class snackAttackTrackApp(App):
    def build(self):
        self.title = 'Snack Attack Track'
        createPatreonTable()
        return SnackAttackTrackWidget()

    def on_stop(self):
        closeDatabase()
        return super().on_stop()

if __name__ == '__main__':
    snackAttackTrackApp().run()
