"""Contains all tiles."""
from math import atan2

from utils import color, abspath
from config import map_params
from panda3d.core import Point3, CardMaker, NodePath, Vec3


class Tile:
    def enemy_walkable(self):
        return self.walkable or self.trampleable

    def __del__(self):
        try:
            self.node.removeNode()
        except AttributeError:
            pass

    def generate(self, pos):
        usz = map_params.unit_size
        msz = (map_params.field_size*map_params.cell_size
               + (map_params.field_size-1)*map_params.wall_width)
        pos = (-msz*usz/2 + pos[0] * usz, -msz*usz/2 + pos[1] * usz)
        card_maker = CardMaker("cm")
        card_maker.setFrame(
            Point3(pos[0], pos[1], 0),
            Point3(pos[0]+usz, pos[1], 0),
            Point3(pos[0]+usz, pos[1]+usz, 0),
            Point3(pos[0], pos[1]+usz, 0)
        )
        card_maker.setColor(self.color)
        self.node = NodePath(card_maker.generate())
        return self.node


class Floor(Tile):
    walkable = True
    trampleable = False
    width = 1
    height = 0
    color = color("94DEFF")


class Wall(Tile):
    walkable = False
    trampleable = False
    width = 1
    height = 100
    color = color("FD9AFF")

class Empty(Tile):
    walkable = False
    trampleable = False
    height = -100

class Trampleable(Tile):
    walkable = False
    trampleable = True

    def __init__(self, loader, parent, pos):
        self.model = loader.loadModel(abspath(f"models/{self.name}.dae"))
        self.model.reparentTo(parent)
        self.model.setHpr(0, 90, 0)
        self.model.setScale(self.scale)
        self.model.setPos(Vec3(*pos, 0) * map_params.unit_size)
        # print(self.model.findAllMatches("**/*"))
        # self.model.clearModelNodes()
        # self.model.flattenStrong()
    def trample(self, damage):
        self.hp = max(0, self.hp - damage)


def viewable(mypos, targpos, get_tile):
    direction_unit = (targpos-mypos).normalized()
    distance = (targpos-mypos).length()
    for _ in range(int(distance)):
        mypos += direction_unit
        if get_tile(mypos).height < -1 :
            return False
        elif mypos[2] < 0:
            return False
        elif mypos[2] < get_tile(mypos[0], mypos[1]).height:
            return False
    return True


class Tower(Trampleable):
    width = 1
    name = "tower"
    hp = 50
    range = 30
    height = 15.
    cannon_height = 12.5
    scale = 10.0
    cd = 1
    color = color("FFF000")

    def __init__(self, *args):
        self.remain_cd = 0
        Trampleable.__init__(self, *args)

    def flatten(self):
        pass

    def check_shoot(self, dt, enemies, get_tile):
        self.remain_cd -= dt
        if self.remain_cd < 0:
            self.remain_cd += self.cd
            self.try_shoot(self, enemies, get_tile)

    def try_shoot(self, enemies, get_tile):
        pos = self.model.getPos()
        pos[2] = self.cannon_height

        def valid(enemy):
            if (enemy-pos).length() > range:
                return False
            return viewable(pos, enemy, get_tile)
        my_enemies = [Vec3(
            enemy.model.getPos()[0], enemy.model.getPos()[1], enemy.height
        ) for enemy in enemies]
        my_enemies = [enemy for enemy in enemies if valid(enemy)]
        my_enemies.sort(key=lambda a: (a-pos).length())
        dirs = my_enemies[0]-pos
        self.model.setHpr(atan2(dirs[1], dirs[0]), 90.0, 0)
        self.shoot()

    def shoot(self):
        pass



class Center(Trampleable):
    walkable = False
    trampleable = True
    width = map_params.center_size
    name = "cake_square"
    scale = 30.0
    hp = 200
    height = 20
    color = color("FFBD7F")
    def flatten(self):
        pass


class Proxy:
    def __init__(self, proxy):
        self.proxy = proxy

    def __getattr__(self, item):
        return self.proxy.__getattribute__(item)
