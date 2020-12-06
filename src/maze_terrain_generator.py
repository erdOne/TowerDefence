"""A class that generate maze-like terrains."""
from utils import generate_2d_array
from maze_generator import MazeGenerator


class MazeTerrainGenerator():
    """The class that generates terrains."""

    def __init__(self, field_size, cell_size, wall_width):
        """
        Init the class.

        Requires the parity of the two sizes to be the same.
        """
        self.field_size = field_size
        self.cell_size = cell_size
        self.wall_width = wall_width
        self.map_size = field_size*cell_size+(field_size-1)*wall_width
        self.wall_dist = self.get_wall_distrubution()

    def get_wall_distrubution(self):
        """Return an array to be traversed."""
        x_pos, x_next = 0, 0
        dx = self.wall_width
        res = []
        for i in range(self.map_size):
            if i == x_next:
                dx = self.cell_size + self.wall_width - dx
                x_next += dx
                x_pos += 1
            res.append((i, x_pos))
        return res

    def remove_pillars(self, height_map):
        """Remove standalone pillars."""
        def get(i, j):
            if i < 0 or i >= self.map_size:
                return False
            if j < 0 or j >= self.map_size:
                return False
            return height_map[i][j]

        for i in range(self.map_size):
            for j in range(self.map_size):
                if get(i, j):
                    for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
                        if get(i+dx, j+dy):
                            break
                    else:
                        height_map[i][j] = False
        return height_map

    def generate(self, seed):
        """Generate height map after generating maze."""
        maze_map = generate_2d_array(self.map_size, default=False)
        maze = MazeGenerator(self.field_size).generate_maze(seed)
        for i, i_pos in self.wall_dist:
            for j, j_pos in self.wall_dist:
                if i_pos % 2 == 0 and j_pos % 2 == 0:
                    maze_map[i][j] = True
                if i_pos % 2 == 0 and j_pos % 2 == 1:
                    maze_map[i][j] = bool(maze[0][i_pos//2][j_pos//2])
                if i_pos % 2 == 1 and j_pos % 2 == 0:
                    maze_map[i][j] = bool(maze[1][i_pos//2][j_pos//2])
                if i_pos % 2 == 1 and j_pos % 2 == 1:
                    maze_map[i][j] = False
        return self.remove_pillars(maze_map)
