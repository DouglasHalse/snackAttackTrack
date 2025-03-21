from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.gridlayout import GridLayout


class RoundedTwoColorGridLayout(GridLayout):
    pass


class ClickableRoundedTwoColorGridLayout(ButtonBehavior, RoundedTwoColorGridLayout):
    pass
