from database import SnackData, removeSnack, updateSnackData
from kivy.properties import ObjectProperty
from widgets.GridLayoutScreen import GridLayoutScreen
from widgets.popups.errorMessagePopup import ErrorMessagePopup
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

        newSnackData = SnackData(
            snackId=self.snack_to_edit.snackId,
            snackName=newSnackName,
            quantity=newSnackQuantity,
            imageID="None",
            pricePerItem=newSnackPrice,
        )
        updateSnackData(snackId=self.snack_to_edit.snackId, newSnackData=newSnackData)
        self.manager.transitionToScreen("editSnacksScreen", transitionDirection="right")

    def onCancel(self):
        self.manager.transitionToScreen("editSnacksScreen", transitionDirection="right")

    def onRemove(self):
        def on_removed_callback(*args):
            removeSnack(self.snack_to_edit.snackId)
            self.manager.transitionToScreen(
                "editSnacksScreen", transitionDirection="right"
            )

        popup = RemoveConfirmationPopup(
            question_text=f"Are you sure you want to remove {self.snack_to_edit.snackName}?",
        )
        popup.bind(on_removed=on_removed_callback)
        popup.open()
