from maze_terrain_generator import MazeTerrainGenerator
from render.terrain_renderer import TerrainRenderer
from math import pi, sin, cos
from panda3d.core import GeomNode, DirectionalLight, PointLight, AmbientLight, Spotlight, PerspectiveLens, loadPrcFile, MultiplexStream, Notify, Filename
from direct.showbase.ShowBase import ShowBase
from direct.task import Task
from utils import Object
import sys
from panda3d.core import loadPrcFileData

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
        self.scene = self.loader.loadModel("models/environment")
        # Reparent the model to render.
        # self.scene.reparentTo(self.render)
        # Apply scale and position transforms on the model.
        # self.scene.setScale(0.25, 0.25, 0.25)
        # self.scene.setPos(-8, 42, 0)
        terrain_generator = MazeTerrainGenerator(
            field_size, cell_size, wall_width
        )

        self.terrain_renderer = TerrainRenderer(
            unit_size, height, colors
        )

        self.geom_node = self.render.attachNewNode(
            self.terrain_renderer.get_geom(terrain_generator.generate(seed))
        )
        print(self.geom_node.getNode(0))
        self.geom_node.setTwoSided(True)
        # self.geom_node.hprInterval(1.5, (360, 360, 360)).loop()

        dlight = DirectionalLight("directional light")
        self.light_node = self.render.attachNewNode(dlight)
        self.light_node.setPos(0, -5, 10)
        self.light_node.lookAt(0, 0, 0)
        self.render.setLight(self.light_node)

        alight = AmbientLight('ambient light')
        alight.setColor((0.5, 0.5, 0.5, 0.5))
        self.ambient_light_node = self.render.attachNewNode(alight)
        self.render.setLight(self.ambient_light_node)

        self.camera.setPos(0, 1000, 1000)
        self.camera.lookAt(0, 0, 0)
        # self.taskMgr.add(self.debug, "debugger")

    # Define a procedure to move the camera.
    def debug(self, task):
        angleDegrees = task.time * 20.0
        angleRadians = angleDegrees * (pi / 180.0)
        self.camera.setPos(1000 * sin(angleRadians), 1000 * cos(angleRadians), 1000)
        self.camera.lookAt(0, 0, 0)
        # print(self.camera.getPos(), self.camera.getHpr())
        return Task.cont


app = MyApp()
app.run()
