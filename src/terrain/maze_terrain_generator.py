"""A class that generate maze-like terrains."""
from utils import generate_2d_array, Object, directions
from terrain.maze_generator import MazeGenerator
from config import map_params
from tiles import Wall, Floor


class MazeTerrainGenerator():
    """The class that generates terrains."""

    def __init__(self):
        """
        Init the class.

        Requires the parity of the two sizes to be the same.
        """
        self.map_size = (map_params.field_size*map_params.cell_size
                         + (map_params.field_size-1)*map_params.wall_width)
        self.wall_dist = self.get_wall_distrubution()
        self.maze_map = generate_2d_array(self.map_size, default=False)

    def get_wall_distrubution(self):
        """Return an array to be traversed."""
        x_pos, x_next = 0, 0
        dx = map_params.wall_width
        res = []
        for i in range(self.map_size):
            if i == x_next:
                dx = map_params.cell_size + map_params.wall_width - dx
                x_next += dx
                x_pos += 1
            res.append((i, x_pos))
        return res

    def remove_pillars(self):
        """Remove standalone pillars."""
        def get(i, j):
            if i < 0 or i >= self.map_size:
                return False
            if j < 0 or j >= self.map_size:
                return False
            return self.maze_map[i][j]

        for i in range(self.map_size):
            for j in range(self.map_size):
                if get(i, j):
                    for dx, dy in Object.values(directions):
                        if get(i+dx, j+dy):
                            break
                    else:
                        self.maze_map[i][j] = False

    def generate(self, seed, origin):
        """Generate height map after generating maze."""
        maze = MazeGenerator().generate_maze(seed, origin)
        for i, i_pos in self.wall_dist:
            for j, j_pos in self.wall_dist:
                if i_pos % 2 == 0 and j_pos % 2 == 0:
                    self.maze_map[i][j] = True
                if i_pos % 2 == 0 and j_pos % 2 == 1:
                    self.maze_map[i][j] = bool(maze[0][i_pos//2][j_pos//2])
                if i_pos % 2 == 1 and j_pos % 2 == 0:
                    self.maze_map[i][j] = bool(maze[1][i_pos//2][j_pos//2])
                if i_pos % 2 == 1 and j_pos % 2 == 1:
                    self.maze_map[i][j] = False
        self.remove_pillars()
        for i in range(self.map_size):
            for j in range(self.map_size):
                self.maze_map[i][j] = \
                    Wall((i, j)) if self.maze_map[i][j] else Floor((i, j))
        return self.maze_map
