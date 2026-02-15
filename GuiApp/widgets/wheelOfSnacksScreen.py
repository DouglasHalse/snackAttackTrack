from datetime import datetime

from widgets.GridLayoutScreen import GridLayoutScreen
from widgets.popups.insufficientFundsPopup import InsufficientFundsPopup
from widgets.popups.WinPopup import WinPopup
from widgets.settingsManager import SettingName


class WheelOfSnacksScreen(GridLayoutScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.ids.header.bind(on_back_button_pressed=self.on_back_button_pressed)
        self.ids.wheel_widget.bind(on_spin_complete=self.on_spin_complete)
        self.winPopup = None
        self.insufficient_funds_popup = None
        self.isSpinning = False
        self.selected_snacks_stash = []

    def on_back_button_pressed(self, *args):
        self.manager.transitionToScreen("mainUserPage", transitionDirection="right")

    def on_pre_enter(self, *args):
        super().on_pre_enter(*args)
        all_snacks = self.manager.database.getAllSnacks()
        # Order snacks by pricePerItem
        all_snacks = sorted(all_snacks, key=lambda x: x.pricePerItem, reverse=True)

        self.set_win_table_snacks(all_snacks)

        if self.selected_snacks_stash:
            for entry in self.ids.win_table.getEntries():
                if entry in self.selected_snacks_stash:
                    self.ids.win_table.toggleSelected(entry, selected=True)
                else:
                    self.ids.win_table.toggleSelected(entry, selected=False)

            selected_snacks = self.get_selected_snacks()
            self.ids.wheel_widget.set_snacks(selected_snacks)
            self.update_win_table_value_gains()
        else:
            self.ids.wheel_widget.set_snacks(all_snacks)

        self.ids.wheel_widget.enable = True
        self.update_price_label()

        # Disable spin button if less than 2 snacks are available
        self.ids.spin_button.disabled = len(all_snacks) < 2

    def on_pre_leave(self, *args):
        self.selected_snacks_stash = []

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
        selected_snack_ids = self.ids.win_table.getSelectedEntries()
        return [
            self.manager.database.getSnack(snackId=snackId)
            for snackId in selected_snack_ids
        ]

    def caluclate_cost_to_spin(self, selected_snacks):
        return round(
            sum(s.pricePerItem for s in selected_snacks) / len(selected_snacks), 2
        )

    def update_price_label(self):
        selected_snacks = self.get_selected_snacks()
        if len(selected_snacks) < 2:
            self.ids.cost_label.text = "Not enough snacks selected"
            return
        average_cost = self.caluclate_cost_to_spin(selected_snacks)

        self.ids.cost_label.text = f"One spin costs: {average_cost:.2f} Credits"

    def update_wheel_snacks(self):
        selected_snacks = self.get_selected_snacks()
        self.ids.wheel_widget.set_snacks(selected_snacks)

    def update_win_table_value_gains(self):
        selected_snacks_ids = self.ids.win_table.getSelectedEntries()
        unselected_snack_ids = self.ids.win_table.getUnselectedEntries()

        for unselected_snack_id in unselected_snack_ids:
            snack = self.manager.database.getSnack(snackId=unselected_snack_id)
            self.ids.win_table.updateEntry(
                entryIdentifier=unselected_snack_id,
                newEntryContents=[
                    snack.snackName,
                    "N/A",
                ],
            )

        if not selected_snacks_ids:
            return

        average_cost_of_selected_snacks = sum(
            self.manager.database.getSnack(snackId=snackId).pricePerItem
            for snackId in selected_snacks_ids
        ) / len(selected_snacks_ids)

        for selected_snack_id in selected_snacks_ids:
            snack = self.manager.database.getSnack(snackId=selected_snack_id)
            value_gain = (snack.pricePerItem) / average_cost_of_selected_snacks * 100
            self.ids.win_table.updateEntry(
                entryIdentifier=selected_snack_id,
                newEntryContents=[
                    snack.snackName,
                    f"{value_gain:.2f}%",
                ],
            )

    def set_win_table_snacks(self, snacks):
        self.ids.win_table.clearEntries()
        average_cost = sum(s.pricePerItem for s in snacks) / len(snacks)
        for snack in snacks:
            value_gain = (snack.pricePerItem) / average_cost * 100
            self.ids.win_table.addEntry(
                entryContents=[
                    snack.snackName,
                    f"{value_gain:.2f}%",
                ],
                entryIdentifier=snack.snackId,
            )

    def item_clicked(self, snackId: int):
        # Prevent changing selection while spinning
        if self.isSpinning:
            return

        self.ids.win_table.toggleSelected(snackId)
        self.update_win_table_value_gains()
        self.update_price_label()
        self.update_wheel_snacks()

        # Disable spin button if less than 2 snacks are selected
        self.ids.spin_button.disabled = len(self.get_selected_snacks()) < 2

    def on_spin_complete(self, caller, snack, *args):
        self.winPopup = WinPopup(
            won_item=snack.snackName, size=(self.width / 1.5, self.height / 2)
        )
        self.winPopup.open()

        self.isSpinning = False

        self.ids.spin_button.disabled = False
        self.enable_navigation_header_buttons(True)

        remaining_snacks = self.manager.database.getAllSnacks()
        remaining_snacks = sorted(
            remaining_snacks, key=lambda x: x.pricePerItem, reverse=True
        )

        # If there is only one snack left, go back to the main user page
        if len(remaining_snacks) == 1:
            self.manager.transitionToScreen("mainUserPage", transitionDirection="right")
            return

        # Get unselected snack ids to maintain their selection state after refreshing the win table
        unselected_snack_ids = self.ids.win_table.getUnselectedEntries()

        self.set_win_table_snacks(remaining_snacks)

        # Re-apply unselected state to snacks that were unselected before refreshing the win table
        for snack_id in self.ids.win_table.getEntries():
            if snack_id in unselected_snack_ids:
                self.ids.win_table.toggleSelected(snack_id, selected=False)

        # Disable spin button if less than 2 snacks are selected
        self.ids.spin_button.disabled = len(self.get_selected_snacks()) < 2

        self.update_price_label()
        selected_snacks = self.get_selected_snacks()
        self.ids.wheel_widget.set_snacks(selected_snacks)

    def on_spin_started(self, *args):
        pass

    def on_going_to_top_up_screen(self, *args):
        self.manager.top_up_requestee = "wheelOfSnacksScreen"
        self.selected_snacks_stash = self.ids.win_table.getSelectedEntries()

    def onSpinButtonPressed(self, *largs):

        selected_snacks = self.get_selected_snacks()

        cost_to_spin = self.caluclate_cost_to_spin(selected_snacks)

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

        self.isSpinning = True

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
