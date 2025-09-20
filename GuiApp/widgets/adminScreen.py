from widgets.GridLayoutScreen import GridLayoutScreen
from widgets.uiElements.buttons import ImageAndTextButton


class SystemSettingsOption(ImageAndTextButton):
    pass


class EditSnacksOption(ImageAndTextButton):
    pass


class EditUsersOption(ImageAndTextButton):
    pass


class AdminScreen(GridLayoutScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.ids.systemSettingsOption.bind(
            on_release=self.onSystemSettingsButtonPressed
        )
        self.ids.editSnacksOption.bind(on_release=self.onEditSnacksButtonPressed)
        self.ids.editUsersOption.bind(on_release=self.onEditUsersButtonPressed)
        self.ids.header.bind(on_back_button_pressed=self.onBackButtonPressed)

    def onSystemSettingsButtonPressed(self, _):
        self.manager.transitionToScreen("editSystemSettingsScreen")

    def onEditSnacksButtonPressed(self, _):
        self.manager.transitionToScreen("editSnacksScreen")

    def onEditUsersButtonPressed(self, _):
        self.manager.transitionToScreen("editUsersScreen")

    def onBackButtonPressed(self, _):
        self.manager.transitionToScreen("mainUserPage", transitionDirection="right")
