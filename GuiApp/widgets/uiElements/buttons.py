from kivy.uix.boxlayout import BoxLayout
from kivy.uix.behaviors import ButtonBehavior


class BoxLayoutButton(ButtonBehavior, BoxLayout):
    pass


class ConfirmButton(BoxLayoutButton):
    pass


class BuyButton(BoxLayoutButton):
    pass


class CancelButton(BoxLayoutButton):
    pass


class CloseButton(BoxLayoutButton):
    pass


class RemoveButton(BoxLayoutButton):
    pass
