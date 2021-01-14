
from os import getcwd, path
from math import atan2, pi
from threading import Thread

from panda3d.core import Vec3
import config
from utils import abspath


def EnemyFactory(loader, parent, path_finder):
    return lambda pos: Enemy(loader, parent, path_finder, pos)


class Enemy:
    """The class of general enemies."""
    name = "kikiboss"
    cd_max = 10
    speed = 10.0
    dps = 10
    size = 1
    omega = 720
    height = 15

    def __init__(self, loader, parent, path_finder, pos):
        self.model = loader.loadModel(abspath(f"models/{self.name}.dae"))
        self.model.clearModelNodes()
        self.model.flattenStrong()
        self.model.reparentTo(parent)
        self.model.setPos(pos)
        self.model.setScale(10.0)
        self.model.setHpr(0, 90, 0)
        self.moves = []
        self.path_finder = path_finder
        self.cd_left = 0

    def calculate_moves(self, sync=True):
        cur_pos = self.model.getPos()

        def task():
            self.moves = list(self.path_finder.astar(
                (int(cur_pos[0])//config.map_params.unit_size,
                 int(cur_pos[1])//config.map_params.unit_size),
                (0, 0)
            ))
            self.moves.reverse()
            if not sync:
                self.moves.pop()

        if sync:
            task()
        else:
            Thread(target=task).start()

    def move(self, dt, get_tile):
        """Move the Enemy according to pathfinder."""
        cur_pos = self.model.getPos()

        if self.moves is None:
            return

        if not get_tile((cur_pos[0], cur_pos[1])).enemy_walkable():
            self.model.setPos(cur_pos+Vec3(config.map_params.unit_size, 0, 0))
            self.moves = []
            return

        if not self.cd_left or not self.moves:
            self.moves = None
            self.calculate_moves(sync=False)
            self.cd_left = self.cd_max
            return

        if get_tile((cur_pos[0], cur_pos[1])).trampleable:
            self.model.setHpr(self.model.getHpr()[0]+dt*self.omega, 90, 0)
            self.trample(dt, get_tile((cur_pos[0], cur_pos[1])))
            return

        dis = Vec3(*self.moves[-1], 0.0)*config.map_params.unit_size - cur_pos
        if dis.length() < dt * self.speed:
            self.model.setPos(dis + cur_pos)
            self.cd_left -= 1
            self.moves.pop()
            self.move(dt - dis.length() / self.speed, get_tile)
            return

        dis.normalize()
        # self.model.setPos(cur_pos + dis * self.speed * dt)

        def walkable(pos):
            return all(get_tile(pos + Vec3(*drn, 0)*self.size).enemy_walkable()
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
        self.model

    def trample(self, dt, tile):
        tile.trample(dt*self.dps)
