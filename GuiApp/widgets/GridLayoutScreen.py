from kivy.properties import (
    NumericProperty,
    ObjectProperty,
    OptionProperty,
    StringProperty,
)
from kivy.uix.gridlayout import GridLayout


class GridLayoutScreen(GridLayout):
    """Screen is an element intended to be used with a :class:`ScreenManager`.
    Check module documentation for more information.

    :Events:
        `on_pre_enter`: ()
            Event fired when the screen is about to be used: the entering
            animation is started.
        `on_enter`: ()
            Event fired when the screen is displayed: the entering animation is
            complete.
        `on_pre_leave`: ()
            Event fired when the screen is about to be removed: the leaving
            animation is started.
        `on_leave`: ()
            Event fired when the screen is removed: the leaving animation is
            finished.

    .. versionchanged:: 1.6.0
        Events `on_pre_enter`, `on_enter`, `on_pre_leave` and `on_leave` were
        added.
    """

    name = StringProperty("")
    """
    Name of the screen which must be unique within a :class:`ScreenManager`.
    This is the name used for :attr:`ScreenManager.current`.

    :attr:`name` is a :class:`~kivy.properties.StringProperty` and defaults to
    ''.
    """

    manager = ObjectProperty(None, allownone=True)
    """:class:`ScreenManager` object, set when the screen is added to a
    manager.

    :attr:`manager` is an :class:`~kivy.properties.ObjectProperty` and
    defaults to None, read-only.

    """

    transition_progress = NumericProperty(0.0)
    """Value that represents the completion of the current transition, if any
    is occurring.

    If a transition is in progress, whatever the mode, the value will change
    from 0 to 1. If you want to know if it's an entering or leaving animation,
    check the :attr:`transition_state`.

    :attr:`transition_progress` is a :class:`~kivy.properties.NumericProperty`
    and defaults to 0.
    """

    transition_state = OptionProperty("out", options=("in", "out"))
    """Value that represents the state of the transition:

    - 'in' if the transition is going to show your screen
    - 'out' if the transition is going to hide your screen

    After the transition is complete, the state will retain its last value (in
    or out).

    :attr:`transition_state` is an :class:`~kivy.properties.OptionProperty` and
    defaults to 'out'.
    """

    __events__ = ("on_pre_enter", "on_enter", "on_pre_leave", "on_leave")

    def on_pre_enter(self, *args):
        pass

    def on_enter(self, *args):
        pass

    def on_pre_leave(self, *args):
        pass

    def on_leave(self, *args):
        pass

    def __repr__(self):
        return f"<Screen name={self.name!r}>"
