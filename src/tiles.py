"""Contains all tiles."""
from utils import color


class Tile:
    # def __init__(self, pos):
    #     self.pos = pos

    def enemy_walkable(self):
        return self.walkable or self.trampleable


class Floor(Tile):
    walkable = True
    trampleable = False
    color = color("94DEFF")


class Wall(Tile):
    walkable = False
    trampleable = False
    color = color("FD9AFF")


class Tower(Tile):
    walkable = False
    trampleable = True


class Empty(Tile):
    walkable = False
    trampleable = False


class Center(Tile):
    walkable = False
    trampleable = True
    color = color("FFBD7F")


class Proxy(Tile):
    def __init__(self, pos, proxy):
        Tile.__init__(self, pos)
        self.proxy = proxy

    def __getattr__(self, item):
        return self.proxy.__getattr__(item)
