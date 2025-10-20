from kivy.properties import StringProperty
from kivy.uix.gridlayout import GridLayout


class SingleStatWidget(GridLayout):
    stat_name = StringProperty("")
    stat_value = StringProperty("")


class DoubleStatWidget(GridLayout):
    stat_name = StringProperty("")
    stat_value_1 = StringProperty("")
    stat_value_2 = StringProperty("")
