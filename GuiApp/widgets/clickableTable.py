from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.label import Label


class BoxLayoutButton(ButtonBehavior, BoxLayout):
    pass


class ClickableTableColumnLabel(Label):
    def __init__(self, columnName: str, **kwargs):
        super().__init__(**kwargs)
        self.text = columnName


class ClickableTableColumnEntryLabel(Label):
    def __init__(self, text: str, **kwargs):
        super().__init__(**kwargs)
        self.text = text


class ClickableTableEntry(BoxLayoutButton):
    def __init__(
        self,
        clickableTable,
        entryContents: list[str],
        entryIdentifier,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.entryIdentifier = entryIdentifier
        self.clickableTable = clickableTable
        for columnValue in entryContents:
            self.add_widget(
                ClickableTableColumnEntryLabel(text=columnValue, markup=True)
            )

    def onPress(self, *largs):
        """
        Call the onEntryPressed function of the clickableTable with the entryIdentifier of the pressed entry on the table
        """
        self.clickableTable.onEntryPressed(entryIdentifier=self.entryIdentifier)


class ClickableTableCustomEntry(BoxLayoutButton):
    def __init__(
        self,
        entryContents: list[str],
        onPressCallback: callable = None,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.onPressCallback = onPressCallback
        for columnValue in entryContents:
            self.add_widget(
                ClickableTableColumnEntryLabel(text=columnValue, markup=True)
            )

    def onPress(self, *largs):
        """
        Call the onPressCallback when the custom entry is pressed
        if the onPressCallback is not provided, print a default message
        """
        if self.onPressCallback:
            self.onPressCallback()
        else:
            print("Custom entry pressed")


class ClickableTable(GridLayout):
    """
    A table that can have clickable entries

    onEntryPressedCallback is a callback function that will be called when an entry is pressed
    The callback function should take one argument, which is the entryIdentifier of the pressed entry
    that is assigned when the entry is added to the table using addEntry

    columns: list[str]
        The column names of the table
    onEntryPressedCallback: callable
        The callback function that will be called when an entry is pressed
    """

    def __init__(
        self, columns: list[str], onEntryPressedCallback: callable = None, **kwargs
    ):
        super().__init__(**kwargs)
        self.columns = columns
        self.onEntryPressedCallback = onEntryPressedCallback
        for column in columns:
            self.ids["tableHeader"].add_widget(
                ClickableTableColumnLabel(columnName=column)
            )

    def addEntry(self, entryContents: list[str], entryIdentifier):
        """
        Add an entry to the table

        entryContents: list[str]
            The contents of the row
        entryIdentifier: any
            The identifier of the row that will be passed to the onEntryPressedCallback when the entry is pressed
        """
        if len(entryContents) != len(self.columns):
            raise ValueError(
                f"Size of row contents {entryContents} does not match number of columns {self.columns}"
            )

        self.ids["tableContent"].add_widget(
            ClickableTableEntry(
                clickableTable=self,
                entryContents=entryContents,
                entryIdentifier=entryIdentifier,
            )
        )

    def addCustomEntry(
        self, entryContents: list[str], onPressCallback: callable = None
    ):
        """
        Add a custom entry to the table that does not ned one entry per column

        entryContents: list[str]
            The contents of the row
        onPressCallback: callable
            The callback function that will be called when the custom entry is
            pressed. If not provided, a default print statement will be used
        """
        self.ids["tableContent"].add_widget(
            ClickableTableCustomEntry(
                entryContents=entryContents, onPressCallback=onPressCallback
            )
        )

    def clearEntries(self):
        """
        Clear all entries from the table
        """
        self.ids["tableContent"].clear_widgets()

    def onEntryPressed(self, entryIdentifier):
        """
        Call the onEntryPressedCallback with the entryIdentifier of the pressed entry
        if the onEntryPressedCallback is not provided, print a default message
        """
        if self.onEntryPressedCallback:
            self.onEntryPressedCallback(entryIdentifier)
        else:
            print(f"Entry with id {entryIdentifier} pressed")
