"""Generate a geom node from heightmap."""
from os import getcwd, path
from threading import Thread, active_count

from panda3d.core import (CollisionNode, CollisionBox, Point3, Vec3, NodePath, CardMaker, TextureStage)

from third_party.geom import GeomBuilder
from config import map_params
from tiles import Wall, Empty
from utils import abspath


class Threads:
    def __init__(self, total, callback):
        self.total = total
        self.callback = callback
        self.threads = []
        self.active_thread = False

    def append(self, func):
        thread_count = len(self.threads)

        def task():
            func()
            self.total -= 1
            if not self.total:
                Thread(target=self.callback).start()
            if len(self.threads) <= thread_count+1:
                self.active_thread = False
            else:
                Thread(target=self.threads[thread_count+1]).start()

        self.threads.append(task)
        if not self.active_thread:
            self.active_thread = True
            Thread(target=self.threads[-1]).start()




def render_wall(pos, terrain, variant, parent, loader, threads):
    """Renders the wall."""
    if not any(terrain):
        return
    if terrain.count(True) == 3:
        orient = terrain.index(False)
        mod = f"concave_{3-variant}"
    elif terrain.count(True) == 2:
        orient = 3 if terrain[0] and terrain[3] else terrain.index(True)
        mod = f"wall_{2-orient%2}"
    elif terrain.count(True) == 1:
        orient = terrain.index(True)
        mod = f"convex_{variant}"

    def task():
        model = loader.loadModel(abspath(f"models/{mod}_low_flat.bam"))
        model.clearModelNodes()
        model.flattenStrong()
        model.setHpr(orient*90+180, 90, 0)
        model.reparentTo(parent)
        model.setPos(Vec3(pos)+Vec3(10, 10, 0))
        model.setScale(10.0)

    threads.append(task)


class TerrainRenderer:
    """Render the map."""

    def __init__(self):
        """Init the class."""
        self.terrain_map = [[]]
        self.geom_node = NodePath('terrain')
        self.minimap_node = NodePath('minimap')
        self.coll_node = CollisionNode('cnode')
        self.geom_builder = GeomBuilder('floor')

    def get_tile(self, i, j):
        """Get element from terrain_map."""
        try:
            return self.terrain_map[i][j]
        except IndexError:
            return Empty()

    def create_geom(self, loader):
        """Creates self.geom_node from self.terrain_map."""
        # geom_builder = GeomBuilder('floor')
        map_size = len(self.terrain_map)
        unit_size = map_params.unit_size
        start_pos = -map_size*unit_size/2
        # colors = map_params.colors

        # geom_builder.add_rect(
        #     colors.floor,
        #     start_pos, start_pos, 0,
        #     -start_pos, -start_pos, 0
        # )
        card_maker = CardMaker("cm")
        card_maker.setFrame(
            Point3(-start_pos, -start_pos, 0),
            Point3(+start_pos, -start_pos, 0),
            Point3(+start_pos, +start_pos, 0),
            Point3(-start_pos, +start_pos, 0)
        )
        card_maker.setColor(map_params.colors.floor)

        floor_node = NodePath(card_maker.generate())
        floor_node.reparentTo(self.geom_node)
        # floor_node.setHpr(0, 90, 0)
        # floor_node.setPos(0, 0, 0)
        tex = loader.loadTexture('models/floor.png')
        floor_node.setTexture(tex, 1)
        floor_node.setTexScale(TextureStage.getDefault(), map_size, map_size)

        def get(i, j):
            return isinstance(self.get_tile(i, j), Wall)

        wall_count = 0
        for i in range(map_size-1):
            for j in range(map_size-1):
                if any([get(i, j), get(i+1, j), get(i+1, j+1), get(i, j+1)]):
                    wall_count += 1

        def callback():
            self.geom_node.clearModelNodes()
            self.geom_node.flattenStrong()

        threads = Threads(wall_count, callback)

        for i in range(map_size-1):
            for j in range(map_size-1):
                current_position = (
                    start_pos+i*unit_size,
                    start_pos+j*unit_size, 0
                )
                render_wall(
                    current_position,
                    [get(i, j), get(i+1, j),
                        get(i+1, j+1), get(i, j+1)],
                    ((i+j) & 1)+1,
                    self.geom_node,
                    loader,
                    threads
                )

    def create_collision(self):
        """Creates self.coll_node from self.terrain_map."""
        map_size = len(self.terrain_map)
        start_pos = -map_size*map_params.unit_size/2

        box_size = Vec3(
            map_params.unit_size,
            map_params.unit_size,
            map_params.height
        )

        for i in range(map_size):
            for j in range(map_size):
                current_position = Point3(
                    start_pos+i*map_params.unit_size,
                    start_pos+j*map_params.unit_size,
                    0
                )
                if isinstance(self.get_tile(i, j), Wall):
                    self.coll_node.addSolid(CollisionBox(
                        current_position,
                        current_position + box_size
                    ))

    def create_minimap(self):
        """Creates self.minimap_node from self.terrain_map."""
        map_size = len(self.terrain_map)

        for i in range(map_size):
            for j in range(map_size):
                self.get_tile(i, j).generate_map((i, j)).reparentTo(
                    self.minimap_node)
