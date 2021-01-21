
from math import atan2, pi, hypot, floor
from threading import Thread

from panda3d.core import Vec3
import config
from model import Model


class Enemy(Model):
    """The class of general enemies."""

    def __init__(self, pos):
        self.pos = pos
        self.moves = []
        self.cd_left = 0
        super().__init__()

    def generate(self, path_finder, *args):
        super().generate(*args)
        self.path_finder = path_finder

    def calculate_moves(self, sync=True):
        cur_pos = self.model.getPos()

        def task():
            self.moves = list(self.path_finder.astar(
                (int(floor(cur_pos[0]))//config.map_params.unit_size,
                 int(floor(cur_pos[1]))//config.map_params.unit_size),
                (0, 0)
            ))
            self.moves.reverse()
            if not sync:
                self.moves.pop()

        if sync:
            task()
        else:
            Thread(target=task).start()

    def move(self, dt):
        """Move the Enemy according to pathfinder."""
        cur_pos = self.model.getPos()

        if self.moves is None:
            return

        if not self.get_tile((cur_pos[0], cur_pos[1])).walkable:
            self.model.setPos(cur_pos+Vec3(config.map_params.unit_size, 0, 0))
            self.moves = []
            return

        surr = [cur_pos + Vec3(*drn, 0)*self.radius
                for drn in [[1, 1], [1, -1], [-1, -1], [-1, 1]]]

        for pos in surr:
            if self.get_tile(pos).trampleable:
                self.trample(dt, self.get_tile(pos))
                return

        if not all(self.get_tile(pos).enemy_walkable() for pos in surr):
            self.model.setPos(cur_pos+Vec3(config.map_params.unit_size, 0, 0))
            self.moves = []
            return

        if not self.cd_left or not self.moves:
            self.moves = None
            self.calculate_moves(sync=False)
            self.cd_left = self.cd_max
            return

        dis = Vec3(*self.moves[-1], 0.0)*config.map_params.unit_size - cur_pos
        if dis.length() < dt * self.speed:
            self.model.setPos(dis + cur_pos)
            self.cd_left -= 1
            self.moves.pop()
            self.move(dt - dis.length() / self.speed)
            return

        dis.normalize()
        # self.model.setPos(cur_pos + dis * self.speed * dt)

        def walkable(pos):
            return all(self.get_tile(pos+Vec3(*drn, 0)*self.radius).enemy_walkable()
                       for drn in [[1, 1], [1, -1], [-1, -1], [-1, 1]])

        for i in range(2):
            vec = [0, 0, 0]
            vec[i] = dis[i] * dt * self.speed
            vec = Vec3(*vec)
            if walkable(cur_pos + vec):
                cur_pos += vec

        dist_p = cur_pos - self.model.getPos()
        dist_h = atan2(dist_p[1], dist_p[0])*180/pi+90 - self.model.getHpr()[0]
        dist_h = (dist_h % 360 + 360) % 360
        if dist_h > 180:
            dist_h -= 360
        if abs(dist_h) > self.omega * dt:
            dist_h *= self.omega * dt / abs(dist_h)

        self.model.setHpr(self.model.getHpr()[0]+dist_h, 90, 0)

        self.model.setPos(cur_pos)

    def trample(self, dt, tile):
        tile.trample(dt*self.dps)

    def get_pos(self):
        return Vec3(self.model.getPos().xy, self.height//2)

    def collide(self, pos):
        if not self.generated:
            return False
        return hypot(*(self.model.getPos()-pos).xy) <= self.radius \
            and pos[2] <= self.height


class Kikiboss(Enemy):
    name = "kikiboss"
    cd_max = 10
    speed = 10.0
    dps = 10
    omega = 720
    height = 15
    radius = 4
    scale = 10.0
    max_hp = 10

    def __init__(self, *args):
        super().__init__(*args)

    def trample(self, dt, tile):
        self.model.setHpr(self.model.getHpr()[0]+dt*self.omega, 90, 0)
        super().trample(dt, tile)
