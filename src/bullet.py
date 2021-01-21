from math import hypot
from panda3d.core import Vec3
from enemy.basic import Enemy
from tiles import Tile
from model import Model


class Bullet(Model):
    name = "cherry"
    damage = 3
    vel = 100
    scale = 6.0

    def __init__(self, pos, hpr, parent_tower):
        self.pos = pos
        self.hpr = hpr
        self.is_active = True
        self.parent_tower = parent_tower
        super().__init__()

    def move(self, dt, enemies):
        if not self.is_active or not self.generated:
            return
        pos = self.model.getPos()
        direct = self.model.getQuat().xform(Vec3(1, 0, 0))
        pos += direct * self.vel * dt
        self.model.setPos(pos)

        if pos[2] <= 0:
            self.hit(None)
            return
        for enemy in enemies:
            if enemy.collide(pos):
                self.hit(enemy)
                return
        cur_tile = self.get_tile((pos[0], pos[1]))
        if cur_tile != self.parent_tower and pos[2] <= cur_tile.height:
            self.hit(None)
            # print("hit", direct, pos, cur_tile)
            return

    def hit(self, obj):
        self.model.removeNode()
        self.is_active = False
        if obj is None:
            return
        if isinstance(obj, Tile):
            return
        if isinstance(obj, Enemy):
            obj.hit(self.damage)
            return
