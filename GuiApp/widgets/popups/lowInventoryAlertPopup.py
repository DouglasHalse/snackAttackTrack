from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.modalview import ModalView


class LowInventoryAlertPopup(ModalView):
    """Popup to alert about snacks with low inventory."""

    def __init__(self, snacks, **kwargs):
        super().__init__(**kwargs)
        self.snacks = snacks
        # Populate snack list after the widget is fully initialized
        self.bind(on_open=self.populate_snacks)

    def populate_snacks(self, *args):
        """Populate the snack list dynamically."""
        snack_container = self.ids.snack_container
        snack_container.clear_widgets()

        for snack in self.snacks:
            # Create a grid for each snack entry
            entry = GridLayout(cols=3, size_hint_y=None, height=35, spacing=10)

            # Snack name
            name_label = Label(
                text=snack.snackName,
                font_size=16,
                color=(1, 1, 1, 1),
                halign="left",
                valign="middle",
                size_hint_x=0.5,
            )
            name_label.bind(size=name_label.setter("text_size"))

            # Quantity (red if 0, orange if low)
            quantity_color = (1, 0.2, 0.2, 1) if snack.quantity == 0 else (1, 0.7, 0, 1)
            quantity_label = Label(
                text=str(snack.quantity),
                font_size=16,
                color=quantity_color,
                halign="center",
                valign="middle",
                bold=True,
                size_hint_x=0.25,
            )
            quantity_label.bind(size=quantity_label.setter("text_size"))

            # Price
            price_label = Label(
                text=f"{snack.pricePerItem:.2f}",
                font_size=16,
                color=(1, 1, 1, 1),
                halign="right",
                valign="middle",
                size_hint_x=0.25,
            )
            price_label.bind(size=price_label.setter("text_size"))

            entry.add_widget(name_label)
            entry.add_widget(quantity_label)
            entry.add_widget(price_label)

            snack_container.add_widget(entry)

    def on_dismiss_pressed(self):
        """Handle dismiss button press."""
        self.dismiss()
