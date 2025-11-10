from database import TransactionType
from widgets.GridLayoutScreen import GridLayoutScreen


class StoreStatisticsScreen(GridLayoutScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.ids.header.bind(on_back_button_pressed=self.onBackButtonPressed)

    def onBackButtonPressed(self, *largs):
        self.manager.transitionToScreen("adminScreen", transitionDirection="right")

    def on_pre_enter(self, *args):
        # Update the statistics displayed on the screen

        value_of_snacks_added = self.manager.database.get_value_of_added_snacks()

        self.ids.added_stats.stat_value_1 = (
            f"{self.manager.database.get_total_snacks_added()} Snacks"
        )
        self.ids.added_stats.stat_value_2 = f"{value_of_snacks_added:.2f} Credits"

        snacks_in_inventory = self.manager.database.getAllSnacks()
        number_of_snacks_in_inventory = sum(
            snack.quantity for snack in snacks_in_inventory
        )
        value_of_snacks_in_inventory = sum(
            snack.pricePerItem * snack.quantity for snack in snacks_in_inventory
        )

        self.ids.inventory_stats.stat_value_1 = (
            f"{number_of_snacks_in_inventory} Snacks"
        )
        self.ids.inventory_stats.stat_value_2 = (
            f"{value_of_snacks_in_inventory:.2f} Credits"
        )

        number_of_sold_snacks = 0
        store_revenue = 0.0
        gambling_revenue = 0.0
        gambling_returns = 0.0
        users = self.manager.database.getAllPatrons()
        for user in users:
            transactions = self.manager.database.getTransactions(user.patronId)
            for transaction in transactions:
                if transaction.transactionType == TransactionType.PURCHASE:
                    for transactionItem in transaction.transactionItems:
                        number_of_sold_snacks += transactionItem.quantity
                    store_revenue += (
                        transaction.amountBeforeTransaction
                        - transaction.amountAfterTransaction
                    )
                elif transaction.transactionType == TransactionType.GAMBLE:
                    for transactionItem in transaction.transactionItems:
                        gambling_returns += transactionItem.pricePerItem
                    gambling_revenue += (
                        transaction.amountBeforeTransaction
                        - transaction.amountAfterTransaction
                    )

        self.ids.sold_stats.stat_value_1 = f"{number_of_sold_snacks} Snacks"
        self.ids.sold_stats.stat_value_2 = f"{store_revenue:.2f} Credits"

        self.ids.lost_stats.stat_value_1 = (
            f"{self.manager.database.get_total_snacks_lost()} Snacks"
        )
        self.ids.lost_stats.stat_value_2 = (
            f"{self.manager.database.get_value_of_lost_snacks():.2f} Credits"
        )

        self.ids.gambling_stats.stat_value_1 = f"{gambling_revenue:.2f} Credits"
        self.ids.gambling_stats.stat_value_2 = f"{gambling_returns:.2f} Credits"

        self.ids.profit_stat.stat_value = (
            f"{(store_revenue + gambling_revenue)-value_of_snacks_added:.2f} Credits"
        )

        return super().on_pre_enter(*args)
