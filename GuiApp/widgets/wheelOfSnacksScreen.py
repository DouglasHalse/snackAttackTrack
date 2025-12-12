from datetime import datetime

from widgets.GridLayoutScreen import GridLayoutScreen
from widgets.popups.errorMessagePopup import ErrorMessagePopup
from widgets.popups.insufficientFundsPopup import InsufficientFundsPopup
from widgets.popups.WinPopup import WinPopup
from widgets.settingsManager import SettingName


class WheelOfSnacksScreen(GridLayoutScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.ids.header.bind(on_back_button_pressed=self.on_back_button_pressed)
        self.winPopup = None
        self.insufficient_funds_popup = None
        self.all_snacks = []
        self.selected_snack_ids = set()

    def on_back_button_pressed(self, *args):
        self.manager.transitionToScreen("mainUserPage", transitionDirection="right")

    def on_pre_enter(self, *args):
        super().on_pre_enter(*args)
        self.all_snacks = self.manager.database.getAllSnacks()
        # Order snacks by pricePerItem
        self.all_snacks = sorted(
            self.all_snacks, key=lambda x: x.pricePerItem, reverse=True
        )

        # Initialize all snacks as selected
        if not self.selected_snack_ids:
            self.selected_snack_ids = {snack.snackId for snack in self.all_snacks}

        # Remove any selected IDs that no longer exist
        existing_ids = {snack.snackId for snack in self.all_snacks}
        self.selected_snack_ids = self.selected_snack_ids.intersection(existing_ids)

        # Ensure at least 2 snacks are selected
        if len(self.selected_snack_ids) < 2:
            self.selected_snack_ids = {snack.snackId for snack in self.all_snacks}

        self.update_display()
        self.ids.wheel_widget.enable = True
        self.ids.wheel_widget.bind(on_spin_complete=self.on_spin_complete)

    def on_leave(self, *args):
        self.ids.wheel_widget.enable = False
        if self.insufficient_funds_popup is not None:
            self.insufficient_funds_popup.dismiss()
            self.insufficient_funds_popup = None

    def enable_navigation_header_buttons(self, enable: bool):
        self.ids.header.ids.logoutButton.disabled = not enable
        self.ids.header.ids.backButton.disabled = not enable
        if not enable:
            self.manager.refreshCurrentPatron()

    def get_selected_snacks(self):
        return [s for s in self.all_snacks if s.snackId in self.selected_snack_ids]

    def update_display(self):
        selected_snacks = self.get_selected_snacks()
        if not selected_snacks:
            return

        average_cost = sum(s.pricePerItem for s in selected_snacks) / len(
            selected_snacks
        )
        self.ids.cost_label.text = f"One spin costs: {average_cost:.2f} Credits"
        self.set_win_table_snacks(selected_snacks)
        self.ids.wheel_widget.set_snacks(selected_snacks)

    def toggle_snack_selection(self, snack_id):
        selected_snacks = self.get_selected_snacks()

        # If trying to deselect and only 2 snacks are selected, show error
        if snack_id in self.selected_snack_ids and len(selected_snacks) <= 2:
            ErrorMessagePopup(errorMessage="At least 2 snacks must be selected").open()
            return

        # Toggle selection
        if snack_id in self.selected_snack_ids:
            self.selected_snack_ids.remove(snack_id)
        else:
            self.selected_snack_ids.add(snack_id)

        self.update_display()

    def set_win_table_snacks(self, snacks):
        self.ids.win_table.clearEntries()
        average_cost = sum(s.pricePerItem for s in snacks) / len(snacks)
        for snack in self.all_snacks:
            is_selected = snack.snackId in self.selected_snack_ids
            value_gain = (snack.pricePerItem) / average_cost * 100 if is_selected else 0
            checkbox = "☑" if is_selected else "☐"
            self.ids.win_table.addEntry(
                entryContents=[
                    checkbox,
                    snack.snackName,
                    f"{value_gain:.2f}%" if is_selected else "-",
                ],
                entryIdentifier=snack.snackId,
            )

    def on_spin_complete(self, caller, snack, *args):
        self.winPopup = WinPopup(
            won_item=snack.snackName, size=(self.width / 1.5, self.height / 2)
        )
        self.winPopup.open()

        self.ids.spin_button.disabled = False
        self.enable_navigation_header_buttons(True)

        self.all_snacks = self.manager.database.getAllSnacks()
        self.all_snacks = sorted(
            self.all_snacks, key=lambda x: x.pricePerItem, reverse=True
        )

        # Remove won snack from selection if it was the last one
        if snack.snackId in self.selected_snack_ids and snack.quantity == 0:
            self.selected_snack_ids.discard(snack.snackId)

        # Check if we have enough snacks left
        existing_ids = {s.snackId for s in self.all_snacks}
        self.selected_snack_ids = self.selected_snack_ids.intersection(existing_ids)

        selected_snacks = self.get_selected_snacks()

        # If less than 2 snacks remain in total, go back
        if len(self.all_snacks) < 2:
            self.manager.transitionToScreen("mainUserPage", transitionDirection="right")
            return

        # If less than 2 selected snacks remain, select all
        if len(selected_snacks) < 2:
            self.selected_snack_ids = {s.snackId for s in self.all_snacks}

        self.update_display()

    def on_spin_started(self, *args):
        pass

    def on_going_to_top_up_screen(self, *args):
        self.manager.top_up_requestee = "wheelOfSnacksScreen"

    def onSpinButtonPressed(self, *largs):
        selected_snacks = self.get_selected_snacks()

        if len(selected_snacks) < 2:
            ErrorMessagePopup(errorMessage="Please select at least 2 snacks").open()
            return

        cost_to_spin = round(
            sum(s.pricePerItem for s in selected_snacks) / len(selected_snacks), 2
        )

        currentPatron = self.manager.getCurrentPatron()
        if currentPatron.totalCredits < cost_to_spin:
            credits_needed = cost_to_spin - currentPatron.totalCredits
            self.insufficient_funds_popup = InsufficientFundsPopup(
                screen_manager=self.manager, credits_needed=credits_needed
            )
            self.insufficient_funds_popup.bind(
                on_top_up_pressed=self.on_going_to_top_up_screen
            )
            self.insufficient_funds_popup.open()
            return

        #
        # Spin validation passed
        #

        exciting = self.manager.settingsManager.get_setting_value(
            settingName=SettingName.EXCITING_GAMBLING
        )

        self.ids.spin_button.disabled = True
        won_snack = self.ids.wheel_widget.spin(exciting)

        self.manager.database.subtractPatronCredits(
            patronID=currentPatron.patronId, creditsToSubtract=cost_to_spin
        )

        if won_snack.quantity == 1:
            self.manager.database.removeSnack(snackId=won_snack.snackId)
        else:
            self.manager.database.subtractSnackQuantity(
                snackId=won_snack.snackId, quantity=1
            )

        won_snack.quantity = 1  # Assuming one snack is won per spin

        self.manager.database.addGambleTransaction(
            patronID=currentPatron.patronId,
            amountBeforeTransaction=currentPatron.totalCredits,
            amountAfterTransaction=currentPatron.totalCredits - cost_to_spin,
            transactionDate=datetime.now(),
            transactionItem=won_snack,
        )

        # Update current patron with new data
        self.manager.refreshCurrentPatron()

        self.enable_navigation_header_buttons(False)
