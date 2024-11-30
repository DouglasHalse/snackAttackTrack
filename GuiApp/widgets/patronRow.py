from kivy.uix.boxlayout import BoxLayout


class PatronRowWidget(BoxLayout):
    def __init__(
        self, firstName: str = "", lastName: str = "", employeeID: str = "", **kwargs
    ):
        super().__init__(**kwargs)
        self.patronFirstName = firstName
        self.patronLastName = lastName
        self.patronEmployeeID = employeeID
