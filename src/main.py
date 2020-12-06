"""The main module."""

from math import pi, sin, cos
import sys
from panda3d.core import (
    DirectionalLight,
    AmbientLight,
    loadPrcFile,
    MultiplexStream,
    Notify,
    Filename
)
from panda3d.core import loadPrcFileData
from direct.showbase.ShowBase import ShowBase
from direct.task import Task

from maze_terrain_generator import MazeTerrainGenerator
from render.terrain_renderer import TerrainRenderer
from utils import Object
from player import Player

# loadPrcFileData('', 'notify-level spam\ndefault-directnotify-level info')

sys.setrecursionlimit(1000000)

nout = MultiplexStream()
Notify.ptr().setOstreamPtr(nout, 0)
nout.addFile(Filename("out.txt"))

unit_size = 10
height = 20
cell_size = 3
wall_width = 1
field_size = 16
town_size = 2
seed = 10
colors = Object(
    wall=(0, 0, 1, 1),
    floor=(1, 0, 0, 1)
)


class MyApp(ShowBase):

    def __init__(self):
        ShowBase.__init__(self)
        self.disableMouse()

        # Load the environment model.
        # self.scene = self.loader.loadModel("models/environment")
        # Reparent the model to render.
        # self.scene.reparentTo(self.render)
        # Apply scale and position transforms on the model.
        # self.scene.setScale(0.25, 0.25, 0.25)
        # self.scene.setPos(-8, 42, 0)
        self.terrain_generator = MazeTerrainGenerator(
            field_size, cell_size, wall_width
        )

        self.terrain_renderer = TerrainRenderer(
            unit_size, height, colors
        )

        self.geom_node = self.render.attachNewNode(
            self.terrain_renderer.get_geom(
                self.terrain_generator.generate(seed)
            )
        )
        # self.geom_node.setTwoSided(True)
        # self.geom_node.hprInterval(1.5, (360, 360, 360)).loop()
        self.light_nodes = self.set_lights()

        self.camera.setPos(0, 1000, 1000)
        self.camera.lookAt(0, 0, 0)
        self.player = Player()
        # self.taskMgr.add(self.debug, "debugger")

    # Define a procedure to move the camera.
    def debug(self, task):
        """Debug."""
        angle_degrees = task.time * 20.0
        angle_radians = angle_degrees * (pi / 180.0)
        self.camera.setPos(
            1000 * sin(angle_radians), 1000 * cos(angle_radians), 1000
        )
        self.camera.lookAt(0, 0, 0)
        # print(self.camera.getPos(), self.camera.getHpr())
        return Task.cont

    def set_lights(self):
        """Set up the lights."""
        dlight = DirectionalLight("directional light")
        light_node = self.render.attachNewNode(dlight)
        light_node.setPos(0, -5, 10)
        light_node.lookAt(0, 0, 0)
        self.render.setLight(light_node)

        alight = AmbientLight('ambient light')
        alight.setColor((0.5, 0.5, 0.5, 0.5))
        ambient_light_node = self.render.attachNewNode(alight)
        self.render.setLight(ambient_light_node)
        return light_node, ambient_light_node


app = MyApp()
app.run()
