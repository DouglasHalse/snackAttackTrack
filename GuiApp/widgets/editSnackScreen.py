from database import SnackData, removeSnack, updateSnackData
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.modalview import ModalView
from widgets.customScreenManager import CustomScreenManager
from widgets.headerBodyLayout import HeaderBodyScreen
from widgets.popups.errorMessagePopup import ErrorMessagePopup


class BoxLayoutButton(ButtonBehavior, BoxLayout):
    pass


class EditSnackScreenContent(GridLayout):
    def __init__(self, screenManager: CustomScreenManager, **kwargs):
        super().__init__(**kwargs)
        self.screenManager = screenManager
        self.snackToEdit: SnackData = self.screenManager.getSnackToEdit()
        self.ids["snackNameInput"].setText(self.snackToEdit.snackName)
        self.ids["snackQuantityInput"].setText(str(self.snackToEdit.quantity))
        self.ids["snackPriceInput"].setText(f"{self.snackToEdit.pricePerItem:.2f}")

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
            snackId=self.snackToEdit.snackId,
            snackName=newSnackName,
            quantity=newSnackQuantity,
            imageID="None",
            pricePerItem=newSnackPrice,
        )
        updateSnackData(snackId=self.snackToEdit.snackId, newSnackData=newSnackData)
        self.screenManager.transitionToScreen(
            "editSnacksScreen", transitionDirection="right"
        )

    def onCancel(self):
        self.screenManager.transitionToScreen(
            "editSnacksScreen", transitionDirection="right"
        )

    def onRemove(self):
        popup = RemoveSnackConfirmationPopup(
            screenManager=self.screenManager, snackToRemove=self.snackToEdit
        )
        popup.open()


class EditSnackScreen(HeaderBodyScreen):
    def __init__(self, **kwargs):
        super().__init__(previousScreen="editSnacksScreen", **kwargs)
        self.headerSuffix = "Edit Snack screen"

    def on_pre_enter(self, *args):
        super().on_pre_enter(*args)
        self.body.add_widget(EditSnackScreenContent(screenManager=self.manager))

    def on_leave(self, *args):
        super().on_leave(*args)
        self.manager.resetSnackToEdit()


class RemoveSnackConfirmationPopup(ModalView):
    def __init__(
        self, screenManager: CustomScreenManager, snackToRemove: SnackData, **kwargs
    ):
        super().__init__(**kwargs)
        self.screenManager = screenManager
        self.snackToRemove = snackToRemove
        self.ids[
            "areYouSureLabel"
        ].text = f"Are you sure you want to \nremove {self.snackToRemove.snackName}?"

    def onCancel(self):
        self.dismiss()

    def onRemove(self):
        removeSnack(self.snackToRemove.snackId)
        self.dismiss()
        self.screenManager.transitionToScreen(
            "editSnacksScreen", transitionDirection="right"
        )
