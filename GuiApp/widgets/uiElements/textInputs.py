import re

from kivy.clock import Clock
from kivy.uix.gridlayout import GridLayout
from kivy.uix.modalview import ModalView


class TextInputWithHeader(GridLayout):
    def __init__(self, enableVirtualKeyboardEntry: bool = True, **kwargs):
        super().__init__(**kwargs)
        self.enableVirtualKeyboardEntry = enableVirtualKeyboardEntry
        Clock.schedule_once(self.init_ui, 0)

    def init_ui(self, dt):
        self.ids["input"].bind(focus=self.on_focus)

    def setInputChangedCallback(self, callback):
        self.ids["input"].bind(text=callback)

    def getText(self) -> str:
        return self.ids["input"].text

    def setText(self, text: str):
        self.ids["input"].text = text

    def clearText(self):
        self.ids["input"].text = ""

    def doBackspace(self):
        self.ids["input"].do_backspace()

    def insertText(self, text: str):
        self.ids["input"].insert_text(text)

    def setFocus(self, value: bool):
        self.ids["input"].focus = value

    def on_focus(self, instance, value):
        if value and self.enableVirtualKeyboardEntry:
            TextInputPopup(
                originalTextInputWidget=self.ids["input"],
                headerText=self.header_text,
                hintText=self.hint_text,
                inputFilter=self.input_filter,
            ).open()


class LargeTextInputWithHeader(TextInputWithHeader):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class TextInputPopup(ModalView):
    def __init__(
        self,
        originalTextInputWidget,
        headerText: str,
        hintText: str,
        inputFilter: str,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.originalTextInputWidget = originalTextInputWidget
        self.input_filter = inputFilter

        # Make copy of input widget
        self.ids["textInput"].header_text = headerText
        self.ids["textInput"].hint_text = hintText
        self.ids["textInput"].input_filter = (
            "float" if inputFilter == "currency" else inputFilter
        )
        self.ids["textInput"].setText(self.originalTextInputWidget.text)
        self.isCapslockActive = False

        if inputFilter in ("float", "currency", "int"):
            self.ids["virtualKeyboard"].layout = "keyboards/numericKeyboardLayout.json"
        else:
            self.ids["virtualKeyboard"].layout = "keyboards/swedishKeyboardLayout.json"

        self.ids["virtualKeyboard"].bind(on_key_up=self.virtualKeyboardInputUp)

    def virtualKeyboardInputUp(self, keyboard, keycode, *args):
        if keycode == "backspace":
            self.ids["textInput"].doBackspace()
            return

        if keycode in ("enter", "escape", "layout"):
            self.dismiss()
            return

        if keycode == "tab":
            return

        if keycode in ("capslock", "shift"):
            self.isCapslockActive = not self.isCapslockActive
            return

        finalSymbolToAdd = keycode

        if keycode == "spacebar":
            finalSymbolToAdd = " "

        if self.isCapslockActive:
            finalSymbolToAdd = finalSymbolToAdd.upper()

        if self.input_filter == "currency":
            current_text = self.ids["textInput"].getText()
            # Simulate the new text after input
            new_text = current_text + finalSymbolToAdd
            # Only allow digits and one decimal point, and max two decimals

            if not re.match(r"^\d*\.?\d{0,2}$", new_text):
                return

        self.ids["textInput"].insertText(finalSymbolToAdd)

    def on_dismiss(self):
        self.originalTextInputWidget.text = self.ids["textInput"].getText()
        self.originalTextInputWidget.focus = False
        return super().on_dismiss()
