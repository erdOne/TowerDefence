from config import color

class Tile:
    def __init__(self, pos):
        self.pos = pos


class Floor(Tile):
    walkable = True
    color = color("94DEFF")


class Wall(Tile):
    walkable = False
    color = color("FD9AFF")


class Tower(Tile):
    walkable = False


class Empty(Tile):
    walkable = False


class Center(Tile):
    walkable = False
    color = color("FFBD7F")
