import time as _time

from kivy.animation import AnimationTransition
from kivy.clock import Clock
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.recycleview.views import RecycleDataViewBehavior
from kivy.uix.screenmanager import Screen
from logger import get_logger
from widgets.popups.createUserOrLinkCardPopup import CreateUserOrLinkCardPopup
from widgets.settingsManager import SettingName

logger = get_logger(__name__)


class LoginScreenUserWidget(RecycleDataViewBehavior, BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.screenManager = None
        self.patronId = None
        self.first_name = ""
        self.last_name = ""

    def refresh_view_attrs(self, rv, index, data):
        self.first_name = data["first_name"]
        self.last_name = data["last_name"]
        self.patronId = data["patron_id"]
        self.screenManager = data["screen_manager"]
        self.ids.first_name_label.text = self.first_name
        self.ids.first_name_label.reset()
        self.ids.last_name_label.text = self.last_name
        self.ids.last_name_label.reset()
        return super().refresh_view_attrs(rv, index, data)

    def Clicked(self, *largs):
        # Suppress login if the user was scrolling, not tapping
        if (
            self.screenManager is None
            or self.screenManager.current_screen.scroll_did_occur
        ):
            logger.debug(
                "Login click REJECTED for %s %s (patronId=%s) — scroll detected",
                self.first_name,
                self.last_name,
                self.patronId,
            )
            return
        logger.debug(
            "Login click ACCEPTED for %s %s (patronId=%s)",
            self.first_name,
            self.last_name,
            self.patronId,
        )
        self.screenManager.login(self.patronId)
        self.screenManager.transitionToScreen("mainUserPage")


class LoginScreen(Screen):
    # Minimum horizontal drag distance (in pixels) before we consider the
    # user to have intentionally scrolled rather than tapped.
    _SCROLL_PX_THRESHOLD = 5

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.create_or_link_card_popup = None
        self.scroll_did_occur = False
        self._screen_active = False
        self._letter_index_map = {}
        self._scroll_event = None
        self._rv_height_cb = None

    def on_pre_enter(self, *args):
        self._screen_active = True
        self.ids["userRecycleView"].bind(on_scroll_move=self._on_user_list_scrolled)
        self.ids["userRecycleView"].scroll_x = 0

        self._populate_users()

        self.ids["alphabetStrip"].set_available_letters(self._letter_index_map.keys())

        if self.manager.settingsManager.get_setting_value(
            settingName=SettingName.GO_TO_SPLASH_SCREEN_ON_IDLE_ENABLE
        ):
            Clock.schedule_once(
                self.goToSplashScreen,
                self.manager.settingsManager.get_setting_value(
                    settingName=SettingName.GO_TO_SPLASH_SCREEN_ON_IDLE_TIME
                ),
            )

        return super().on_pre_enter(*args)

    def _populate_users(self):
        """Build RecycleView data from the database."""
        user_data_list = self.manager.database.getAllPatrons()
        user_data_list.sort(key=lambda u: u.firstName.lower())

        data = []
        self._letter_index_map = {}
        for i, ud in enumerate(user_data_list):
            data.append(
                {
                    "first_name": ud.firstName,
                    "last_name": ud.lastName,
                    "patron_id": ud.patronId,
                    "screen_manager": self.manager,
                }
            )
            first_letter = ud.firstName[0].upper()
            if first_letter not in self._letter_index_map:
                self._letter_index_map[first_letter] = i

        self.ids["userRecycleView"].data = data
        rv = self.ids["userRecycleView"]
        self._rv_height_cb = lambda instance, value: Clock.schedule_once(
            lambda dt: self._fix_layout_width(reset_scroll=True), 0
        )
        rv.bind(height=self._rv_height_cb)
        Clock.schedule_once(lambda dt: self._fix_layout_width(), 0.05)

    def _fix_layout_width(self, reset_scroll=False):
        rv = self.ids["userRecycleView"]
        layout = rv.children[0]
        n = len(rv.data)
        effective_h = rv.height - layout.padding[1] - layout.padding[3]
        layout.width = n * effective_h + (n - 1) * layout.spacing
        if reset_scroll:
            rv.scroll_x = 0
        else:
            # Pre-warm only on initial setup
            rv.scroll_x = 1
            Clock.schedule_once(lambda dt, r=rv: setattr(r, "scroll_x", 0), 0.05)

    def on_enter(self, *args):
        self.manager.RFIDReader.start(self.cardRead)
        return super().on_enter(*args)

    def on_pre_leave(self, *args):
        if self.create_or_link_card_popup is not None:
            self.create_or_link_card_popup = None
        self.manager.RFIDReader.stop()
        if self._rv_height_cb is not None:
            self.ids["userRecycleView"].unbind(height=self._rv_height_cb)
            self._rv_height_cb = None
        return super().on_pre_leave(*args)

    def on_leave(self, *args):
        self._screen_active = False
        Clock.unschedule(self.goToSplashScreen)
        Clock.unschedule(self._do_alphabet_scroll)
        self.ids["userRecycleView"].unbind(on_scroll_move=self._on_user_list_scrolled)
        self.ids["userRecycleView"].data = []
        self._letter_index_map = {}
        return super().on_leave(*args)

    def cardRead(self, cardId, *args):
        patronId = self.manager.database.getPatronIdByCardId(cardId=cardId)
        if patronId is None:
            self.create_or_link_card_popup = CreateUserOrLinkCardPopup(
                screenManager=self.manager, readCard=cardId
            )
            self.create_or_link_card_popup.open()
            return

        self.manager.login(patronId)
        self.manager.transitionToScreen("mainUserPage")

    def goToSplashScreen(self, *args):
        self.manager.transitionToScreen("splashScreen", transitionDirection="right")

    def on_touch_down(self, touch):
        self.scroll_did_occur = False  # Reset scroll flag each touch sequence

        # Dispatch touch to RecycleView's child layout so user widgets
        # get immediate press feedback. RecycleView normally delays
        # child dispatch to distinguish scroll from tap, which suppresses
        # the press animation. This replicates FastTouchScrollView's
        # behaviour for RecycleView.
        rv = self.ids["userRecycleView"] if self._screen_active else None
        if rv and rv.collide_point(*touch.pos):
            touch.push()
            touch.apply_transform_2d(rv.to_local)
            for child in rv.children[:]:
                child.dispatch("on_touch_down", touch)
            touch.pop()

        # Reset timer for returning to splash screen
        if self.manager.settingsManager.get_setting_value(
            settingName=SettingName.GO_TO_SPLASH_SCREEN_ON_IDLE_ENABLE
        ):
            timeToAutoLogout = self.manager.settingsManager.get_setting_value(
                settingName=SettingName.GO_TO_SPLASH_SCREEN_ON_IDLE_TIME
            )
            Clock.unschedule(self.goToSplashScreen)
            Clock.schedule_once(self.goToSplashScreen, timeToAutoLogout)
        return super().on_touch_down(touch)

    def on_touch_move(self, touch):
        if not self.scroll_did_occur:
            drag = abs(touch.x - touch.ox)
            if drag > self._SCROLL_PX_THRESHOLD:
                self.scroll_did_occur = True
        return super().on_touch_move(touch)

    def _on_user_list_scrolled(self, scroll_view, touch, *args):
        # Fallback for RecycleView's scroll_move event (may not fire).
        # Primary detection is via on_touch_move above.
        drag = abs(touch.x - touch.ox)
        if drag > self._SCROLL_PX_THRESHOLD and not self.scroll_did_occur:
            self.scroll_did_occur = True
            logger.debug(
                "Scroll flagged (drag=%.1f px, threshold=%d px)",
                drag,
                self._SCROLL_PX_THRESHOLD,
            )

    # ------------------------------------------------------------------
    # Alphabet quick-scroll
    # ------------------------------------------------------------------

    def get_user_index_for_letter(self, letter: str):
        """Return the data index of the first user whose first name
        starts with *letter*."""
        return self._letter_index_map.get(letter)

    def on_alphabet_letter_selected(self, letter: str):
        """Scroll the carousel to centre the first user whose first
        name starts with *letter*."""
        index = self._letter_index_map.get(letter)
        if index is None:
            return
        # Cancel any in-progress scroll animation
        if self._scroll_event:
            self._scroll_event.cancel()
            self._scroll_event = None
        # Stop RecycleView's kinetic coasting from the finger swipe
        rv = self.ids["userRecycleView"]
        rv.effect_x.velocity = 0
        Clock.schedule_once(lambda dt: self._do_alphabet_scroll(index), 0)

    def _do_alphabet_scroll(self, index):
        """Scroll so user at *index* is centered in the viewport."""
        if not self._screen_active:
            return
        rv = self.ids["userRecycleView"]
        total = len(rv.data)
        if total <= 1:
            return
        # Each widget is square (width = height) with 15px spacing between
        item_w = rv.height
        spacing = 15
        content_w = total * item_w + (total - 1) * spacing
        viewport_w = rv.width
        scrollable = max(0, content_w - viewport_w)
        if scrollable <= 0:
            return
        item_center = index * (item_w + spacing) + item_w / 2
        target = max(0, min(1, (item_center - viewport_w / 2) / scrollable))

        # Cancel any previous scroll before starting a new one
        if self._scroll_event:
            self._scroll_event.cancel()

        start_x = rv.scroll_x
        start_t = _time.perf_counter()
        duration = 0.3

        def _anim_step(_dt):
            elapsed = _time.perf_counter() - start_t
            progress = min(1.0, elapsed / duration)
            eased = AnimationTransition.out_quad(progress)
            rv.scroll_x = start_x + (target - start_x) * eased
            if progress >= 1.0:
                self._scroll_event.cancel()
                self._scroll_event = None

        self._scroll_event = Clock.schedule_interval(_anim_step, 0)

    def back_button_pressed(self, *args):
        self.manager.transitionToScreen("splashScreen", transitionDirection="right")

    def createNewUserButtonClicked(self, *largs):
        self.manager.transitionToScreen("createUserScreen")
