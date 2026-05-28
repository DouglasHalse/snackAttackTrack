from kivy.uix.scrollview import ScrollView


class FastTouchScrollView(ScrollView):
    """ScrollView that dispatches on_touch_down to children immediately"""

    def on_scroll_start(self, touch, check_children=True):
        if not self.disabled and not self._touch and self.collide_point(*touch.pos):
            touch.push()
            touch.apply_transform_2d(self.to_local)
            for child in self.children[:]:
                child.dispatch("on_touch_down", touch)
            touch.pop()
            return super().on_scroll_start(touch, check_children=False) or True
        return super().on_scroll_start(touch, check_children)
