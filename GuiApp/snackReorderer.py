from database import SnackData


class SnackReorderer:
    """
    A class to reorder snacks.
    """

    @staticmethod
    def reorder_snacks_based_on_guide_list(
        snacks_to_reorder: list[SnackData], snack_guide_list: list[str]
    ) -> None:
        """
        Reorder snacks based on a guide list.
        The snacks will be reordered based on the guide list, if a snack is not in the guide then those snacks will not be reordered
        and will be placed at the end of the list in the order they appear in the snacks_to_reorder list.
        If a snack is in the guide list but not in the snacks_to_reorder list, it will be ignored.

        snacks_to_reorder: list[SnackData]
            The snacks to reorder
        snack_guide_list: list[str]
            The guide list to reorder the snacks based on

        example:
            reorder_snacks_based_on_guide_list([snack1, snack2, snack3], ["snack3", "snack1", "snack2"])
            -> snack3, snack1, snack2

            reorder_snacks_based_on_guide_list([snack1, snack2, snack3], ["snack2", "snack3"])
            -> snack2, snack3, snack1
        """
        # Create a dictionary for quick lookup of snacks by name
        snack_dict = {snack.snackName: snack for snack in snacks_to_reorder}

        # Reorder snacks based on the guide list
        reordered_snacks = [
            snack_dict[name] for name in snack_guide_list if name in snack_dict
        ]

        # Add snacks that are not in the guide list to the end
        remaining_snacks = [
            snack
            for snack in snacks_to_reorder
            if snack.snackName not in snack_guide_list
        ]
        reordered_snacks.extend(remaining_snacks)

        # Update the original list in place
        snacks_to_reorder[:] = reordered_snacks
