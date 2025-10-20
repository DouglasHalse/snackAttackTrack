from database import TransactionType, getMostPurchasedSnacksByPatron, getTransactions
from kivy.app import App
from widgets.GridLayoutScreen import GridLayoutScreen


class UserStatisticsScreen(GridLayoutScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.ids.header.bind(on_back_button_pressed=self.onBackButtonPressed)

    def on_kv_post(self, _):
        app = App.get_running_app()
        app.screenManager.bind(
            logged_in_user=lambda instance, value: self.updateStatistics(value)
        )

    def onBackButtonPressed(self, *largs):
        self.manager.transitionToScreen("profileScreen", transitionDirection="right")

    def updateStatistics(self, logged_in_user):
        # Update the statistics displayed on the screen

        if logged_in_user is None:
            return

        transactions = getTransactions(logged_in_user.patronId)

        total_credits_spent = 0.0
        total_snacks_purchased = 0
        total_snacks_won = 0
        favorite_snack = "N/A"
        for transaction in transactions:
            if transaction.transactionType == TransactionType.PURCHASE:
                total_credits_spent += (
                    transaction.amountBeforeTransaction
                    - transaction.amountAfterTransaction
                )
                total_snacks_purchased += len(transaction.transactionItems)
            if transaction.transactionType == TransactionType.GAMBLE:
                total_snacks_won += 1

        most_purchased_snacks = getMostPurchasedSnacksByPatron(logged_in_user.patronId)
        if most_purchased_snacks:
            favorite_snack = most_purchased_snacks[0]

        self.ids.total_credits_spent.stat_value = f"{total_credits_spent:.2f}"
        self.ids.favorite_snack.stat_value = favorite_snack
        self.ids.total_snacks_purchased.stat_value = f"{total_snacks_purchased}"
        self.ids.total_snacks_won.stat_value = f"{total_snacks_won}"
