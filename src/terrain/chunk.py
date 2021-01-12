""" Saves a chunck of terrain in chunk map. """
from math import atan2, pi

from terrain.maze_terrain_generator import MazeTerrainGenerator
from terrain.renderer import TerrainRenderer
import config
from utils import directions, Object


class Chunk(TerrainRenderer):
    """ Saves a chunk of terrain in chunk map. """
    def __init__(self, pos):
        TerrainRenderer.__init__(self)
        self.pos = pos

    def generate(self, loader):
        """ Generates terrain_map. """
        origin = 0
        if self.pos[0] or self.pos[1]:
            for i, (dx, dy) in zip(range(4), Object.values(directions)):
                if abs(atan2(*self.pos) - atan2(dx, dy) + 1e-6) % (2*pi) < pi/6:
                    origin |= 1 << i
        self.terrain_map = MazeTerrainGenerator().generate(
            config.map_params.seed ^ hash(self.pos), origin
        )
        self.create_geom(loader)
        self.create_minimap()

    def show(self):
        self.geom_node.show()
        self.minimap_node.show()

    def hide(self):
        self.geom_node.hide()
        self.minimap_node.hide()
