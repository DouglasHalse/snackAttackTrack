from kivy.uix.screenmanager import Screen
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.graphics import RoundedRectangle, Color

from database import getAllPatrons, getPatronData, UserData


class ClickableBoxLayout(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def on_touch_down(self, touch):
        if self.collide_point(touch.x, touch.y):
            self.on_click()
            return True
        return super().on_touch_down(touch)

    def on_click(self):
        patron_data = self.children[3].text
        print(f"Clicked on row with Patron: {patron_data}")


class EditUsersScreenHeader(GridLayout):
    def __init__(self, editUsersScreen, userData: UserData, **kwargs):
        super().__init__(**kwargs)
        self.mainUserScreen = editUsersScreen
        self.ids.welcomeTextLabel.text = (
            f"Welcome {userData.firstName} - edit users screen"
        )

    def onLogoutButtonPressed(self, *largs):
        self.mainUserScreen.logout()


class EditUsersScreenBody(GridLayout):
    def __init__(self, editUsersScreen, **kwargs):
        super().__init__(**kwargs)
        grid = self.ids.patron_grid
        for patron in getAllPatrons():
            row = ClickableBoxLayout(
                orientation="horizontal", size_hint_y=None, height=40
            )
            with row.canvas.before:
                Color(0.5, 0.5, 0.5, 1)
                RoundedRectangle(pos=row.pos, size=row.size)

            # Bind to update the background position and size when the layout is resized or moved
            row.bind(
                pos=lambda instance, value: setattr(
                    instance.canvas.before.children[-1], "pos", value
                )
            )
            row.bind(
                size=lambda instance, value: setattr(
                    instance.canvas.before.children[-1], "size", value
                )
            )

            # Add each column (label) in the row
            row.add_widget(
                Label(
                    text=patron.firstName,
                    halign="left",
                    text_size=(150, 30),
                    size_hint_x=None,
                    width=200,
                )
            )
            row.add_widget(
                Label(
                    text=patron.lastName,
                    halign="left",
                    text_size=(150, 30),
                    size_hint_x=None,
                    width=200,
                )
            )
            row.add_widget(
                Label(
                    text=patron.employeeID,
                    halign="left",
                    text_size=(150, 30),
                    size_hint_x=None,
                    width=200,
                )
            )
            row.add_widget(
                Label(
                    text=str(patron.totalCredits),
                    halign="left",
                    text_size=(150, 30),
                    size_hint_x=None,
                    width=200,
                )
            )

            grid.add_widget(row)


class EditUsersScreenWidget(Screen):
    userName = ""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.userData = None

    def setUserId(self, userId: int):
        self.userData = getPatronData(userId)
        header = EditUsersScreenHeader(self, self.userData)
        self.ids["editUsersScreenGridLayout"].add_widget(header)
        body = EditUsersScreenBody(self)
        self.ids["editUsersScreenGridLayout"].add_widget(body)

    def logout(self):
        self.ids["editUsersScreenGridLayout"].clear_widgets()
        self.manager.current = "adminScreen"
