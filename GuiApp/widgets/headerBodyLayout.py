from kivy.uix.screenmanager import Screen
from kivy.uix.gridlayout import GridLayout
from kivy.uix.screenmanager import ScreenManager
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.image import Image


class ImageButton(ButtonBehavior, Image):
    pass


class Header(GridLayout):
    def __init__(
        self,
        screenManager: ScreenManager,
        enableSettingsButton: bool = False,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.screenManager = screenManager
        self.currentPatron = self.screenManager.getCurrentPatron()
        self.ids["welcomeTextLabel"].text = f"Welcome {self.currentPatron.firstName}"
        if enableSettingsButton:
            self.ids["rightContent"].add_widget(
                SettingsButton(screenManager=self.screenManager)
            )

    def onLogoutButtonPressed(self, *largs):
        self.screenManager.current = "splashScreen"

    def setSuffix(self, suffix: str):
        self.ids["welcomeTextLabel"].text += " - " + suffix


class Body(GridLayout):
    def __init__(self, screenManager: ScreenManager, **kwargs):
        super().__init__(**kwargs)
        self.screenManager = screenManager


class SettingsButton(ImageButton):
    def __init__(self, screenManager: ScreenManager, **kwargs):
        super().__init__(**kwargs)
        self.screenManager = screenManager

    def onPressed(self, *largs):
        self.screenManager.current = "adminScreen"


class HeaderBodyScreen(Screen):
    header: Header
    body: Body

    def __init__(self, enableSettingsButton: bool = False, **kwargs):
        super().__init__(**kwargs)
        self.enableSettingsButton = enableSettingsButton
        self.headerSuffix = None
        self.header = None
        self.body = None

    def on_pre_enter(self, *args):
        super().on_pre_enter(*args)
        self.header = Header(
            screenManager=self.manager,
            enableSettingsButton=self.enableSettingsButton,
        )
        if self.headerSuffix:
            self.header.setSuffix(self.headerSuffix)
        self.ids["screenLayout"].add_widget(self.header)

        self.body = Body(screenManager=self.manager)
        self.ids["screenLayout"].add_widget(self.body)

    def on_leave(self, *args):
        self.ids["screenLayout"].clear_widgets()
        return super().on_leave(*args)
