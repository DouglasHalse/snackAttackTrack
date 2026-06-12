from kivy.animation import Animation
from kivy.clock import Clock
from kivy.properties import NumericProperty, StringProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.relativelayout import RelativeLayout


class LetterLabel(Label):
    """Label used for each letter in the alphabet strip.
    Font size is bound via kv rule to the parent AlphabetStrip's width.
    """


class AlphabetStrip(RelativeLayout):  # pylint: disable=too-many-instance-attributes
    """A horizontal row of A-Z letters for quick-scrolling through
    alphabetically-sorted lists.

    Touch interaction:
        - Tap a letter -> fires ``on_letter_selected``
        - Slide across letters -> floating preview follows the finger
        - Lift -> fires ``on_letter_selected`` with the final letter

    Events
    ------
    on_letter_selected:
        Fired with the selected letter (str).
    """

    LETTERS = "ABCDEFGHIJKLMNOPQRSTUVWXYZÅÄÖ"

    letter_count = NumericProperty(0)

    floating_text = StringProperty("")
    floating_opacity = NumericProperty(0)
    floating_y = NumericProperty(0)

    # --- colour constants ---------------------------------------------------
    _COLOR_ACTIVE = (0, 0, 0, 1)
    _COLOR_DIM = (0.4, 0.4, 0.4, 0.5)

    def __init__(self, **kwargs):
        self.register_event_type("on_letter_selected")
        super().__init__(**kwargs)
        self._letters = list(self.LETTERS)
        self.letter_count = len(self._letters)
        self._letter_labels: dict[str, Label] = {}
        self._available_letters: set[str] = set(self._letters)
        self._touch_uid = None
        self._current_letter = None
        self._last_dispatched_letter = None
        self._did_animate_in = False
        self._letter_row = BoxLayout(
            orientation="horizontal",
            size_hint=(1, 1),
            pos_hint={"x": 0, "y": 0},
        )
        self.add_widget(self._letter_row)
        Clock.schedule_once(self._build_letters, 0)

    # ------------------------------------------------------------------
    # Letter row construction
    # ------------------------------------------------------------------

    def _build_letters(self, *args):
        """Create a Label for each letter."""
        self._letter_row.clear_widgets()
        self._letter_labels.clear()
        for letter in self._letters:
            label = LetterLabel(
                text=letter,
                halign="center",
                valign="middle",
                size_hint_x=1.0 / len(self._letters),
            )
            self._letter_labels[letter] = label
            self._letter_row.add_widget(label)
        self._refresh_label_styles()

    def _color_for_letter(self, letter, *, highlight=False):
        """Color for *letter*: active-black if available, dim-grey if not.
        When *highlight* is True, always return the active color."""
        if highlight or letter in self._available_letters:
            return self._COLOR_ACTIVE
        return self._COLOR_DIM

    def _refresh_label_styles(self):
        """Update every label's colour from the available set."""
        for letter, label in self._letter_labels.items():
            if letter == self._current_letter:
                continue
            label.color = self._color_for_letter(letter)

    # ------------------------------------------------------------------
    # Touch handling
    # ------------------------------------------------------------------

    def _letter_at_pos(self, parent_x, parent_y):
        """Return the letter under (*parent_x*, *parent_y*) in parent-relative coords."""
        local_x = self.to_widget(parent_x, parent_y)[0]
        if local_x < 0 or local_x > self.width:
            return None
        idx = int(local_x / (self.width / len(self._letters)))
        idx = max(0, min(idx, len(self._letters) - 1))
        return self._letters[idx]

    def on_touch_down(self, touch):
        if not self.collide_point(*touch.pos):
            return super().on_touch_down(touch)
        letter = self._letter_at_pos(touch.x, touch.y)
        if letter is None:
            return super().on_touch_down(touch)
        self._touch_uid = touch.uid
        self._last_dispatched_letter = letter
        self._highlight_letter(letter)
        self._update_floating_preview(touch.x, touch.y)
        self.dispatch("on_letter_selected", letter)
        return True

    def on_touch_move(self, touch):
        if touch.uid != self._touch_uid:
            return super().on_touch_move(touch)
        letter = self._letter_at_pos(touch.x, touch.y)
        if letter is not None and letter != self._current_letter:
            self._highlight_letter(letter)
        self._update_floating_preview(touch.x, touch.y)
        if letter is not None and letter != self._last_dispatched_letter:
            self._last_dispatched_letter = letter
            self.dispatch("on_letter_selected", letter)
        return True

    def on_touch_up(self, touch):
        if touch.uid != self._touch_uid:
            return super().on_touch_up(touch)
        self._touch_uid = None
        self._last_dispatched_letter = None
        self._did_animate_in = False
        Animation(floating_opacity=0, floating_y=self.height * 0.2, d=0.15).start(self)
        if self._current_letter and self._current_letter in self._letter_labels:
            cl = self._current_letter
            self._letter_labels[cl].color = self._color_for_letter(cl)
        self._current_letter = None
        return True

    def _highlight_letter(self, letter):
        """Mark a letter as the currently touched one."""
        if self._current_letter and self._current_letter in self._letter_labels:
            prev = self._letter_labels[self._current_letter]
            prev.color = self._color_for_letter(self._current_letter)
        self._current_letter = letter
        if letter in self._letter_labels:
            self._letter_labels[letter].color = self._color_for_letter(
                letter, highlight=True
            )

    def _update_floating_preview(self, screen_x, screen_y):
        """Animate the floating preview flying down on first touch;
        on subsequent slides just update the letter."""
        if self._did_animate_in:
            if self._current_letter:
                self.floating_text = self._current_letter
            return
        self._did_animate_in = True
        if self._current_letter:
            self.floating_text = self._current_letter
            self.floating_y = self.height * 0.6
            self.floating_opacity = 1
            anim = Animation(floating_y=self.height + 10, d=0.12, t="out_back")
            anim.start(self)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def set_available_letters(self, letters: set):
        """Mark which letters have matching users (others shown dimmed)."""
        self._available_letters = set(letters)
        self._refresh_label_styles()

    def on_letter_selected(self, letter: str):
        """Override or bind in kv."""
