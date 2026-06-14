"""Minimal test screen for isolating RecycleView scroll jolts."""
from kivy.clock import Clock
from kivy.uix.screenmanager import Screen


class PerfTestScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._rv_height_cb = None

    def on_pre_enter(self, *args):
        data = [{"text": f"Item {i}"} for i in range(20)]
        self.ids.rv.data = data
        rv = self.ids.rv
        self._rv_height_cb = lambda instance, value: Clock.schedule_once(
            lambda dt: self._recalc_layout_width(reset_scroll=True), 0
        )
        rv.bind(height=self._rv_height_cb)
        Clock.schedule_once(lambda dt: self._recalc_layout_width(), 0.05)
        return super().on_pre_enter(*args)

    def on_pre_leave(self, *args):
        rv = self.ids.rv
        if self._rv_height_cb is not None:
            rv.unbind(height=self._rv_height_cb)
            self._rv_height_cb = None
        return super().on_pre_leave(*args)

    def _recalc_layout_width(self, reset_scroll=False):
        rv = self.ids.rv
        layout = rv.children[0]
        n = len(rv.data)
        effective_h_test = rv.height - layout.padding[1] - layout.padding[3]
        layout.width = n * effective_h_test + (n - 1) * layout.spacing
        if reset_scroll:
            rv.scroll_x = 0

    def back_pressed(self):
        self.manager.transitionToScreen("splashScreen", transitionDirection="right")
