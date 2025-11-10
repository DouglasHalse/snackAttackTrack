from database import LostSnackReason, SnackData
from kivy.properties import ObjectProperty
from widgets.GridLayoutScreen import GridLayoutScreen
from widgets.popups.addedSnackPricePopup import AddedSnackPricePopup
from widgets.popups.errorMessagePopup import ErrorMessagePopup
from widgets.popups.removalReasonPopup import RemovalReasonPopup
from widgets.popups.removeConfirmationPopup import RemoveConfirmationPopup


class EditSnackScreen(GridLayoutScreen):
    snack_to_edit = ObjectProperty(None, allownone=True)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.ids.header.bind(on_back_button_pressed=self.on_back_button_pressed)

    def on_back_button_pressed(self, *args):
        self.manager.transitionToScreen("editSnacksScreen", transitionDirection="right")

    def on_leave(self, *args):
        self.snack_to_edit = None
        super().on_leave(*args)

    def on_snack_to_edit(self, _, value):
        if value:
            self.ids.snackNameInput.setText(value.snackName)
            self.ids.snackQuantityInput.setText(str(value.quantity))
            self.ids.snackPriceInput.setText(f"{value.pricePerItem:.2f}")
        else:
            self.ids.snackNameInput.setText("SNACKNAME")
            self.ids.snackQuantityInput.setText("QUANTITY")
            self.ids.snackPriceInput.setText("PRICE")

    def onConfirm(self):
        newSnackName = self.ids["snackNameInput"].getText()
        if newSnackName == "":
            ErrorMessagePopup(errorMessage="Snack Name cannot be empty").open()
            return

        try:
            newSnackQuantity = int(self.ids["snackQuantityInput"].getText())
        except ValueError:
            ErrorMessagePopup(errorMessage="Quantity must be a number").open()
            return
        if newSnackQuantity == 0:
            ErrorMessagePopup(errorMessage="Quantity cannot be 0").open()
            return
        if newSnackQuantity < 0:
            ErrorMessagePopup(errorMessage="Quantity cannot be negative").open()
            return

        try:
            newSnackPrice = float(self.ids["snackPriceInput"].getText())
        except ValueError:
            ErrorMessagePopup(errorMessage="Price must be a number").open()
            return
        if newSnackPrice < 0:
            ErrorMessagePopup(errorMessage="Price cannot be negative").open()
            return

        if newSnackQuantity < self.snack_to_edit.quantity:
            popup = RemovalReasonPopup()

            def on_reason_selected(_, reason: LostSnackReason):
                quantity_removed = self.snack_to_edit.quantity - newSnackQuantity
                value_lost = self.snack_to_edit.pricePerItem * quantity_removed
                self.manager.database.add_lost_snack(
                    snack_name=newSnackName,
                    quantity=quantity_removed,
                    reason=reason,
                    total_value=value_lost,
                )
                self.finishEditingSnack(newSnackName, newSnackQuantity, newSnackPrice)

            popup.bind(on_selection=on_reason_selected)
            popup.open()
        elif newSnackQuantity > self.snack_to_edit.quantity:

            added_snack_popup = AddedSnackPricePopup()

            def on_price_confirmed(_, total_added_value: float):
                quantity_added = newSnackQuantity - self.snack_to_edit.quantity
                self.manager.database.add_added_snack(
                    snack_name=newSnackName,
                    quantity=quantity_added,
                    value=total_added_value,
                )
                self.finishEditingSnack(newSnackName, newSnackQuantity, newSnackPrice)

            added_snack_popup.bind(on_selection=on_price_confirmed)
            added_snack_popup.open()
        else:
            self.finishEditingSnack(newSnackName, newSnackQuantity, newSnackPrice)

    def finishEditingSnack(
        self, newSnackName: str, newSnackQuantity: int, newSnackPrice: float
    ):
        newSnackData = SnackData(
            snackId=self.snack_to_edit.snackId,
            snackName=newSnackName,
            quantity=newSnackQuantity,
            imageID="None",
            pricePerItem=newSnackPrice,
        )
        self.manager.database.updateSnackData(
            snackId=self.snack_to_edit.snackId, newSnackData=newSnackData
        )
        self.manager.transitionToScreen("editSnacksScreen", transitionDirection="right")

    def onCancel(self):
        self.manager.transitionToScreen("editSnacksScreen", transitionDirection="right")

    def onRemove(self):
        def on_removed_callback(*args):
            removalReasonPopup = RemovalReasonPopup()

            def on_reason_selected(_, reason: LostSnackReason):
                quantity_removed = self.snack_to_edit.quantity
                value_lost = self.snack_to_edit.pricePerItem * quantity_removed
                self.manager.database.add_lost_snack(
                    snack_name=self.snack_to_edit.snackName,
                    quantity=quantity_removed,
                    reason=reason,
                    total_value=value_lost,
                )
                self.manager.database.removeSnack(self.snack_to_edit.snackId)
                self.manager.transitionToScreen(
                    "editSnacksScreen", transitionDirection="right"
                )

            removalReasonPopup.bind(on_selection=on_reason_selected)
            removalReasonPopup.open()

        RemovalConfirmationPopup = RemoveConfirmationPopup(
            question_text=f"Are you sure you want to remove {self.snack_to_edit.snackName}?",
        )
        RemovalConfirmationPopup.bind(on_removed=on_removed_callback)
        RemovalConfirmationPopup.open()
