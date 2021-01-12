
class Tile:
    def __init__(self, pos):
        self.pos = pos


class Floor(Tile):
    walkable = True


class Wall(Tile):
    walkable = False


class Tower(Tile):
    walkable = False


class Empty(Tile):
    walkable = False
