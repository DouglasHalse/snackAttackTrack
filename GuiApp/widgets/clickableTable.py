from time import time

from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.label import Label
from kivy.clock import Clock
from kivy.animation import AnimationTransition

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


class ClickableTableEntry(BoxLayoutButton):
    def __init__(
        self,
        clickableTable,
        entryContents: list[str],
        columnProportions: list[float],
        entryIdentifier,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.entryIdentifier = entryIdentifier
        self.clickableTable = clickableTable
        self.columnProportions = columnProportions
        for columnText, columnProportion in zip(entryContents, columnProportions):
            self.add_widget(
                ClickableTableColumnEntryLabel(
                    text=columnText,
                    size_hint_x=columnProportion,
                )
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
            self.add_widget(ClickableTableColumnEntryLabel(text=columnValue))

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
        if len(entryContents) != len(self.columns):
            raise ValueError(
                f"Size of row contents {entryContents} does not match number of columns {self.columns}"
            )

        self.ids["tableContent"].add_widget(
            ClickableTableEntry(
                clickableTable=self,
                entryContents=entryContents,
                columnProportions=self.columnProportions,
                entryIdentifier=entryIdentifier,
            )
        )

    def hasEntry(self, entryIdentifier):
        """
        Check if an entry with the given entryIdentifier exists in the table

        entryIdentifier: any
            The identifier of the entry to check
        """
        for entry in self.ids["tableContent"].children:
            if entry.entryIdentifier == entryIdentifier:
                return True
        return False

    def removeEntry(self, entryIdentifier):
        """
        Remove an entry from the table

        entryIdentifier: any
            The identifier of the entry to remove
        """
        for entry in self.ids["tableContent"].children:
            if entry.entryIdentifier == entryIdentifier:
                self.ids["tableContent"].remove_widget(entry)
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
        for entry in self.ids["tableContent"].children:
            if entry.entryIdentifier == entryIdentifier:
                for columnLabel, newColumnContent in zip(
                    entry.children, reversed(newEntryContents)
                ):
                    columnLabel.ids["entryLabel"].text = newColumnContent
                return
        raise ValueError(f"Entry with identifier {entryIdentifier} not found")

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
