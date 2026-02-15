import kivy.core.text
from kivy.clock import Clock
from kivy.properties import BooleanProperty
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.recycleview.views import RecycleDataViewBehavior
from widgets.uiElements.labels import AutoScrollingLabel


def get_str_pixel_width(string: str, **kwargs) -> int:
    return kivy.core.text.Label(**kwargs).get_extents(string)[0]


class BoxLayoutButton(ButtonBehavior, BoxLayout):
    pass


class ClickableTableColumnLabel(Label):
    def __init__(self, columnName: str, **kwargs):
        super().__init__(**kwargs)
        self.text = columnName


class ClickableTableEntry(RecycleDataViewBehavior, BoxLayoutButton):
    clickableTable = None
    entryContents = None
    columnProportions = None
    entryIdentifier = None
    selected = BooleanProperty(True)
    index = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.opacity = 1

    def refresh_view_attrs(self, rv, index, data):
        self.clickableTable = data["clickableTable"]
        self.entryContents = data["entryContents"]
        self.columnProportions = data["columnProportions"]
        self.entryIdentifier = data["entryIdentifier"]
        self.selected = data["selected"]
        self.index = index

        # If the entry has children, then we can reuse them
        if len(self.children) == len(self.entryContents):
            reversedContents = list(reversed(self.entryContents))
            reversedColumnProportions = list(reversed(self.columnProportions))
            for child, columnText, columnProportion in zip(
                self.children, reversedContents, reversedColumnProportions
            ):
                child.text = columnText
                child.size_hint_x = columnProportion
                # Schedule the label width initialization to run in the next frame
                Clock.schedule_once(child.initLabelWidth, 0)
        else:
            self.clear_widgets()
            for columnText, columnProportion in zip(
                self.entryContents, self.columnProportions
            ):
                self.add_widget(
                    AutoScrollingLabel(
                        text=columnText,
                        size_hint_x=columnProportion,
                    )
                )
        super().refresh_view_attrs(rv, index, data)

    def onPress(self, *largs):
        """
        Call the onEntryPressed function of the clickableTable with the entryIdentifier of the pressed entry on the table
        """
        self.clickableTable.onEntryPressed(self.entryIdentifier)

    def on_selected(self, instance, value):
        self.opacity = 1 if value else 0.5


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

    columns = None
    columnExamples = None

    def __init__(
        self,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.columnProportions = []
        self.is_kv_posted = False
        self.entries_to_add_after_kv_post = []

    def _setup_columns(self):
        if self.columnExamples:
            assert len(self.columns) == len(self.columnExamples)
            columnExampleWidths = []
            for columnExample, columnName in zip(self.columnExamples, self.columns):
                widestContent = max(
                    get_str_pixel_width(columnExample), get_str_pixel_width(columnName)
                )
                columnExampleWidths.append(widestContent)

            columnWidthSum = sum(columnExampleWidths)
            self.columnProportions = [i / columnWidthSum for i in columnExampleWidths]

        else:
            self.columnProportions = [
                1 / len(self.columns) for _ in range(len(self.columns))
            ]

        for columnName, columnProportion in zip(self.columns, self.columnProportions):
            self.ids["tableHeader"].add_widget(
                ClickableTableColumnLabel(
                    columnName=columnName, size_hint_x=columnProportion
                )
            )

    def on_kv_post(self, base_widget):
        self.is_kv_posted = True

        self._setup_columns()

        for entryContents, entryIdentifier in self.entries_to_add_after_kv_post:
            self.addEntry(entryContents, entryIdentifier)
        self.entries_to_add_after_kv_post = []
        return super().on_kv_post(base_widget)

    def addEntry(self, entryContents: list[str], entryIdentifier):
        """
        Add an entry to the table

        entryContents: list[str]
            The contents of the row
        entryIdentifier: any
            The identifier of the row that will be passed to the onEntryPressedCallback when the entry is pressed

        This function schedules the addition of the entry to the table data
        to ensure that it is added after the table has been initialized
        """
        if not self.is_kv_posted:
            self.entries_to_add_after_kv_post.append((entryContents, entryIdentifier))
            return

        self.ids["rw"].data.append(
            {
                "clickableTable": self,
                "entryContents": entryContents,
                "columnProportions": self.columnProportions,
                "entryIdentifier": entryIdentifier,
                "selected": True,
            }
        )

    def hasEntry(self, entryIdentifier):
        """
        Check if an entry with the given entryIdentifier exists in the table

        entryIdentifier: any
            The identifier of the entry to check
        """

        if not self.is_kv_posted:
            return any(
                entryIdentifier == eid for _, eid in self.entries_to_add_after_kv_post
            )

        for entry in self.ids["rw"].data:
            if entry["entryIdentifier"] == entryIdentifier:
                return True
        return False

    def getEntries(self):
        """
        Get a list of all entries in the table

        Returns: list[entryIdentifier]
            A list of all entryIdentifiers of the entries in the table
        """
        if not self.is_kv_posted:
            return [eid for _, eid in self.entries_to_add_after_kv_post]

        return [entry["entryIdentifier"] for entry in self.ids["rw"].data]

    def toggleSelected(self, entryIdentifier, selected=None):
        """
        Toggle the selected state of an entry in the table

        entryIdentifier: any
            The identifier of the entry to toggle
        selected: bool or None
            The new selected state of the entry. If None, the selected state will be toggled
        """
        if not self.is_kv_posted:
            for i, (entryContents, eid) in enumerate(self.entries_to_add_after_kv_post):
                if eid == entryIdentifier:
                    currentSelected = (
                        self.entries_to_add_after_kv_post[i][2]
                        if len(self.entries_to_add_after_kv_post[i]) > 2
                        else False
                    )
                    newSelected = not currentSelected if selected is None else selected
                    self.entries_to_add_after_kv_post[i] = (
                        entryContents,
                        eid,
                        newSelected,
                    )
                    return
            raise ValueError(f"Entry with identifier {entryIdentifier} not found")

        for entry in self.ids["rw"].data:
            if entry["entryIdentifier"] == entryIdentifier:
                currentSelected = entry.get("selected", False)
                entry["selected"] = (
                    not currentSelected if selected is None else selected
                )
                self.ids["rw"].refresh_from_data()
                return
        raise ValueError(f"Entry with identifier {entryIdentifier} not found")

    def getSelectedEntries(self):
        """
        Get a list of all selected entries in the table

        Returns: list[entryIdentifier]
            A list of all entryIdentifiers of the selected entries in the table
        """
        if not self.is_kv_posted:
            return [
                eid
                for entryContents, eid, selected in self.entries_to_add_after_kv_post
                if selected
            ]

        return [
            entry["entryIdentifier"]
            for entry in self.ids["rw"].data
            if entry.get("selected", False)
        ]

    def getUnselectedEntries(self):
        """
        Get a list of all unselected entries in the table

        Returns: list[entryIdentifier]
            A list of all entryIdentifiers of the unselected entries in the table
        """
        if not self.is_kv_posted:
            return [
                eid
                for entryContents, eid, selected in self.entries_to_add_after_kv_post
                if not selected
            ]

        return [
            entry["entryIdentifier"]
            for entry in self.ids["rw"].data
            if not entry.get("selected", False)
        ]

    def removeEntry(self, entryIdentifier):
        """
        Remove an entry from the table

        entryIdentifier: any
            The identifier of the entry to remove
        """
        if not self.is_kv_posted:
            for i, (_, eid) in enumerate(self.entries_to_add_after_kv_post):
                if eid == entryIdentifier:
                    del self.entries_to_add_after_kv_post[i]
                    return
            raise ValueError(f"Entry with identifier {entryIdentifier} not found")

        for entry in self.ids["rw"].data:
            if entry["entryIdentifier"] == entryIdentifier:
                self.ids["rw"].data.remove(entry)
                return
        raise ValueError(f"Entry with identifier {entryIdentifier} not found")

    def updateEntry(self, entryIdentifier, newEntryContents: list[str]):
        """
        Update the contents of an entry in the table

        entryIdentifier: any
            The identifier of the entry to update
        newEntryContents: list[str]
            The new contents of the row
        """

        if not self.is_kv_posted:
            for i, (_, eid) in enumerate(self.entries_to_add_after_kv_post):
                if eid == entryIdentifier:
                    self.entries_to_add_after_kv_post[i] = (
                        newEntryContents,
                        entryIdentifier,
                    )
                    return
            raise ValueError(f"Entry with identifier {entryIdentifier} not found")

        for entry in self.ids["rw"].data:
            if entry["entryIdentifier"] == entryIdentifier:
                entry["entryContents"] = newEntryContents
                self.ids["rw"].refresh_from_data()
                return
        raise ValueError(f"Entry with identifier {entryIdentifier} not found")

    def clearEntries(self):
        """
        Clear all entries from the table
        """
        if not self.is_kv_posted:
            self.entries_to_add_after_kv_post = []
            return

        self.ids["rw"].data = []

        # Scroll back to the top when cleared
        self.ids["rw"].scroll_y = 1.0

    def onEntryPressed(self, *largs):
        """
        Call the onEntryPressedCallback with the entryIdentifier of the pressed entry
        if the onEntryPressedCallback is not provided, print a default message
        """
