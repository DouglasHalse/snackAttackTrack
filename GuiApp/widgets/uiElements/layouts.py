from kivy.properties import NumericProperty
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.gridlayout import GridLayout
from widgets.uiElements.behaviors import PressAnimator


class RoundedTwoColorGridLayout(GridLayout):
    press_offset = NumericProperty(0)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.visible = True
        self.opacity = 1.0
        self.disabled = False
        self._prev_offset = 0
        self.bind(press_offset=self._shift_children)

    def on_disabled(self, instance, value):
        self.opacity = 0.8 if value else 1.0
        self.disabled = value
        self.visible = not value

    def _shift_children(self, *args):
        delta = self.press_offset - self._prev_offset
        for child in self.children:
            child.x -= delta
            child.y -= delta
        self._prev_offset = self.press_offset

    def do_layout(self, *largs, **kwargs):
        # Undo accumulated offset so GridLayout positions children at base
        for child in self.children:
            child.x += self._prev_offset
            child.y += self._prev_offset
        self._prev_offset = 0
        super().do_layout(*largs, **kwargs)
        self._shift_children()


class ClickableRoundedTwoColorGridLayout(
    PressAnimator, ButtonBehavior, RoundedTwoColorGridLayout
):
    pass
