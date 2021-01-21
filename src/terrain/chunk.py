""" Saves a chunck of terrain in chunk map. """
from math import atan2, pi

from terrain.maze_terrain_generator import MazeTerrainGenerator
from terrain.renderer import TerrainRenderer
import config
from towers import Center


class Chunk(TerrainRenderer):
    """ Saves a chunk of terrain in chunk map. """
    def __init__(self, pos):
        TerrainRenderer.__init__(self)
        self.pos = pos

    def generate(self, loader):
        """ Generates terrain_map. """
        origin = 0
        if self.pos[0] or self.pos[1]:
            for i in range(4):
                if abs(pi/2*i - atan2(*self.pos) + 1e-6) % (2*pi) < pi/3:
                    origin |= 1 << i
        self.terrain_map = MazeTerrainGenerator().generate(
            config.map_params.seed ^ hash(self.pos), origin
        )
        # if not origin:
        #     self.set_center()
        self.create_geom(loader)
        self.create_minimap()

    def set_center(self):
        csize = config.map_params.center_size // 2
        fsize = len(self.terrain_map) // 2
        for i in range(fsize-csize, csize+fsize+1):
            for j in range(fsize-csize, csize+fsize+1):
                self.terrain_map[i][j] = Center()

    def set_tile(self, pos, value):
        i, j = pos
        self.terrain_map[i][j] = value
        value.generate_map((i, j)).reparentTo(self.minimap_node)

    def show(self):
        self.geom_node.show()
        self.minimap_node.show()

    def hide(self):
        self.geom_node.hide()
        self.minimap_node.hide()
