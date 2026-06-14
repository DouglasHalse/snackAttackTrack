from kivy.animation import Animation
from kivy.properties import NumericProperty


class PressAnimator:  # pylint: disable=no-member
    """Mixin that provides on_press/on_release/on_touch_up with press_offset animation."""

    press_offset = NumericProperty(0)

    def _animate_press(self, pressed):
        offset = 4 if pressed else 0
        duration = 0.05 if pressed else 0.1
        anim = Animation(press_offset=offset, duration=duration)
        anim.start(self)

    def reset_press_state(self):
        """Instantly clear press animation"""
        Animation.cancel_all(self, "press_offset")
        self.press_offset = 0

    def on_press(self, *args):
        self._animate_press(pressed=True)
        return super().on_press(*args)

    def on_release(self, *args):
        self._animate_press(pressed=False)
        return super().on_release(*args)

    def on_touch_up(self, touch):
        if touch.grab_current is self and not self.collide_point(*touch.pos):
            self._animate_press(pressed=False)
        return super().on_touch_up(touch)
