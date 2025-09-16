from kivy.properties import StringProperty
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.boxlayout import BoxLayout
from widgets.uiElements.layouts import ClickableRoundedTwoColorGridLayout


class BoxLayoutButton(ButtonBehavior, BoxLayout):
    pass


class GreenButton(BoxLayoutButton):
    pass


class OrangeButton(BoxLayoutButton):
    pass


class RedButton(BoxLayoutButton):
    pass


class ImageAndTextButton(ClickableRoundedTwoColorGridLayout):
    text = StringProperty("")
    image_path = StringProperty("")
