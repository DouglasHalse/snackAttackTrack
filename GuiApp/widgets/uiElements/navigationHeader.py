from kivy.app import App
from kivy.properties import BooleanProperty, StringProperty
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout


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
            logged_in_user=lambda instance, value: self.set_welcome_name(
                value.firstName if value else "Guest"
            )
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
        app.screenManager.transitionToScreen("adminScreen")

    def logout_button_pressed(self, *largs):
        self.dispatch("on_logout_button_pressed")
        app = App.get_running_app()
        app.screenManager.logout()
        app.screenManager.transitionToScreen(
            "splashScreen", transitionDirection="right"
        )

    def set_welcome_name(self, first_name):
        self.ids.welcomeTextLabel.text = f"Welcome, {first_name}"
        if self.page_name:
            self.ids.welcomeTextLabel.text += f" - {self.page_name}"

    def set_current_credits(self, current_credits):
        self.ids.patronCreditsLabel.text = f"Your credits: {current_credits:.2f}"


class NavigationBackButton(BoxLayoutButton):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class NavigationSettingsButton(BoxLayoutButton):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
