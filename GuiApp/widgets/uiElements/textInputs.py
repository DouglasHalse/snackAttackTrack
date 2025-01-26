from kivy.uix.gridlayout import GridLayout
from kivy.clock import Clock
from kivy.uix.vkeyboard import VKeyboard
from kivy.uix.popup import Popup


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


class TextInputPopup(Popup):
    def __init__(
        self,
        originalTextInputWidget,
        headerText: str,
        hintText: str,
        inputFilter: str,
        **kwargs
    ):
        super().__init__(**kwargs)
        self.originalTextInputWidget = originalTextInputWidget

        # Make copy of input widget
        self.ids["textInput"].header_text = headerText
        self.ids["textInput"].hint_text = hintText
        self.ids["textInput"].input_filter = inputFilter
        self.ids["textInput"].setText(self.originalTextInputWidget.text)
        self.isCapslockActive = False
        self.isShiftActive = False

        self.kb = VKeyboard(
            on_key_up=self.virtualKeyboardInputUp,
            on_key_down=self.virtualKeyboardInputDown,
            pos_hint={"center_x": 0.5},
            size_hint=(0.8, None),
        )
        self.kb.layout = "keyboards/swedishKeyboardLayout.json"
        self.ids["keyboardLayout"].add_widget(self.kb)
        self.ids["textInput"].setFocus(True)

    def virtualKeyboardInputUp(self, keyboard, keycode, *args):
        if keycode == "backspace":
            self.ids["textInput"].doBackspace()
            return

        if keycode in ("enter", "escape", "layout"):
            self.dismiss()
            return

        if keycode == "tab":
            return

        if keycode == "shift":
            self.isShiftActive = False
            return

        if keycode == "capslock":
            self.isCapslockActive = not self.isCapslockActive
            return

        finalSymbolToAdd = keycode

        if keycode == "spacebar":
            finalSymbolToAdd = " "

        if self.isShiftActive and not self.isCapslockActive:
            finalSymbolToAdd = finalSymbolToAdd.upper()

        if self.isCapslockActive and not self.isShiftActive:
            finalSymbolToAdd = finalSymbolToAdd.upper()

        self.ids["textInput"].insertText(finalSymbolToAdd)

    def virtualKeyboardInputDown(self, keyboard, keycode, *args):
        if keycode == "shift":
            self.isShiftActive = True

    def on_dismiss(self):
        self.originalTextInputWidget.text = self.ids["textInput"].getText()
        self.originalTextInputWidget.focus = False
        self.ids["keyboardLayout"].remove_widget(self.kb)
        return super().on_dismiss()
