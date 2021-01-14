"""Class of the whole terrain."""

from sortedcontainers import SortedDict
from panda3d.core import NodePath, BitMask32, StencilAttrib

from terrain.chunk import Chunk
from terrain.pathfinder import PathFinder
from config import map_params
from tiles import Empty, Proxy, Center, Tower

constant_one_stencil = StencilAttrib.make(
    1, StencilAttrib.SCFAlways,
    StencilAttrib.SOZero, StencilAttrib.SOReplace,
    StencilAttrib.SOReplace, 1, 0, 1
)

stencil_reader = StencilAttrib.make(
    1, StencilAttrib.SCFEqual,
    StencilAttrib.SOKeep, StencilAttrib.SOKeep,
    StencilAttrib.SOKeep, 1, 1, 0
)


class Terrain:
    """The class holding the whole map."""

    def __init__(self, render, loader):
        self.chunk_map = SortedDict()
        self.geom_node = NodePath("terrain")
        self.geom_node.reparentTo(render)
        self.geom_node.hide(BitMask32.bit(1))
        self.terrain_node = NodePath("ground")
        self.terrain_node.reparentTo(self.geom_node)

        self.minimap_node = NodePath("minimap")
        self.minimap_node.reparentTo(render)
        self.minimap_node.hide(BitMask32.bit(0))
        self.minimap_node.node().setAttrib(stencil_reader)

        self.loader = loader
        self.chunk_size = map_params.unit_size * (
            (map_params.field_size*map_params.cell_size
             + (map_params.field_size-1)*map_params.wall_width)
        )
        self.active_chunks = set()
        self.path_finder = PathFinder(self.get_tile)

        self.towers = set()

    def generate(self, pos):
        """Generates everything."""
        print(f"generating {pos}")
        assert pos not in self.chunk_map
        new_chunk = Chunk(pos)
        self.chunk_map[pos] = new_chunk
        new_chunk.generate(self.loader)
        new_chunk.geom_node.reparentTo(self.terrain_node)
        new_chunk.geom_node.setPos(
            (pos[0]*self.chunk_size, pos[1]*self.chunk_size, 0))
        new_chunk.minimap_node.reparentTo(self.minimap_node)
        new_chunk.minimap_node.setPos(
            (pos[0]*self.chunk_size, pos[1]*self.chunk_size, 0))
        print(f"generated {pos}")

    def get_chunk_no(self, pos):
        return (
            (int(pos[0]) + self.chunk_size//2) // self.chunk_size,
            (int(pos[1]) + self.chunk_size//2) // self.chunk_size
        )

    def get_chunk_coord(self, pos):
        return (
            (int(pos[0]) + self.chunk_size//2)
                % self.chunk_size // map_params.unit_size,
            (int(pos[1]) + self.chunk_size//2)
                % self.chunk_size // map_params.unit_size
        )

    def show(self, chunk_no):
        """Show a certian chunk."""
        if chunk_no not in self.chunk_map:
            self.generate(chunk_no)
        self.active_chunks.add(chunk_no)
        self.chunk_map[chunk_no].show()

    def update_player_pos(self, pos):
        """Check if position of player is not generated."""
        new_set = set()

        pos = (int(pos[0]) // self.chunk_size, int(pos[1]) // self.chunk_size)
        for i in range(pos[0], pos[0]+2):
            for j in range(pos[1], pos[1]+2):
                new_set.add((i, j))

        for chunk_no in self.active_chunks - new_set:
            self.active_chunks.remove(chunk_no)
            self.chunk_map[chunk_no].hide()

        # for chunk_no in new_set - self.active_chunks:
        #     self.show(chunk_no)

    def get_tile(self, pos):
        if self.get_chunk_no(pos) not in self.chunk_map:
            return Empty()
        return self.chunk_map[
            self.get_chunk_no(pos)
        ].get_tile(*self.get_chunk_coord(pos))

    def start_up(self):
        """Generate the first nine chunks."""
        self.show((0, 0))
        self[(0, 0)] = Center(self.loader, self.geom_node, (0, 0))
        self[(4, 4)] = Tower(self.loader, self.geom_node, (4, 4))
        # for i in range(-1, 2):
        #     for j in range(-1, 2):
        #         self.show((i, j))

    def __getitem__(self, item):
        return self.get_tile(
            (item[0] * map_params.unit_size, item[1] * map_params.unit_size)
        )

    def set_tile(self, item, value):
        item = item[0] * map_params.unit_size, item[1] * map_params.unit_size
        if self.get_chunk_no(item) not in self.chunk_map:
            raise IndexError
        self.chunk_map[
            self.get_chunk_no(item)
        ].set_tile(self.get_chunk_coord(item), value)

    def __setitem__(self, item, value):
        if isinstance(value, Tower):
            self.towers.add(value)
        for i in range(-(value.width//2), (value.width+1)//2):
            for j in range(-(value.width//2), (value.width+1)//2):
                # print(i, j)
                self.set_tile(
                    (item[0]+i, item[0]+j),
                    value
                )
