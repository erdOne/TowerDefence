"""A class that generate maze-like terrains."""
import random
from sortedcontainers import SortedDict
from utils import generate_2d_array, directions, Object


class MazeGenerator():
    """The class that generates terrains."""

    def __init__(self, field_size):
        """
        Init the class.

        Requires the parity of the two sizes to be the same.
        """
        self.field_size = field_size
        self.adjacency_list = [[] for _ in range(field_size**2)]
        self.pending_set = SortedDict()
        self.used_set = set()
        self.result = (
            generate_2d_array(field_size+1, field_size, True),
            generate_2d_array(field_size, field_size+1, True)
        )

    def insert_point(self, item):
        """Insert into pending set with random key."""
        while True:
            key = random.random()
            if key not in self.pending_set:
                break
        self.pending_set[key] = item

    def remove_wall_between(self, point_a, point_b):
        """Remove the wall between point_a and point_b."""
        if not self.in_range(point_a) or not self.in_range(point_b):
            return
        if point_a > point_b:
            point_a, point_b = point_b, point_a
        if point_a[0] != point_b[0]:
            assert point_a[0]+1 == point_b[0], ValueError
            assert point_a[1] == point_b[1], ValueError
            self.result[0][point_a[0]+1][point_a[1]] = False
        else:
            assert point_a[1]+1 == point_b[1], ValueError
            assert point_a[0] == point_b[0], ValueError
            self.result[1][point_a[0]][point_a[1]+1] = False

    def in_range(self, point):
        """Check if point is in range."""
        if point[0] < 0 or point[0] >= self.field_size:
            return False
        if point[1] < 0 or point[1] >= self.field_size:
            return False
        return True

    def process_point(self, point, parent):
        """Link the point to its parent, remove the wall between."""
        if not self.in_range(point):
            self.process_next()
            return
        if point in self.used_set:
            self.process_next()
            return
        self.used_set.add(point)
        self.remove_wall_between(point, parent)
        for dx, dy in Object.values(directions):
            self.insert_point(((point[0]+dx, point[1]+dy), point))
        if len(self.used_set) < self.field_size**2:
            self.process_next()

    def process_next(self):
        """Process a random point in pending set."""
        key = next(iter(self.pending_set))
        next_point = self.pending_set[key]
        del self.pending_set[key]
        self.process_point(*next_point)

    def remove_random_edges(self):
        """Remove some edges to create shortcuts."""
        for _ in range(int(self.field_size**2/2)):
            x_pos = random.randrange(self.field_size)
            y_pos = random.randrange(self.field_size)
            self.result[random.randrange(2)][x_pos][y_pos] = False

    def generate_maze(self, seed):
        """Start the generation wrt the seed."""
        random.seed(seed)
        self.insert_point(
            ((self.field_size//2, self.field_size//2), (-1, -1))
        )
        self.process_next()
        self.remove_random_edges()
        return self.result

    def __str__(self):
        """Print out the terrain (for debug purposes)."""
        res = ""
        for x_pos in range(self.field_size*2+1):
            for y_pos in range(self.field_size*2+1):
                if x_pos % 2 == 0 and y_pos % 2 == 0:
                    res += "Ｘ"
                if x_pos % 2 == 0 and y_pos % 2 == 1:
                    res += "Ｘ" if self.result[0][x_pos//2][y_pos//2] else "　"
                if x_pos % 2 == 1 and y_pos % 2 == 0:
                    res += "Ｘ" if self.result[1][x_pos//2][y_pos//2] else "　"
                if x_pos % 2 == 1 and y_pos % 2 == 0:
                    res += "　"
            res += "\n"
        return res
