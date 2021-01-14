
from third_party.astar import AStar
from math import hypot
from utils import directions, Object
from config import map_params


class PathFinder(AStar):

    def __init__(self, get_tile):
        self.get_tile = (lambda tup: get_tile((
            tup[0] * map_params.unit_size, tup[1] * map_params.unit_size
        )))
        self.tower_weight = 20
        self.search_width = 3
        self.gone = set()

    def heuristic_cost_estimate(self, n_1, n_2):
        """computes the 'direct' distance between two (x,y) tuples"""
        # if n_1 not in self.gone:
        #     print(n_1)
        #     self.gone.add(n_1)
        #
        # if n_2 not in self.gone:
        #     print(n_2)
        #     self.gone.add(n_2)

        (x_1, y_1) = n_1
        (x_2, y_2) = n_2
        return hypot(x_2 - x_1, y_2 - y_1)

    def distance_between(self, n_1, n_2):
        (x_1, y_1) = n_1
        (x_2, y_2) = n_2
        if x_1 >= x_2:
            x_1, x_2 = x_2, x_1
        if y_1 >= y_2:
            y_1, y_2 = y_2, y_1
        count, t_count = 0, 0
        for i in range(x_1, x_2+1):
            for j in range(y_1, y_2+1):
                count += 1
                if not self.get_tile((i, j)).walkable:
                    t_count += 1
        # print(t_count / count * self.tower_weight)
        return hypot(x_2 - x_1, y_2 - y_1) * \
            (1 + t_count / count * self.tower_weight)

    def neighbors(self, pos):
        ans = set()
        for dx, dy in Object.values(directions):
            for j in [-1, 1]:
                for i in range(self.search_width):
                    cur = (pos[0] + dx + dy * i * j, pos[1] + dy + dx * i * j)
                    try:
                        if not self.get_tile(cur).enemy_walkable():
                            break
                    except TypeError:
                        print(self.get_tile(cur))
                        raise EOFError
                    ans.add(cur)
        # print(ans)
        return [*ans]
