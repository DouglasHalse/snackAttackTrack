"""LogLine — a single row in the RecycleView log display.

Only visible rows are ever textured (virtual scrolling),
eliminating the GPU texture overflow issue on Raspberry Pi.
"""

from kivy.clock import Clock
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.recycleview.views import RecycleDataViewBehavior


class LogLine(RecycleDataViewBehavior, BoxLayout):
    """One log line rendered in the RecycleView.

    Each row auto-sizes its height to fit wrapped text
    (tracebacks, long lines, etc.).
    """

    _height_set = False

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.height = 20

    def refresh_view_attrs(self, rv, index, data):
        """Called when the RecycleView reuses this widget for a data row."""
        self.ids.logLabel.text = data.get("log_text", "")
        self._height_set = False
        Clock.schedule_once(self._set_height, 0)
        return super().refresh_view_attrs(rv, index, data)

    def _set_height(self, dt):
        """Set row height based on the rendered label texture."""
        if self._height_set:
            return
        self._height_set = True
        self.height = max(self.ids.logLabel.texture_size[1] + 2, 20)
