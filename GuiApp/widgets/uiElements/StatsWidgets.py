from kivy.properties import StringProperty
from kivy.uix.gridlayout import GridLayout


class SingleStatWidget(GridLayout):
    stat_name = StringProperty("")
    stat_value = StringProperty("")


class DoubleStatWidget(GridLayout):
    stat_name = StringProperty("")
    stat_value_1 = StringProperty("")
    stat_value_2 = StringProperty("")


class TripleHeaderValueStatWidget(GridLayout):
    stat_name_1 = StringProperty("")
    stat_name_2 = StringProperty("")
    stat_name_3 = StringProperty("")
    stat_value_1 = StringProperty("")
    stat_value_2 = StringProperty("")
    stat_value_3 = StringProperty("")
