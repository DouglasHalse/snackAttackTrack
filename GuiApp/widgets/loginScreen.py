from app_types import UserData
from kivy.animation import Animation
from kivy.clock import Clock
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import Screen
from logger import get_logger
from widgets.customScreenManager import CustomScreenManager
from widgets.popups.createUserOrLinkCardPopup import CreateUserOrLinkCardPopup
from widgets.settingsManager import SettingName

logger = get_logger(__name__)


class LoginScreenUserWidget(ButtonBehavior, BoxLayout):
    def __init__(
        self, userData: UserData, screenManager: CustomScreenManager, **kwargs
    ):
        super().__init__(**kwargs)
        self.screenManager = screenManager
        self.userData = userData
        self.first_name = userData.firstName
        self.last_name = userData.lastName

    def Clicked(self, *largs):
        # Suppress login if the user was scrolling, not tapping
        if self.screenManager.current_screen.scroll_did_occur:
            logger.debug(
                "Login click REJECTED for %s %s (patronId=%s) — scroll detected",
                self.first_name,
                self.last_name,
                self.userData.patronId,
            )
            return
        logger.debug(
            "Login click ACCEPTED for %s %s (patronId=%s)",
            self.first_name,
            self.last_name,
            self.userData.patronId,
        )
        self.screenManager.login(self.userData.patronId)
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
        self._letter_widget_map = {}

    def on_pre_enter(self, *args):
        self._screen_active = True
        self.AddUsersToLoginScreen()
        self.ids["scrollView"].bind(on_scroll_move=self._on_user_list_scrolled)
        self.ids["scrollView"].scroll_x = 0.5

        self.ids["alphabetStrip"].set_available_letters(self._letter_widget_map.keys())

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

    def on_enter(self, *args):
        self.manager.RFIDReader.start(self.cardRead)
        return super().on_enter(*args)

    def on_pre_leave(self, *args):
        if self.create_or_link_card_popup is not None:
            self.create_or_link_card_popup = None
        self.manager.RFIDReader.stop()
        return super().on_pre_leave(*args)

    def on_leave(self, *args):
        self._screen_active = False
        Clock.unschedule(self.goToSplashScreen)
        Clock.unschedule(self._do_alphabet_scroll)
        self.ids["scrollView"].unbind(on_scroll_move=self._on_user_list_scrolled)
        self.ids["LoginScreenUserGridLayout"].clear_widgets()
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

    def AddUsersToLoginScreen(self):
        userDataList = self.manager.database.getAllPatrons()
        self._letter_widget_map.clear()
        if userDataList:
            userDataList.sort(key=lambda u: u.firstName.lower())
            for userData in userDataList:
                widget = LoginScreenUserWidget(
                    userData=userData, screenManager=self.manager
                )
                self.ids["LoginScreenUserGridLayout"].add_widget(widget)
                first_letter = userData.firstName[0].upper()
                if first_letter not in self._letter_widget_map:
                    self._letter_widget_map[first_letter] = widget

    def _on_user_list_scrolled(self, scroll_view, touch, *args):
        # touch.ox is the origin x at touch-down, touch.x is current.
        # Only flag as a scroll once the total horizontal drag exceeds
        # the pixel threshold. This prevents tiny accidental movements
        # during a tap from suppressing the click.
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

    def get_user_widget_for_letter(self, letter: str):
        """Return the first user widget whose first name starts with *letter*."""
        return self._letter_widget_map.get(letter)

    def on_alphabet_letter_selected(self, letter: str):
        """Scroll the carousel to centre the first user whose first
        name starts with *letter*."""
        widget = self._letter_widget_map.get(letter)
        if widget is None:
            return
        sv = self.ids["scrollView"]
        sv.cancel_active_scroll()

        target_widget = widget
        Clock.schedule_once(lambda dt, w=target_widget: self._do_alphabet_scroll(w), 0)

    def _do_alphabet_scroll(self, widget):
        """Scroll so the target widget is centered in the viewport."""
        if not self._screen_active:
            return
        sv = self.ids["scrollView"]
        grid = self.ids["LoginScreenUserGridLayout"]
        content_w = max(0, grid.width - sv.width)
        if content_w <= 0:
            return
        widget_center = widget.x + widget.width / 2
        target = (widget_center - sv.width / 2) / content_w
        target = max(0, min(target, 1))
        Animation(scroll_x=target, d=0.3, t="out_quad").start(sv)

    def back_button_pressed(self, *args):
        self.manager.transitionToScreen("splashScreen", transitionDirection="right")

    def createNewUserButtonClicked(self, *largs):
        self.manager.transitionToScreen("createUserScreen")
