from kivy.clock import Clock
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import Screen
from logger import get_logger
from widgets.popups.createUserOrLinkCardPopup import CreateUserOrLinkCardPopup
from widgets.settingsManager import SettingName
from widgets.uiElements.interactiveRecycleView import InteractiveRecycleDataViewBehavior
from app_types import UserData

logger = get_logger(__name__)


class LoginScreenUserWidget(InteractiveRecycleDataViewBehavior, BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.patronId = None
        self.first_name = ""
        self.last_name = ""

    def refresh_view_attrs(self, rv, index, data):
        self.first_name = data["first_name"]
        self.last_name = data["last_name"]
        self.patronId = data["patron_id"]

        self.ids.first_name_label.text = self.first_name
        self.ids.first_name_label.reset()
        self.ids.last_name_label.text = self.last_name
        self.ids.last_name_label.reset()

        return super().refresh_view_attrs(rv, index, data)


class LoginScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.create_or_link_card_popup = None

    def on_pre_enter(self, *args):
        self.ids.userRecycleView.bind(on_item_clicked=self._on_user_clicked)
        self.ids.userRecycleView.scroll_x = 0.5

        users = self.manager.database.getAllPatrons()
        users.sort(key=lambda u: u.firstName.lower())

        self._populate_users(users)

        available_initials = set(u.firstName[0].upper() for u in users if u.firstName)
        self.ids["alphabetStrip"].set_available_letters(available_initials)

        if self.manager.settingsManager.get_setting_value(
            settingName=SettingName.GO_TO_SPLASH_SCREEN_ON_IDLE_ENABLE
        ):
            Clock.schedule_once(
                self.go_to_splash_screen,
                self.manager.settingsManager.get_setting_value(
                    settingName=SettingName.GO_TO_SPLASH_SCREEN_ON_IDLE_TIME
                ),
            )

        return super().on_pre_enter(*args)

    def on_enter(self, *args):
        self.manager.RFIDReader.start(self.on_card_read)
        return super().on_enter(*args)

    def on_pre_leave(self, *args):
        if self.create_or_link_card_popup is not None:
            self.create_or_link_card_popup.dismiss()
            self.create_or_link_card_popup = None
        self.manager.RFIDReader.stop()
        return super().on_pre_leave(*args)

    def on_leave(self, *args):
        Clock.unschedule(self.go_to_splash_screen)
        self.ids["userRecycleView"].data = []
        return super().on_leave(*args)

    def _populate_users(self, users: list[UserData]):
        """Build RecycleView data from the list of users"""

        data = []
        for ud in users:
            data.append(
                {
                    "first_name": ud.firstName,
                    "last_name": ud.lastName,
                    "patron_id": ud.patronId,
                }
            )

        self.ids.userRecycleView.data = data

    def _on_user_clicked(self, instance, index):
        """Called when a user is clicked"""
        data = instance.data[index]
        patronId = data["patron_id"]
        logger.debug("Login click ACCEPTED for patronId=%s", patronId)
        self.manager.login(patronId)
        self.manager.transitionToScreen("mainUserPage")

    def on_card_read(self, cardId, *args):
        patronId = self.manager.database.getPatronIdByCardId(cardId=cardId)
        if patronId is None:
            self.create_or_link_card_popup = CreateUserOrLinkCardPopup(
                screenManager=self.manager, readCard=cardId
            )
            self.create_or_link_card_popup.open()
            return

        self.manager.login(patronId)
        self.manager.transitionToScreen("mainUserPage")

    def go_to_splash_screen(self, *args):
        self.manager.transitionToScreen("splashScreen", transitionDirection="right")

    def on_touch_down(self, touch):
        # Reset timer for returning to splash screen on any touch.
        if self.manager.settingsManager.get_setting_value(
            settingName=SettingName.GO_TO_SPLASH_SCREEN_ON_IDLE_ENABLE
        ):
            timeToAutoLogout = self.manager.settingsManager.get_setting_value(
                settingName=SettingName.GO_TO_SPLASH_SCREEN_ON_IDLE_TIME
            )
            Clock.unschedule(self.go_to_splash_screen)
            Clock.schedule_once(self.go_to_splash_screen, timeToAutoLogout)
        return super().on_touch_down(touch)

    def on_alphabet_letter_selected(self, letter: str):
        """Scroll to the first item whose first name starts with *letter*."""
        self.ids["userRecycleView"].scroll_to(
            lambda i, d: d["first_name"].upper().startswith(letter)
        )

    def back_button_pressed(self, *args):
        self.manager.transitionToScreen("splashScreen", transitionDirection="right")

    def create_new_user_clicked(self, *largs):
        self.manager.transitionToScreen("createUserScreen")
