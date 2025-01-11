from kivy.uix.gridlayout import GridLayout


class TextInputWithHeader(GridLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def setInputChangedCallback(self, callback):
        self.ids["input"].bind(text=callback)

    def getText(self) -> str:
        return self.ids["input"].text

    def setText(self, text: str):
        self.ids["input"].text = text

    def clearText(self):
        self.ids["input"].text = ""


class LargeTextInputWithHeader(TextInputWithHeader):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
