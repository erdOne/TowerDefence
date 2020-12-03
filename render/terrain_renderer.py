"""Generate a geom node from heightmap."""
from render.wall_renderer import WallRenderer
from panda3d.core import GeomNode


class TerrainRenderer:
    """Render the map."""

    def __init__(self, unit_size, height, colors):
        """Init the class."""
        self.unit_size = unit_size
        self.height = height
        self.colors = colors

    def get_geom(self, height_map):
        """Return the geom."""
        geom_node = GeomNode("background terrain")
        map_size = len(height_map)
        start_pos = -map_size*self.unit_size/2

        def get(i, j):
            if i < 0 or i >= map_size:
                return False
            if j < 0 or j >= map_size:
                return False
            return height_map[i][j]
        print(map_size)
        for i in range(map_size):
            for j in range(map_size):
                if get(i, j):
                    geom_node.addGeom(WallRenderer(
                        (start_pos+i*self.unit_size, start_pos+j*self.unit_size, 0),
                        (self.unit_size, self.unit_size, self.height),
                        self.colors.wall,
                        [not get(i-1, j), not get(i+1, j),
                            not get(i, j-1), not get(i, j+1)]
                    ).get_geom())
                else:
                    geom_node.addGeom(WallRenderer(
                        (start_pos+i*self.unit_size, start_pos+j*self.unit_size, 0),
                        (self.unit_size, self.unit_size, 0),
                        self.colors.floor,
                        [0, 0, 0, 0]
                    ).get_geom())
        return geom_node
