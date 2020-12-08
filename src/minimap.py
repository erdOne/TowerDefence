"""The minimap."""

import math

from panda3d.core import (
    NodePath,
    Camera,
    OrthographicLens,
    Point3D,
    StencilAttrib,
    ColorWriteAttrib,
    BitMask32
)
from panda3d.egg import (
    EggData,
    EggVertex,
    EggPolygon,
    EggVertexPool,
    loadEggData
)

import config

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


class Minimap():
    """The minimap."""

    def __init__(self, display_region):
        self.display_region = display_region
        self.display_region.setSort(20)

        self.camera = NodePath(Camera('myCam2d'))
        lens = OrthographicLens()
        lens.setFilmSize(config.minimap.size, config.minimap.size)
        lens.setNearFar(-1000, 1000)
        self.camera.node().setLens(lens)
        self.camera.setHpr(0, 90, 0)
        self.camera.node().setCameraMask(BitMask32.bit(1))

        self.node_path = NodePath('myRender2d')
        self.node_path.setDepthTest(False)
        self.node_path.setDepthWrite(False)
        self.camera.reparentTo(self.node_path)
        self.display_region.setCamera(self.camera)
        self.stencil = self.create_stencil()
        # self.stencil.hprInterval(1.5, (360, 360, 360)).loop()
        self.stencil.setTwoSided(True)

    def set_pos(self, player_pos, player_hpr):
        """Set camera position from player position."""
        self.camera.setPos(
            player_pos[0], player_pos[1], config.minimap.height)
        self.camera.setHpr(
            player_hpr[0], -90, 0
        )

    def make_circle(self, num_steps):
        data = EggData()

        vertex_pool = EggVertexPool('fan')
        data.addChild(vertex_pool)

        poly = EggPolygon()
        data.addChild(poly)

        for i in range(num_steps + 1):
            angle = 2 * math.pi * i / num_steps
            y = math.sin(angle) * config.minimap.size / 2
            x = math.cos(angle) * config.minimap.size / 2

            vertex = EggVertex()
            vertex.setPos(Point3D(x, 0, y))
            poly.addVertex(vertex_pool.addVertex(vertex))

        node = loadEggData(data)
        return node

    def create_stencil(self):
        stencil = self.node_path.attachNewNode(self.make_circle(100))
        stencil.reparentTo(self.camera)
        stencil.setPos(0, 5, 0)

        stencil.node().setAttrib(constant_one_stencil)
        stencil.hide(BitMask32.bit(0))
        stencil.node().setAttrib(ColorWriteAttrib.make(0))
        stencil.setBin('background', 0)
        stencil.setDepthWrite(0)
        # self.node_path.node().setAttrib(stencil_reader)
        return stencil
