import math
import random

from database import getAllSnacks
from kivy.animation import Animation
from kivy.clock import Clock
from kivy.core.text import Label as CoreLabel
from kivy.graphics import Color, Ellipse, Rectangle, Rotate, SmoothLine
from kivy.graphics.instructions import InstructionGroup
from kivy.properties import NumericProperty
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.widget import Widget
from widgets.customScreenManager import CustomScreenManager
from widgets.headerBodyLayout import HeaderBodyScreen


class WheelPointer(Widget):
    angle = NumericProperty(0)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class WheelWidget(Widget):
    angle = NumericProperty(0)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.snacks = getAllSnacks()

    def create_slice(self, slice_width, snack_name, slice_color):
        """Create a slice of the wheel for the given angle and snack."""

        lineWidth = self.width / 100

        instructionGroup = InstructionGroup()

        # Create slice background
        instructionGroup.add(slice_color)
        instructionGroup.add(
            Ellipse(
                angle_start=270 + slice_width / 2,
                angle_end=270 - slice_width / 2,
                pos=(
                    self.center_x - self.width / 2,
                    self.center_y - self.height / 2,
                ),
                size=self.size,
            )
        )

        # Border color
        instructionGroup.add(Color(1, 1, 1, 1))

        # Create rounded outer border
        instructionGroup.add(
            SmoothLine(
                circle=(
                    self.center_x,
                    self.center_y,
                    self.width / 2,
                    270 + slice_width / 2,
                    270 - slice_width / 2,
                ),
                width=lineWidth,
            )
        )

        # Create upper corner to center line
        corner1 = (
            self.center_x
            + math.cos(math.radians(180 + slice_width / 2)) * self.width / 2,
            self.center_y
            + math.sin(math.radians(180 + slice_width / 2)) * self.width / 2,
        )
        instructionGroup.add(
            SmoothLine(
                points=(self.center_x, self.center_y, corner1[0], corner1[1]),
                width=lineWidth,
            )
        )

        # Create lower corner to center line
        corner2 = (
            self.center_x
            + math.cos(math.radians(180 - slice_width / 2)) * self.width / 2,
            self.center_y
            + math.sin(math.radians(180 - slice_width / 2)) * self.width / 2,
        )
        instructionGroup.add(
            SmoothLine(
                points=(self.center_x, self.center_y, corner2[0], corner2[1]),
                width=lineWidth,
            )
        )

        # Add text to slice
        mylabel = CoreLabel(
            text=snack_name, font_size=self.height / 14, color=(0, 0, 0, 1), bold=True
        )
        mylabel.refresh()
        labelTexture = mylabel.texture
        instructionGroup.add(
            Rectangle(
                texture=labelTexture,
                size=list(labelTexture.size),
                pos=(
                    self.center_x - (self.width / 2.1),
                    self.center_y - labelTexture.height / 2,
                ),
            )
        )

        return instructionGroup

    def create_wheel(self, _):
        self.canvas.clear()
        slice_width = 360 / len(self.snacks)

        availableColors = []

        if len(self.snacks) % 2 == 0:
            availableColors = [
                Color(8 / 255, 127 / 255, 140 / 255, 1),
                Color(255 / 255, 169 / 255, 194 / 255, 1),
            ]
        else:
            availableColors = [
                Color(8 / 255, 127 / 255, 140 / 255, 1),
                Color(255 / 255, 169 / 255, 194 / 255, 1),
                Color(165 / 255, 231 / 255, 234 / 255, 1),
            ]

        # Create rotation before slices to rotate them all later
        total_wheel_rotation = Rotate(
            angle=0,
            axis=(0, 0, 1),
            origin=(self.center_x, self.center_y),
        )
        self.canvas.add(total_wheel_rotation)

        # Add slices to wheel
        for snack in self.snacks:
            color = availableColors[len(self.snacks) % (self.snacks.index(snack) + 1)]
            wheel_slice = self.create_slice(
                slice_width=slice_width,
                snack_name=snack.snackName,
                slice_color=color,
            )
            self.canvas.add(wheel_slice)
            self.canvas.add(
                Rotate(
                    angle=slice_width,
                    axis=(0, 0, 1),
                    origin=(self.center_x, self.center_y),
                )
            )

        # Perform last rotation to line up snacks with their angles gotten from get_snack_from_angle
        total_wheel_rotation.angle = 180 + (slice_width / 2)


class WheelOfSnacksWidget(AnchorLayout):
    wheel_angle = NumericProperty(0)
    pointer_angle = NumericProperty(0)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.snacks = getAllSnacks()
        self.pointer_angle = 180
        self.sliceWidth = 360 / len(self.snacks)
        self.border_angles = [
            self.sliceWidth * self.snacks.index(snack) for snack in self.snacks
        ]

    def on_size(self, _, new_size):
        Clock.schedule_once(self.ids.wheel.create_wheel, 0)

    def map_from_to(self, x, a, b, c, d):
        y = (x - a) / (b - a) * (d - c) + c
        return y

    def on_wheel_angle(self, _, angle):
        self.ids.wheel.angle = angle
        if (
            (self.ids.wheel.angle + (self.sliceWidth / 2)) % self.sliceWidth
        ) > self.sliceWidth - (self.width / 100):
            progress = self.map_from_to(
                (self.ids.wheel.angle + (self.sliceWidth / 2)) % self.sliceWidth,
                self.sliceWidth - (self.width / 100),
                self.sliceWidth,
                0,
                1,
            )
            self.ids.pointer.angle = -(progress * 20)
        else:
            self.ids.pointer.angle = 0

    def get_current_wheel_angle_bounded(self):
        return self.wheel_angle % 360

    def get_current_snack_at_angle(self, read_angle):
        current_angle_bounded = self.get_current_wheel_angle_bounded()
        current_read_angle = -(-read_angle + current_angle_bounded) % 360
        for snack in self.snacks:
            startAngle = self.sliceWidth * self.snacks.index(snack)
            endAngle = startAngle + self.sliceWidth
            if startAngle <= current_read_angle <= endAngle:
                return snack
        print("Snack not found!")
        return None

    def predict_snack_at_angle(self, read_angle, total_rotation):
        future_read_angle = -(-read_angle + total_rotation) % 360
        for snack in self.snacks:
            startAngle = self.sliceWidth * self.snacks.index(snack)
            endAngle = startAngle + self.sliceWidth
            if startAngle <= future_read_angle <= endAngle:
                return snack
        print("Snack not found!")
        return None

    def get_random_new_angle(self, exciting=False):
        new_angle = 0

        if exciting:
            # Current rotation
            angle_current = self.wheel_angle

            # Angle to a randoms snacks border
            angle_to_random_border = (
                random.choice(self.border_angles)
                + self.pointer_angle
                - self.wheel_angle % self.sliceWidth
            )

            # Margin for how far into the random snack we should spin
            angle_margin = random.uniform(0, self.sliceWidth / 10)

            new_angle = (
                angle_current
                + 360 * 8  # Eight rotations for excitement
                + angle_to_random_border
                + angle_margin
            )
        else:
            current_angle = self.wheel_angle
            new_angle = current_angle + random.uniform(360 * 8, 360 * 9)

        return new_angle

    def spin(self):
        current_snack = self.get_current_snack_at_angle(read_angle=self.pointer_angle)
        print(f"Current snack at {self.pointer_angle}: {current_snack.snackName}")

        new_angle = self.get_random_new_angle(exciting=True)

        print(f"Spinning to angle {new_angle}")

        predicted_snack = self.predict_snack_at_angle(
            read_angle=self.pointer_angle, total_rotation=new_angle
        )
        print(f"Predicted snack at {self.pointer_angle}: {predicted_snack.snackName}")
        anim = Animation(wheel_angle=new_angle, duration=8, t="out_quint")
        anim.start(self)


class WheelOfSnacksContent(GridLayout):
    def __init__(self, screenManager: CustomScreenManager, **kwargs):
        super().__init__(**kwargs)
        self.screenManager = screenManager
        snacks = getAllSnacks()
        # Order snacks by pricePerItem
        snacks = sorted(snacks, key=lambda x: x.pricePerItem, reverse=True)
        for snack in snacks:
            print(f"snack: {snack.snackName}, price: {snack.pricePerItem}")

        average_cost = sum(s.pricePerItem for s in snacks) / len(snacks)
        self.ids.cost_label.text = f"One spin costs: {average_cost:.2f} Credits"

    def onSpinButtonPressed(self, *largs):
        self.ids.wheel_widget.spin()


class WheelOfSnacksScreen(HeaderBodyScreen):
    def __init__(self, **kwargs):
        super().__init__(previousScreen="mainUserPage", **kwargs)
        self.headerSuffix = "Wheel of Snacks"

    def on_pre_enter(self, *args):
        super().on_pre_enter(*args)
        self.body.add_widget(WheelOfSnacksContent(screenManager=self.manager))
