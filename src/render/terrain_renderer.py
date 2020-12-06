"""Generate a geom node from heightmap."""
from panda3d.core import GeomNode
from render.wall_renderer import WallRenderer


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
            try:
                return height_map[i][j]
            except IndexError:
                return False

        print(map_size)
        for i in range(map_size):
            for j in range(map_size):
                current_position = (
                    start_pos+i*self.unit_size, start_pos+j*self.unit_size, 0
                )
                if get(i, j):
                    geom_node.addGeom(WallRenderer(
                        current_position,
                        (self.unit_size, self.unit_size, self.height),
                        self.colors.wall,
                        [not get(i-1, j), not get(i+1, j),
                            not get(i, j-1), not get(i, j+1)]
                    ).get_geom())
                else:
                    geom_node.addGeom(WallRenderer(
                        current_position,
                        (self.unit_size, self.unit_size, 0),
                        self.colors.floor,
                        [0, 0, 0, 0]
                    ).get_geom())
        return geom_node
