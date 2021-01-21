"""Contains all tiles."""

from panda3d.core import Point3, CardMaker, NodePath

from utils import color
from config import map_params


class Tile:
    def enemy_walkable(self):
        return self.walkable or self.trampleable

    def __del__(self):
        try:
            self.node.removeNode()
        except AttributeError:
            pass

    def generate_map(self, pos):
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
