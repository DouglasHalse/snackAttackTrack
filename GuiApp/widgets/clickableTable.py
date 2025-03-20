from time import time

from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.label import Label
from kivy.clock import Clock
from kivy.animation import AnimationTransition
from kivy.uix.recycleview.views import RecycleDataViewBehavior

import kivy.core.text


def get_str_pixel_width(string: str, **kwargs) -> int:
    return kivy.core.text.Label(**kwargs).get_extents(string)[0]


class BoxLayoutButton(ButtonBehavior, BoxLayout):
    pass


class ClickableTableColumnLabel(Label):
    def __init__(self, columnName: str, **kwargs):
        super().__init__(**kwargs)
        self.text = columnName


class ClickableTableColumnEntryLabel(GridLayout):
    def __init__(self, text: str, **kwargs):
        super().__init__(**kwargs)
        self.ids["entryLabel"].text = text
        self.widthOverhang = 0.0
        self.startPosition = 0.0
        self.animationStartDelay = 1.0
        self.animationTime = 2.0
        self.postAnimationTime = 1.0
        self.timeOfStart = time() + self.animationStartDelay

        # Need to run this once to get the initial width of the label
        Clock.schedule_once(self.initLabelWidth, 0)

    def initLabelWidth(self, dt):
        entryLabelWidth = self.ids["entryLabel"].texture_size[0]
        # if text label is wider than the entrylabel, then we need to animate the text
        if entryLabelWidth > self.width:
            self.widthOverhang = entryLabelWidth - self.width
            self.ids["entryLabel"].x += self.widthOverhang / 2.0
            self.startPosition = self.ids["entryLabel"].x
            Clock.schedule_interval(self.updateText, 0.01666)

    def updateText(self, dt):
        timeUsed = time() - self.timeOfStart

        if timeUsed < 0:
            return

        if timeUsed < self.animationTime:
            animationTimeProgress = timeUsed / self.animationTime
            animationState = AnimationTransition.linear(animationTimeProgress)
            self.ids["entryLabel"].x = (
                self.startPosition - self.widthOverhang * animationState
            )
        else:
            Clock.unschedule(self.updateText)
            Clock.schedule_once(self.resetAndStartAnimation, self.postAnimationTime)

    def resetAndStartAnimation(self, dt):
        self.ids["entryLabel"].x = self.startPosition
        self.timeOfStart = time() + self.animationStartDelay
        Clock.schedule_interval(self.updateText, 0.01666)


class ClickableTableEntry(RecycleDataViewBehavior, BoxLayoutButton):
    clickableTable = None
    entryContents = None
    columnProportions = None
    entryIdentifier = None
    index = None

    def refresh_view_attrs(self, rv, index, data):
        self.clickableTable = data["clickableTable"]
        self.entryContents = data["entryContents"]
        self.columnProportions = data["columnProportions"]
        self.entryIdentifier = data["entryIdentifier"]
        self.index = index

        # If the entry has children, then we can reuse them
        if len(self.children) == len(self.entryContents):
            reversedContents = list(reversed(self.entryContents))
            reversedColumnProportions = list(reversed(self.columnProportions))
            for child, columnText, columnProportion in zip(
                self.children, reversedContents, reversedColumnProportions
            ):
                child.ids["entryLabel"].text = columnText
                child.size_hint_x = columnProportion
        else:
            self.clear_widgets()
            for columnText, columnProportion in zip(
                self.entryContents, self.columnProportions
            ):
                self.add_widget(
                    ClickableTableColumnEntryLabel(
                        text=columnText,
                        size_hint_x=columnProportion,
                    )
                )
        super().refresh_view_attrs(rv, index, data)

    def onPress(self, *largs):
        """
        Call the onEntryPressed function of the clickableTable with the entryIdentifier of the pressed entry on the table
        """
        self.clickableTable.onEntryPressed(entryIdentifier=self.entryIdentifier)


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
        self,
        columns: list[str],
        columnExamples: list[str] = None,
        onEntryPressedCallback: callable = None,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.columns = columns
        self.columnProportions = []

        if columnExamples:
            assert len(columns) == len(columnExamples)
            columnExampleWidths = []
            for columnExample, columnName in zip(columnExamples, columns):
                widestContent = max(
                    get_str_pixel_width(columnExample), get_str_pixel_width(columnName)
                )
                columnExampleWidths.append(widestContent)

            columnWidthSum = sum(columnExampleWidths)
            self.columnProportions = [i / columnWidthSum for i in columnExampleWidths]

        else:
            self.columnProportions = [1 / len(columns) for _ in range(len(columns))]

        self.onEntryPressedCallback = onEntryPressedCallback
        for columnName, columnProportion in zip(columns, self.columnProportions):
            self.ids["tableHeader"].add_widget(
                ClickableTableColumnLabel(
                    columnName=columnName, size_hint_x=columnProportion
                )
            )

    def addEntry(self, entryContents: list[str], entryIdentifier):
        """
        Add an entry to the table

        entryContents: list[str]
            The contents of the row
        entryIdentifier: any
            The identifier of the row that will be passed to the onEntryPressedCallback when the entry is pressed
        """
        self.ids["rw"].data.append(
            {
                "clickableTable": self,
                "entryContents": entryContents,
                "columnProportions": self.columnProportions,
                "entryIdentifier": entryIdentifier,
            }
        )

    def hasEntry(self, entryIdentifier):
        """
        Check if an entry with the given entryIdentifier exists in the table

        entryIdentifier: any
            The identifier of the entry to check
        """

        for entry in self.ids["rw"].data:
            if entry["entryIdentifier"] == entryIdentifier:
                return True
        return False

    def removeEntry(self, entryIdentifier):
        """
        Remove an entry from the table

        entryIdentifier: any
            The identifier of the entry to remove
        """
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
        self.ids["rw"].data = []

    def onEntryPressed(self, entryIdentifier):
        """
        Call the onEntryPressedCallback with the entryIdentifier of the pressed entry
        if the onEntryPressedCallback is not provided, print a default message
        """
        if self.onEntryPressedCallback:
            self.onEntryPressedCallback(entryIdentifier)
        else:
            print(f"Entry with id {entryIdentifier} pressed")
