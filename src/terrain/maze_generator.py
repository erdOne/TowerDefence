"""A class that generate maze-like terrains."""
import random
from sortedcontainers import SortedDict
from utils import generate_2d_array, directions, Object
from config import map_params

field_size = map_params.field_size  # type: ignore


class MazeGenerator():
    """The class that generates terrains."""

    def __init__(self):
        """
        Init the class.

        Requires the parity of the two sizes to be the same.
        """
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

    @staticmethod
    def in_range(point):
        """Check if point is in range."""
        if point[0] < 0 or point[0] >= field_size:
            return False
        if point[1] < 0 or point[1] >= field_size:
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
        self.process_next()

    def process_next(self):
        """Process a random point in pending set."""
        try:
            key = next(iter(self.pending_set))
            next_point = self.pending_set[key]
            del self.pending_set[key]
            self.process_point(*next_point)
        except StopIteration:
            pass

    def remove_random_edges(self):
        """Remove some edges to create shortcuts."""
        for _ in range(int(field_size**2/5)):
            x_pos = random.randrange(field_size)
            y_pos = random.randrange(field_size)
            self.result[random.randrange(2)][x_pos][y_pos] = False

    def clear_core(self):
        """Clear space for core."""
        start = (field_size - map_params.core_size) // 2

        for i in range(map_params.core_size):
            for j in range(map_params.core_size-1):
                self.remove_wall_between(
                    (start+i, start+j), (start+i, start+j+1)
                )
                self.remove_wall_between(
                    (start+j, start+i), (start+j+1, start+i)
                )

    def generate_maze(self, seed, origin):
        """
        Start the generation wrt the seed.
        origin:
              1
            4 0 8
              2
        """
        random.seed(seed)
        if not origin:
            self.insert_point(
                ((field_size//2, field_size//2), (-1, -1))
            )
        for j, (dx, dy) in zip(range(4), Object.values(directions)):
            if origin & (1 << j):
                for i in range(field_size):
                    self.insert_point(((
                        (field_size-1)*(dx+1)//2 if dx else i,
                        (field_size-1)*(dy+1)//2 if dy else i
                    ), (-1, -1)))
        self.process_next()
        self.remove_random_edges()
        if not origin:
            self.clear_core()
        return self.result

    def __str__(self):
        """Print out the terrain (for debug purposes)."""
        res = ""
        for x_pos in range(field_size*2+1):
            for y_pos in range(field_size*2+1):
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
