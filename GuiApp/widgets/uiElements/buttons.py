from kivy.properties import StringProperty
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.floatlayout import FloatLayout
from widgets.uiElements.layouts import ClickableRoundedTwoColorGridLayout
from widgets.uiElements.behaviors import PressAnimator


class BoxLayoutButton(PressAnimator, ButtonBehavior, FloatLayout):
    pass


class PressButton(BoxLayoutButton):
    button_color_name = StringProperty("green_button")


class GreenButton(PressButton):
    pass


class OrangeButton(PressButton):
    pass


class RedButton(PressButton):
    pass


class ImageAndTextButton(ClickableRoundedTwoColorGridLayout):
    text = StringProperty("")
    image_path = StringProperty("")
