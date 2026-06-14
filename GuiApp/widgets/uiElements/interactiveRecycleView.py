"""InteractiveRecycleView - a RecycleView that supports press + tap on items.

Uses the Kivy-recommended pattern: press state is stored in the data dicts
themselves (``"pressed": True/False``) rather than in the widget instances.

Features:
  - Immediate touch feedback (dispatches on_touch_down to children)
  - Scroll-vs-tap detection
  - Press visual follows data through recycling
  - Fires ``on_item_clicked`` event on tap (not scroll)
  - Press cleanup on touch-up (handles RecycleView touch-grab stealing)
  - ``scroll_to_index`` / ``scroll_to`` for programmatic scrolling
  - Fixed layout width to prevent scroll jolts

Viewclass must inherit from ``InteractiveRecycleDataViewBehavior``.
"""

from time import perf_counter

from kivy.animation import AnimationTransition
from kivy.clock import Clock
from kivy.uix.recycleview import RecycleView
from kivy.uix.recycleview.views import RecycleDataViewBehavior
from kivy.factory import Factory as KivyFactory


class InteractiveRecycleView(RecycleView):
    """RecycleView whose items support press feedback and tap actions."""

    __events__ = ("on_item_clicked",)

    # Pixels of horizontal drag before we decide the user is scrolling
    # rather than tapping.
    scroll_threshold = 5

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.scroll_x = 0
        self._pressed_index = None
        self._touch_start_x = 0
        self._did_scroll = False
        self._scroll_anim = None

    def on_kv_post(self, base_widget):
        """Validate the viewclass once, after KV properties are applied."""
        super().on_kv_post(base_widget)
        self._assert_valid_viewclass()

    def _assert_valid_viewclass(self):
        """Catch misconfigured viewclass early (before any widgets are created).

        Raises ``TypeError`` if ``self.viewclass`` does not inherit from
        ``InteractiveRecycleDataViewBehavior``.
        """

        vc = self.viewclass
        if isinstance(vc, str):
            vc = KivyFactory.get(vc)
        if vc is not None and not issubclass(vc, InteractiveRecycleDataViewBehavior):
            raise TypeError(
                f"{vc.__name__} must inherit from InteractiveRecycleDataViewBehavior"
            )

    def on_item_clicked(self, index):
        pass

    def scroll_to_index(self, index):
        """Animate the viewport so the data item at *index* is centred."""
        total = len(self.data)
        if total <= 1 or not 0 <= index < total:
            return
        # Cancel any in-progress scroll animation
        if self._scroll_anim:
            self._scroll_anim.cancel()
            self._scroll_anim = None
        if hasattr(self, "effect_x") and self.effect_x is not None:
            self.effect_x.velocity = 0

        layout = self.layout_manager
        if layout is None:
            return
        item_w = self.height  # square widgets
        spacing = layout.spacing
        content_w = total * item_w + (total - 1) * spacing
        viewport_w = self.width
        scrollable = max(0, content_w - viewport_w)
        if scrollable <= 0:
            return
        item_center = index * (item_w + spacing) + item_w / 2
        target = max(0, min(1, (item_center - viewport_w / 2) / scrollable))

        start_x = self.scroll_x
        start_t = perf_counter()
        duration = 0.3

        def _anim_step(_dt):
            elapsed = perf_counter() - start_t
            progress = min(1.0, elapsed / duration)
            eased = AnimationTransition.out_quad(progress)
            self.scroll_x = start_x + (target - start_x) * eased
            if progress >= 1.0:
                self._scroll_anim.cancel()
                self._scroll_anim = None

        self._scroll_anim = Clock.schedule_interval(_anim_step, 0)

    def scroll_to(self, match_fn):
        """Scroll to the first data item where ``match_fn(index, data)`` is True."""
        for i, item in enumerate(self.data or ()):
            if match_fn(i, item):
                self.scroll_to_index(i)
                return

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            self._did_scroll = False
            self._touch_start_x = touch.x

            # Dispatch to layout children so widgets get immediate
            # press feedback.  ButtonBehavior normally delays this
            # to distinguish scroll from tap - we handle that here.
            touch.push()
            touch.apply_transform_2d(self.to_local)
            for child in self.children[:]:
                child.dispatch("on_touch_down", touch)
            touch.pop()
        return super().on_touch_down(touch)

    def on_touch_move(self, touch):
        if not self._did_scroll:
            if abs(touch.x - self._touch_start_x) > self.scroll_threshold:
                self._did_scroll = True
        return super().on_touch_move(touch)

    def on_touch_up(self, touch):
        if not self._did_scroll and self._pressed_index is not None:
            # Tap detected - fire the event.
            self.dispatch("on_item_clicked", self._pressed_index)
        # Always release press.  During a scroll the widget's
        # ButtonBehavior may have been recycled and never saw the
        # touch-up, so we clean up unconditionally.
        self._clear_press()
        return super().on_touch_up(touch)

    def _set_press(self, index):
        """Record that the data item at *index* is pressed."""
        if self._pressed_index == index:
            return
        self._unmark_pressed()
        self._pressed_index = index
        if 0 <= index < len(self.data):
            self.data[index]["pressed"] = True
            # No refresh - the widget already shows the press from
            # ButtonBehavior, and recycling picks up the data change
            # via normal refresh_view_attrs cycles.

    def _clear_press(self):
        """Clear the currently-pressed item and refresh visible widgets."""
        if self._pressed_index is not None:
            self._unmark_pressed()
            self._pressed_index = None
            layout = self.layout_manager
            if layout is not None:
                for child in layout.children[:]:
                    if isinstance(child, InteractiveRecycleDataViewBehavior):
                        child.reset_press_if_down()

    def _unmark_pressed(self):
        """Set data[*]["pressed"] = False for the current pressed
        index, without triggering a view refresh."""
        if self._pressed_index is not None:
            idx = self._pressed_index
            if 0 <= idx < len(self.data):
                self.data[idx]["pressed"] = False


class InteractiveRecycleDataViewBehavior(RecycleDataViewBehavior):
    """Mixin for viewclass widgets in an InteractiveRecycleView.

    Handles press-state tracking so subclass widgets can focus on
    data binding.  Requires a ``clickableLayout`` child that is a
    ButtonBehavior with a ``reset_press_state()`` method.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._current_index = -1
        self._rv = None
        self.ids.clickableLayout.bind(on_press=self._on_child_pressed)
        self.ids.clickableLayout.bind(on_release=self._on_child_released)

    # pylint: disable=protected-access
    # _set_press / _clear_press belong to InteractiveRecycleView

    def _on_child_pressed(self, *args):
        if self._rv is not None:
            self._rv._set_press(self._current_index)

    def _on_child_released(self, *args):
        if self._rv is not None:
            self._rv._clear_press()

    def reset_press_if_down(self):
        """If visually pressed, release.  Called by the RecycleView on
        touch-up to handle widgets whose ButtonBehavior never saw the
        touch-up due to grab stealing during scroll."""
        layout = self.ids.clickableLayout
        if layout.state == "down":
            layout.state = "normal"
            layout.reset_press_state()

    def refresh_view_attrs(self, rv, index, data):
        self._current_index = index
        self._rv = rv
        # Apply / clear press visual from the data dict.
        layout = self.ids.clickableLayout
        if data.get("pressed"):
            if layout.state != "down":
                layout.state = "down"
                layout.press_offset = 4  # snap — no animation
        elif layout.state == "down":
            layout.state = "normal"
            layout.reset_press_state()
        return super().refresh_view_attrs(rv, index, data)
