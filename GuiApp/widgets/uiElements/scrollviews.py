from kivy.clock import Clock
from kivy.uix.scrollview import ScrollView


class FastTouchScrollView(ScrollView):
    """ScrollView that dispatches on_touch_down to children immediately"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Declare Kivy-internal attributes that are set lazily at
        # runtime so pylint can see them.  The values are managed
        # entirely by ScrollView; we just give them a home.
        self._touch = None
        self._velocity_check_ev = None

    def on_scroll_start(self, touch, check_children=True):
        if not self.disabled and not self._touch and self.collide_point(*touch.pos):
            touch.push()
            touch.apply_transform_2d(self.to_local)
            for child in self.children[:]:
                child.dispatch("on_touch_down", touch)
            touch.pop()
            return super().on_scroll_start(touch, check_children=False) or True
        return super().on_scroll_start(touch, check_children)

    def cancel_active_scroll(self):
        """Stop any in-progress scroll and reset all internal state
        so the ScrollView accepts programmatic ``scroll_x`` changes."""
        touch = self._touch
        if touch is not None:
            try:
                touch.ungrab(self)
            except Exception:  # pylint: disable=broad-exception-caught
                pass
        self._touch = None

        # Cancel the gesture-detection timeout
        try:
            Clock.unschedule(self._change_touch_mode)
        except Exception:  # pylint: disable=broad-exception-caught
            pass

        # Cancel the post-scroll velocity continuation
        if self._velocity_check_ev is not None:
            self._velocity_check_ev.cancel()
            self._velocity_check_ev = None

        # Kill effect inertia on both axes
        for attr in ("effect_x", "effect_y"):
            effect = getattr(self, attr, None)
            if effect is not None:
                effect.velocity = 0
                try:
                    effect.cancel()
                except Exception:  # pylint: disable=broad-exception-caught
                    pass
