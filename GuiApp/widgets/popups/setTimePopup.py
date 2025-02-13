import os
import datetime

from kivy.uix.modalview import ModalView
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.popup import Popup


class SetTimePopup(ModalView):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.title = "Set Date and Time"

        now = datetime.datetime.now()
        self.ids["dateInput"].setText(now.strftime("%Y-%m-%d"))
        self.ids["timeInput"].setText(now.strftime("%H:%M:%S"))

    def set_time(self, instance):
        date = self.date_input.text
        time = self.time_input.text
        datetime_str = f"{date} {time}"

        try:
            # Try to parse the date and time to verify the format
            datetime.datetime.strptime(datetime_str, "%Y-%m-%d %H:%M:%S")
            os.system(f'sudo date -s "{datetime_str}"')
            self.dismiss()
            # self.prompt_reboot()
        except ValueError:
            # Display an error message if the format is incorrect
            error_popup = Popup(
                title="Invalid Format",
                content=Label(
                    text="Please enter a valid date and time in the format YYYY-MM-DD HH:MM:SS."
                ),
                size_hint=(0.8, 0.3),
                auto_dismiss=True,
            )
            error_popup.open()

    def prompt_reboot(self):
        reboot_popup = Popup(
            title="Reboot Required",
            content=Label(
                text="The system time has been updated. Please reboot the Raspberry Pi."
            ),
            size_hint=(0.8, 0.3),
            auto_dismiss=False,
        )
        reboot_button = Button(text="Reboot Now", on_press=self.reboot_system)
        reboot_popup.content.add_widget(reboot_button)
        reboot_popup.open()

    def reboot_system(self, instance):
        os.system("sudo reboot")
