from datetime import datetime

from database import (
    addGambleTransaction,
    getAllSnacks,
    removeSnack,
    subtractPatronCredits,
    subtractSnackQuantity,
)
from kivy.uix.gridlayout import GridLayout
from widgets.customScreenManager import CustomScreenManager
from widgets.headerBodyLayout import HeaderBodyScreen
from widgets.popups.insufficientFundsPopup import InsufficientFundsPopup
from widgets.popups.WinPopup import WinPopup
from widgets.settingsManager import SettingName


class WheelOfSnacksContent(GridLayout):
    __events__ = ("on_spin_started",)

    def __init__(self, screenManager: CustomScreenManager, **kwargs):
        super().__init__(**kwargs)
        self.screenManager = screenManager
        snacks = getAllSnacks()
        # Order snacks by pricePerItem
        snacks = sorted(snacks, key=lambda x: x.pricePerItem, reverse=True)

        average_cost = sum(s.pricePerItem for s in snacks) / len(snacks)
        self.ids.cost_label.text = f"One spin costs: {average_cost:.2f} Credits"
        self.set_win_table_snacks(snacks)
        self.ids.wheel_widget.set_snacks(snacks)
        self.ids.wheel_widget.bind(on_spin_complete=self.on_spin_complete)
        self.winPopup = None

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
                entryIdentifier=None,
            )

    def on_spin_complete(self, caller, snack, *args):
        self.winPopup = WinPopup(
            won_item=snack.snackName, size=(self.width / 1.5, self.height / 2)
        )
        self.winPopup.open()

        self.ids.spin_button.disabled = False
        self.dispatch("on_spin_started", False)

        new_snacks = getAllSnacks()
        new_snacks = sorted(new_snacks, key=lambda x: x.pricePerItem, reverse=True)

        # If there is only one snack left, go back to the main user page
        if len(new_snacks) == 1:
            self.screenManager.transitionToScreen(
                "mainUserPage", transitionDirection="right"
            )
            return

        average_cost = sum(s.pricePerItem for s in new_snacks) / len(new_snacks)
        self.ids.cost_label.text = f"One spin costs: {average_cost:.2f} Credits"
        self.ids.wheel_widget.set_snacks(new_snacks)
        self.set_win_table_snacks(new_snacks)

    def on_spin_started(self, *args):
        pass

    def onSpinButtonPressed(self, *largs):

        snacks = getAllSnacks()
        cost_to_spin = round(sum(s.pricePerItem for s in snacks) / len(snacks), 2)

        currentPatron = self.screenManager.getCurrentPatron()
        if currentPatron.totalCredits < cost_to_spin:
            popup = InsufficientFundsPopup(screenManager=self.screenManager)
            popup.open()
            return

        #
        # Spin validation passed
        #

        exciting = self.screenManager.settingsManager.get_setting_value(
            settingName=SettingName.EXCITING_GAMBLING
        )

        self.ids.spin_button.disabled = True
        won_snack = self.ids.wheel_widget.spin(exciting)

        subtractPatronCredits(
            patronID=currentPatron.patronId, creditsToSubtract=cost_to_spin
        )

        if won_snack.quantity == 1:
            removeSnack(snackId=won_snack.snackId)
        else:
            subtractSnackQuantity(snackId=won_snack.snackId, quantity=1)

        won_snack.quantity = 1  # Assuming one snack is won per spin

        addGambleTransaction(
            patronID=currentPatron.patronId,
            amountBeforeTransaction=currentPatron.totalCredits,
            amountAfterTransaction=currentPatron.totalCredits - cost_to_spin,
            transactionDate=datetime.now(),
            transactionItem=won_snack,
        )

        # Update current patron with new data
        self.screenManager.refreshCurrentPatron()

        self.dispatch("on_spin_started", True)


class WheelOfSnacksScreen(HeaderBodyScreen):
    def __init__(self, **kwargs):
        super().__init__(previousScreen="mainUserPage", **kwargs)
        self.headerSuffix = "Wheel of Snacks"
        self.content = None

    def on_pre_enter(self, *args):
        super().on_pre_enter(*args)
        self.content = WheelOfSnacksContent(screenManager=self.manager)
        self.body.add_widget(self.content)
        self.content.bind(on_spin_started=self.on_enable_buttons)

    def on_leave(self, *args):
        super().on_leave(*args)
        self.content.ids.wheel_widget.cleanup()

    def on_enable_buttons(self, instance, spinning_started):
        self.header.ids.logoutButton.disabled = spinning_started
        self.header.backButton.disabled = spinning_started
        if spinning_started:
            self.header.refreshHeader()
