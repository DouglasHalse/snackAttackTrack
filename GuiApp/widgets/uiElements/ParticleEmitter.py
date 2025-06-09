import math
import random

from kivy.clock import Clock
from kivy.graphics import Color, Point
from kivy.uix.floatlayout import FloatLayout


class ParticleEmitter(FloatLayout):
    __events__ = ("on_particles_emitted", "on_emitting_complete")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.colors = []
        self.point_size = 5
        self.number_of_particles = 0
        self.particle_coordinates = []
        self.point_velocities = []
        self.point_lifetimes = []
        self.wind_direction = 0

    def point_on_edge(self, center_x, center_y, width, height, direction):
        dx = math.cos(direction)
        dy = math.sin(direction)
        half_w = width / 2
        half_h = height / 2

        # Calculate t for each side
        if dx != 0:
            tx1 = half_w / abs(dx)
        else:
            tx1 = float("inf")
        if dy != 0:
            ty1 = half_h / abs(dy)
        else:
            ty1 = float("inf")

        t = min(tx1, ty1)
        edge_x = center_x + dx * t
        edge_y = center_y + dy * t
        return (edge_x, edge_y)

    def emit_burst(self, colors, particle_count=10, particle_size=5):
        self.dispatch(
            "on_particles_emitted",
        )

        self.colors = colors
        self.point_size = particle_size
        self.number_of_particles = particle_count
        self.particle_coordinates = []
        self.wind_direction = random.uniform(-1, 1)

        for _ in range(particle_count):
            direction = random.uniform(0, 2 * math.pi)
            speed = random.uniform(50, 500)
            velocity = [speed * math.cos(direction), speed * math.sin(direction)]
            start_position = self.point_on_edge(
                self.center_x, self.center_y, self.width, self.height, direction
            )

            self.particle_coordinates.extend(start_position)
            self.point_velocities.extend(velocity)
            self.point_lifetimes.append(random.uniform(1, 2))

        Clock.schedule_interval(self.update_particles, 1 / 60)

    def update_particles(self, dt):
        # Early exit if all lifetimes are <= 0
        if not self.point_lifetimes or all(
            lifetime <= 0 for lifetime in self.point_lifetimes
        ):
            Clock.unschedule(self.update_particles)
            self.dispatch("on_emitting_complete")
            return

        # Use local variables for faster access
        coords = self.particle_coordinates
        vels = self.point_velocities
        lifes = self.point_lifetimes
        n = len(lifes)
        w = self.width

        # Use range and step for efficient iteration
        for i in range(n):
            if lifes[i] <= 0:
                continue
            idx = i * 2
            coords[idx] += vels[idx] * dt
            coords[idx + 1] += vels[idx + 1] * dt
            vels[idx] += (
                dt
                * (100 * math.sin((coords[idx] / (w / 2)) + (dt * 5)))
                * self.wind_direction
            )
            vels[idx + 1] += -9.81 * dt * 15
            lifes[i] -= dt

        self.update_display()

    def update_display(self):
        self.canvas.clear()

        for color_index, color in enumerate(self.colors):
            with self.canvas:
                Color(
                    color[0],
                    color[1],
                    color[2],
                    sum(self.point_lifetimes) / len(self.point_lifetimes),
                )

                # Calculate every nth point for the current color
                # where n is the number of colors
                points_to_include = list(
                    range(color_index, self.number_of_particles, len(self.colors))
                )
                # Use a list comprehension for faster coordinate selection
                coordinates_to_draw = [
                    self.particle_coordinates[i * 2 + j]
                    for i in points_to_include
                    if self.point_lifetimes[i] > 0
                    for j in range(2)
                ]

                Point(
                    points=coordinates_to_draw,
                    pointsize=self.point_size,
                )

    def on_particles_emitted(self):
        pass

    def on_emitting_complete(self):
        pass
