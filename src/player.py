"""The player."""
from math import atan2, pi, sin, cos, floor

from panda3d.core import Vec3, LVecBase3

import config
from utils import directions


class Player:
    """The player."""

    def __init__(self):
        self.pos = Vec3(0, 0, 7.5)
        self.prepos = self.pos
        self.velocity = Vec3(0, 0, 0)
        self.hpr = LVecBase3(90, 90, 0)

    def update_pos(self, key_state, dt, is_walkable):
        """Update position from key state."""
        self.prepos = Vec3(self.pos)
        direction = Vec3(0, 0, 0)
        for key, vec in directions:
            if key_state[getattr(config.key_map.character, key)]:
                direction += Vec3(*vec, 0)

        if not direction.normalize():
            self.velocity *= max(1 - config.physics.stop_friction * dt, 0)
        else:
            angle = atan2(direction[1], direction[0])
            # print(self.hpr[0], angle*180/pi)
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

        def walkable(pos):
            return all(is_walkable(pos + Vec3(*drn, 0) * config.player.size)
                       for drn in [[1, 1], [1, -1], [-1, -1], [-1, 1]])

        for i in range(3):
            vec = [0, 0, 0]
            vec[i] = self.velocity[i] * dt
            vec = Vec3(*vec)
            if walkable(self.pos + vec):
                self.pos += vec

    def update_hpr(self, mouse_pos):
        """Set hpr from mouse position."""
        self.hpr = LVecBase3(
            -mouse_pos[0]*config.mouse_params.heading_speed,
            mouse_pos[1]*config.mouse_params.pitch_speed,
            0
        )
