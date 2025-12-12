from kivy.app import App
from kivy.properties import BooleanProperty, StringProperty
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from widgets.popups.adminPinEntryPopup import AdminPinEntryPopup


class BoxLayoutButton(ButtonBehavior, BoxLayout):
    pass


class NavigationHeader(GridLayout):
    __events__ = ("on_back_button_pressed", "on_logout_button_pressed")
    use_settings_button = BooleanProperty(False)
    page_name = StringProperty(None, allownone=True)

    def __init__(
        self,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.settings_button = None

    def on_kv_post(self, _):
        app = App.get_running_app()
        app.screenManager.bind(
            logged_in_user=lambda instance, value: self.set_welcome_name(value)
        )
        app.screenManager.bind(
            logged_in_user=lambda instance, value: self.set_current_credits(
                value.totalCredits if value else 0.0
            )
        )
        self.ids.backButton.bind(
            on_release=lambda instance: self.dispatch("on_back_button_pressed")
        )
        self.ids.logoutButton.bind(on_release=self.logout_button_pressed)

    def on_use_settings_button(self, _, value):
        if value:
            self.settings_button = NavigationSettingsButton()
            self.settings_button.bind(on_release=self.go_to_settings_screen)
            self.ids.rightContent.add_widget(self.settings_button)
        else:
            if self.settings_button:
                self.ids.rightContent.remove_widget(self.settings_button)
                self.settings_button = None

    def on_back_button_pressed(self, *largs):
        pass

    def on_logout_button_pressed(self, *largs):
        pass

    def go_to_settings_screen(self, *largs):
        app = App.get_running_app()

        # Show admin PIN popup
        def on_admin_pin_success():
            app.screenManager.transitionToScreen("adminScreen")

        admin_pin_popup = AdminPinEntryPopup(
            screen_manager=app.screenManager, on_success_callback=on_admin_pin_success
        )
        admin_pin_popup.open()

    def logout_button_pressed(self, *largs):
        self.dispatch("on_logout_button_pressed")
        app = App.get_running_app()
        app.screenManager.logout()
        app.screenManager.transitionToScreen(
            "splashScreen", transitionDirection="right"
        )

    def set_welcome_name(self, user_data):
        if user_data:
            full_name = f"{user_data.firstName} {user_data.lastName}"
            # Check if guest mode
            app = App.get_running_app()
            if (
                hasattr(app.screenManager, "is_guest_mode")
                and app.screenManager.is_guest_mode()
            ):
                self.ids.welcomeTextLabel.text = f"Welcome, {full_name} (Guest Mode)"
            else:
                self.ids.welcomeTextLabel.text = f"Welcome, {full_name}"
        else:
            self.ids.welcomeTextLabel.text = "Welcome, Guest"
        if self.page_name:
            self.ids.welcomeTextLabel.text += f" - {self.page_name}"

    def set_current_credits(self, current_credits):
        app = App.get_running_app()
        if (
            hasattr(app.screenManager, "is_guest_mode")
            and app.screenManager.is_guest_mode()
        ):
            self.ids.patronCreditsLabel.text = "Credits: N/A (Guest Mode)"
        else:
            self.ids.patronCreditsLabel.text = f"Your credits: {current_credits:.2f}"


class NavigationBackButton(BoxLayoutButton):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class NavigationSettingsButton(BoxLayoutButton):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
