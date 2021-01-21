from math import atan2, pi

from utils import color
from config import map_params
from panda3d.core import Vec3
from model import Model
from bullet import Bullet
from tiles import Tile


class Trampleable(Tile, Model):
    walkable = False
    trampleable = True

    def __init__(self, pos):
        self.grid_pos = pos
        self.pos = Vec3(*pos, 0.0) * map_params.unit_size
        super().__init__()

    def trample(self, damage):
        self.hp = max(0, self.hp - damage)


def viewable(self, mypos, targpos, rad, get_tile):
    mypos = Vec3(mypos)
    direction_unit = (targpos-mypos).normalized()
    distance = (targpos-mypos).length()
    for _ in range(int(distance-rad)):
        mypos += direction_unit
        if get_tile(mypos).height < -1:
            return False
        if mypos[2] < 0:
            return False
        if mypos[2] < get_tile((mypos[0], mypos[1])).height and \
                get_tile((mypos[0], mypos[1])) != self:
            return False
    return True

class Tower(Trampleable):
    def __init__(self, *args):
        self.bullets = set()
        Trampleable.__init__(self, *args)

    def move(self, enemies, dt):
        pass

    def generate_bullet(self, *args):
        for bullet in set(self.bullets):
            if not bullet.generated:
                bullet.generate(*args)


class ShootTower(Tower):
    width = 1
    name = "tower"
    max_hp = 50
    range = 100
    height = 15.
    cannon_height = 10
    scale = 10.0
    cd = 0.5
    cost = 40
    color = color("FFF000")

    def __init__(self, *args):
        self.remain_cd = 0
        Tower.__init__(self, *args)

    def flatten(self):
        pass

    def get_cannon_pos(self):
        return self.model.getPos() + Vec3(0, 0, self.cannon_height)

    def aim(self, dt, enemies):
        pos = self.get_cannon_pos()

        def valid(enemy):
            enemy_pos = enemy.get_pos()
            if (enemy_pos-pos).length() > self.range:
                return False
            return viewable(self, pos, enemy_pos, enemy.radius, self.get_tile)
        my_enemies = [enemy.get_pos() for enemy in enemies if valid(enemy)]
        my_enemies.sort(key=lambda a: (a-pos).length())
        if len(my_enemies):
            dirs = my_enemies[0]-pos
            self.model.setHpr(atan2(dirs[1], dirs[0])*180/pi, 90.0, 0.0)

        if self.remain_cd >= 0:
            self.remain_cd -= dt
        if self.remain_cd < 0 and len(my_enemies):
            self.remain_cd += self.cd
            self.shoot()

    def shoot(self):
        self.bullets.add(
            Bullet(self.get_cannon_pos(), self.model.getHpr(), self))

    def move_bullet(self, dt, enemies):
        for bullet in set(self.bullets):
            if not bullet.is_active:
                self.bullets.remove(bullet)
            bullet.move(dt, enemies)

    def move(self, dt, enemies):
        self.move_bullet(dt, enemies)
        self.aim(dt, enemies)


class WallTower(Tower):
    width = 1
    name = "icecream"
    max_hp = 50
    height = 15.
    scale = 10.0
    cost = 30
    color = color("F0E000")


class Center(Trampleable):
    walkable = False
    trampleable = True
    width = map_params.center_size
    name = "cake_square"
    scale = 30.0
    max_hp = 200
    height = 20
    color = color("FFBD7F")

    def flatten(self):
        pass
