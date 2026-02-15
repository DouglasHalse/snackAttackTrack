import math
import random

from database import SnackData
from kivy.animation import Animation
from kivy.clock import Clock
from kivy.core.text import Label as CoreLabel
from kivy.graphics import (
    Color,
    Ellipse,
    InstructionGroup,
    Rectangle,
    Rotate,
    SmoothLine,
)
from kivy.graphics.stencil_instructions import (
    StencilPop,
    StencilPush,
    StencilUnUse,
    StencilUse,
)
from kivy.properties import BooleanProperty, NumericProperty
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.widget import Widget


class WheelPointer(Widget):
    angle = NumericProperty(0)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class WheelWidget(Widget):
    angle = NumericProperty(0)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._label_textures = {}  # Cache for label textures
        self._saved_instruction_groups = {}

    def on_size(self, *args):
        self.clear_cache()

    def clear_cache(self):
        self._label_textures = {}
        self._saved_instruction_groups = {}

    def get_label_texture(self, snack_name, font_size):
        cache_key = (snack_name, font_size)
        if cache_key in self._label_textures:
            return self._label_textures[cache_key]
        mylabel = CoreLabel(
            text=snack_name,
            font_size=font_size,
            color=(0, 0, 0, 1),
            bold=True,
        )
        mylabel.refresh()
        self._label_textures[cache_key] = mylabel.texture
        return self._label_textures[cache_key]

    def get_slice_colors(self, num_slices):
        base_colors = [
            Color(8 / 255, 127 / 255, 140 / 255, 1),
            Color(255 / 255, 169 / 255, 194 / 255, 1),
            Color(165 / 255, 231 / 255, 234 / 255, 1),
            Color(255 / 255, 223 / 255, 128 / 255, 1),
            Color(128 / 255, 255 / 255, 170 / 255, 1),
            Color(255 / 255, 128 / 255, 128 / 255, 1),
            Color(128 / 255, 128 / 255, 255 / 255, 1),
        ]

        for color_count in range(2, min(num_slices, len(base_colors)) + 1):
            colors = base_colors[:color_count]
            result = []
            for i in range(num_slices):
                result.append(colors[i % color_count])
            # Check for adjacent duplicates, including wrap-around
            if all(
                result[i] != result[(i + 1) % num_slices] for i in range(num_slices)
            ):
                return result
        # Fallback: use as many colors as slices
        return [base_colors[i % len(base_colors)] for i in range(num_slices)]

    # pylint: disable=too-many-locals
    def create_wheel(self, snacks, label_pan_position_scale=0):
        self.canvas.clear()

        font_size = self.width / 14

        snack_names_hash = str([snack.snackName for snack in snacks])
        label_position_hash = 0.004 * round(label_pan_position_scale / 0.004)
        cache_key = (
            snack_names_hash,
            label_position_hash,
            font_size,
        )
        if cache_key in self._saved_instruction_groups:
            self.canvas.add(self._saved_instruction_groups[cache_key])
            return

        instruction_group = InstructionGroup()

        # Precompute positions and sizes
        cx, cy = self.center_x, self.center_y
        w, h = self.width, self.height
        half_w, half_h = w / 2, h / 2
        line_width = self.width / 100

        # Create simple empty circle if no snacks
        if len(snacks) < 2:
            instruction_group.add(Color(8 / 255, 127 / 255, 140 / 255, 1))
            instruction_group.add(
                Ellipse(
                    pos=(
                        self.center_x - self.width / 2,
                        self.center_y - self.height / 2,
                    ),
                    size=self.size,
                )
            )
            # Border color
            instruction_group.add(Color(1, 1, 1, 1))

            # Create rounded outer border
            instruction_group.add(
                SmoothLine(
                    circle=(
                        self.center_x,
                        self.center_y,
                        self.width / 2,
                        0,
                        360,
                    ),
                    width=line_width,
                )
            )

            # Rotate label based on current rotation
            instruction_group.add(
                Rotate(
                    angle=-(self.angle % 360),
                    axis=(0, 0, 1),
                    origin=(self.center_x, self.center_y),
                )
            )

            # No snacks selected text in the middle
            labelTexture = self.get_label_texture(
                "Select two snacks to spin", font_size
            )
            instruction_group.add(
                Rectangle(
                    texture=labelTexture,
                    size=list(labelTexture.size),
                    pos=(
                        self.center_x - labelTexture.width / 2,
                        self.center_y - labelTexture.height / 2,
                    ),
                )
            )

            # Restore rotation
            instruction_group.add(
                Rotate(
                    angle=(self.angle % 360),
                    axis=(0, 0, 1),
                    origin=(self.center_x, self.center_y),
                )
            )

            self._saved_instruction_groups[cache_key] = instruction_group
            self.canvas.add(instruction_group)
            return

        slice_width = 360 / len(snacks)

        availableColors = self.get_slice_colors(len(snacks))

        # Create rotation before slices to rotate them all later
        total_wheel_rotation = Rotate(
            angle=0,
            axis=(0, 0, 1),
            origin=(cx, cy),
        )
        instruction_group.add(total_wheel_rotation)

        # Add slices to wheel
        for i, snack in enumerate(snacks):
            color = availableColors[
                (i * len(availableColors)) // len(snacks) % len(availableColors)
            ]

            # Color for the slice
            instruction_group.add(color)
            instruction_group.add(
                Ellipse(
                    angle_start=270 + slice_width / 2,
                    angle_end=270 - slice_width / 2,
                    pos=(cx - half_w, cy - half_h),
                    size=self.size,
                )
            )

            labelTexture = self.get_label_texture(snack.snackName, font_size)

            instruction_group.add(StencilPush())

            # Create stencil for label
            instruction_group.add(
                Rectangle(
                    pos=(
                        self.center_x - (self.width / 2.1),
                        self.center_y - labelTexture.height / 2,
                    ),
                    size=[self.width / 2.5, labelTexture.height],
                )
            )

            instruction_group.add(StencilUse())

            # Add text to slice

            label_pos_x = self.center_x - (self.width / 2.1)

            if labelTexture.width > self.width / 2.5:
                label_overhang = labelTexture.width - (self.width / 2.5)
                label_pos_x -= (
                    label_overhang
                ) * label_pan_position_scale  # Adjust position based on pan scale

            instruction_group.add(
                Rectangle(
                    texture=labelTexture,
                    size=list(labelTexture.size),
                    pos=(
                        label_pos_x,
                        self.center_y - labelTexture.height / 2,
                    ),
                )
            )

            instruction_group.add(StencilUnUse())

            instruction_group.add(
                Rectangle(
                    pos=(
                        self.center_x - (self.width / 2.1),
                        self.center_y - labelTexture.height / 2,
                    ),
                    size=[self.width / 2.5, labelTexture.height],
                )
            )

            instruction_group.add(StencilPop())

            instruction_group.add(
                Rotate(
                    angle=slice_width,
                    axis=(0, 0, 1),
                    origin=(self.center_x, self.center_y),
                )
            )

        # Border color
        instruction_group.add(Color(1, 1, 1, 1))

        # Create rounded outer border
        instruction_group.add(
            SmoothLine(
                circle=(
                    self.center_x,
                    self.center_y,
                    self.width / 2,
                    0,
                    360,
                ),
                width=line_width,
            )
        )

        for border_angle in [
            (slice_width * snacks.index(snack)) - (180 + (slice_width / 2))
            for snack in snacks
        ]:
            instruction_group.add(
                SmoothLine(
                    points=(
                        self.center_x,
                        self.center_y,
                        self.center_x
                        + math.cos(math.radians(border_angle)) * self.width / 2,
                        self.center_y
                        + math.sin(math.radians(border_angle)) * self.width / 2,
                    ),
                    width=line_width,
                )
            )

        # Perform last rotation to line up snacks with their angles gotten from get_snack_from_angle
        total_wheel_rotation.angle = 180 + (slice_width / 2)

        self._saved_instruction_groups[cache_key] = instruction_group

        self.canvas.add(instruction_group)

    # pylint: enable=too-many-locals


class WheelOfSnacksWidget(AnchorLayout):
    wheel_angle = NumericProperty(0)
    pointer_angle = NumericProperty(0)
    label_pan_position_scale = NumericProperty(0)
    enable = BooleanProperty(False)
    label_pan_animation = None
    __events__ = ("on_spin_complete",)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.snacks = []
        self.sliceWidth = 0
        self.border_angles = []
        self.pointer_angle = 180
        self.label_pan_animation = (
            Animation(label_pan_position_scale=0, duration=1.0)
            + Animation(label_pan_position_scale=1, duration=2.0)
            + Animation(label_pan_position_scale=1, duration=1.0)
            + Animation(label_pan_position_scale=0, duration=0.0)
        )
        self.label_pan_animation.repeat = True
        self.bind(label_pan_position_scale=self.schedule_wheel_update)
        self.bind(size=self.schedule_wheel_update)

    def on_enable(self, _, enable):
        if enable:
            self.label_pan_animation.start(self)
            self.schedule_wheel_update(None, None)
        else:
            self.label_pan_animation.stop(self)
            self.label_pan_position_scale = 0

    def cleanup(self):
        Animation.cancel_all(self)
        Clock.unschedule(self.label_pan_animation)

    def schedule_wheel_update(self, _, __):
        if not self.enable:
            return
        Clock.schedule_once(
            lambda dt: self.ids.wheel.create_wheel(
                snacks=self.snacks,
                label_pan_position_scale=self.label_pan_position_scale,
            ),
            0,
        )

    def set_snacks(self, snacks):
        new_snack_names = [snack.snackName for snack in snacks]
        current_snack_names = [snack.snackName for snack in self.snacks]
        if current_snack_names != new_snack_names:
            self.ids.wheel.clear_cache()

        self.snacks = snacks
        self.sliceWidth = 360 / len(self.snacks) if self.snacks else 360
        self.border_angles = [
            self.sliceWidth * self.snacks.index(snack) for snack in self.snacks
        ]

        # Update the wheel with new snacks immediately
        self.schedule_wheel_update(None, None)

        # Update angle to ensure cursor tilts correctly with new slice width and border angles
        self.on_wheel_angle(None, self.wheel_angle)

    def map_from_to(self, x, a, b, c, d):
        y = (x - a) / (b - a) * (d - c) + c
        return y

    def on_wheel_angle(self, _, angle):
        self.ids.wheel.angle = angle

        angle_mod = (self.ids.wheel.angle + self.pointer_angle) % self.sliceWidth
        border_threshold = self.width / 100

        # Near the end of a slice
        if angle_mod > self.sliceWidth - border_threshold:
            progress = self.map_from_to(
                angle_mod,
                self.sliceWidth - border_threshold,
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

            # Margin for how far off the border we should land
            angle_margin = random.uniform(-self.sliceWidth / 10, self.sliceWidth / 10)

            new_angle = (
                angle_current
                + angle_to_random_border
                + angle_margin
                + 360 * 8  # Eight additional rotations for excitement
            )
        else:
            current_angle = self.wheel_angle
            new_angle = current_angle + random.uniform(360 * 8, 360 * 9)

        return new_angle

    def spin(self, exciting=False) -> SnackData:
        new_angle = self.get_random_new_angle(exciting=exciting)

        anim = Animation(wheel_angle=new_angle, duration=8, t="out_quint")
        anim.bind(on_complete=self.on_wheel_animation_complete)
        anim.start(self)

        return self.predict_snack_at_angle(
            read_angle=self.pointer_angle, total_rotation=new_angle
        )

    def on_wheel_animation_complete(self, *args):
        current_snack = self.get_current_snack_at_angle(read_angle=self.pointer_angle)
        self.dispatch("on_spin_complete", current_snack)

    def on_spin_complete(self, snack, *args):
        pass
