from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.gridlayout import GridLayout


class RoundedTwoColorGridLayout(GridLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.visible = True
        self.opacity = 1.0
        self.disabled = False

    def on_disabled(self, instance, value):
        self.opacity = 0.8 if value else 1.0
        self.disabled = value
        self.visible = not value


class ClickableRoundedTwoColorGridLayout(ButtonBehavior, RoundedTwoColorGridLayout):
    pass
