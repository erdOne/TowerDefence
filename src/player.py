"""The player."""
from math import atan2, pi, sin, cos

from panda3d.core import Vec3, LVecBase3

import config
from utils import directions


class Player:
    """The player."""

    def __init__(self):
        self.pos = Vec3(0, 0, 5)
        self.velocity = Vec3(0, 0, 0)
        self.hpr = LVecBase3(0, 0, 0)

    def update_pos(self, key_state, dt):
        """Update position from key state."""
        direction = Vec3(0, 0, 0)
        for key, vec in directions:
            if key_state[getattr(config.key_map.character, key)]:
                direction += Vec3(*vec, 0)

        if not direction.normalize():
            self.velocity *= 1 - config.physics.stop_friction * dt
        else:
            angle = atan2(direction[1], direction[0])
            print(self.hpr[0], angle*180/pi)
            angle += (self.hpr[0]-90) * pi / 180
            direction = Vec3(-sin(angle), cos(angle), 0).normalized()

            prev = self.velocity.project(direction)
            if self.velocity.dot(direction) < 0:
                prev *= 0
            if prev.length() < (self.velocity.length() *
                                config.physics.keep_velocity):
                prev += direction * (
                    self.velocity.length() * config.physics.keep_velocity -
                    prev.length()
                )

            diff = (self.velocity - prev) * (
                1 - config.physics.friction * dt
            )
            accel = direction * config.physics.walk_accel
            self.velocity = prev + diff + accel * dt

        if self.velocity.length() > config.physics.max_speed:
            self.velocity = (
                self.velocity.normalized() * config.physics.max_speed
            )

        self.pos += self.velocity * dt
        # print(self.velocity.length(), self.velocity)

    def update_hpr(self, mouse_pos):
        """Set hpr from mouse position."""
        self.hpr = LVecBase3(
            -mouse_pos[0]*config.mouse_params.heading_speed,
            mouse_pos[1]*config.mouse_params.pitch_speed,
            0
        )
