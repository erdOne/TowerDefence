"""The main module."""

from math import pi, sin, cos
import sys
from panda3d.core import (
    DirectionalLight,
    AmbientLight,
    MultiplexStream,
    Notify,
    Filename,
    ClockObject,
    WindowProperties,
    NodePath,
    Camera,
    OrthographicLens,
    StencilAttrib,
    loadPrcFileData,
    CardMaker,
    ColorWriteAttrib,
    BitMask32
)
# from panda3d.core import loadPrcFileData
from direct.showbase.ShowBase import ShowBase
from direct.task import Task


from maze_terrain_generator import MazeTerrainGenerator
from render.terrain_renderer import TerrainRenderer
from player import Player
from minimap import Minimap
from utils import Object
import config


loadPrcFileData("", "framebuffer-stencil #t")
# loadPrcFileData('', 'notify-level spam\ndefault-directnotify-level info')

sys.setrecursionlimit(1000000)

nout = MultiplexStream()
Notify.ptr().setOstreamPtr(nout, 0)
nout.addFile(Filename("out.txt"))

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

class MyApp:
    """The main class."""

    def __init__(self):
        """Start the app."""
        self.base = ShowBase()
        self.base.disableMouse()

        # Load the environment model.
        # self.scene = self.loader.loadModel("models/environment")
        # Reparent the model to render.
        # self.scene.reparentTo(self.render)
        # Apply scale and position transforms on the model.
        # self.scene.setScale(0.25, 0.25, 0.25)
        # self.scene.setPos(-8, 42, 0)
        self.terrain_generator = MazeTerrainGenerator(
            config.map_params.field_size,
            config.map_params.cell_size,
            config.map_params.wall_width
        )

        self.terrain_renderer = TerrainRenderer(
            config.map_params.unit_size,
            config.map_params.height,
            config.map_params.colors
        )

        height_map = self.terrain_generator.generate(config.map_params.seed)

        self.geom_node = self.base.render.attachNewNode(
            self.terrain_renderer.get_geom(height_map)
        )
        self.geom_node.hide(BitMask32.bit(1))
        self.map_geom_node = self.base.render.attachNewNode(
            self.terrain_renderer.get_geom(height_map)
        )
        self.map_geom_node.hide(BitMask32.bit(0))
        self.map_geom_node.node().setAttrib(stencil_reader)
        # self.geom_node.setTwoSided(True)
        # self.geom_node.hprInterval(1.5, (360, 360, 360)).loop()
        self.light_nodes = self.set_lights()

        # self.camera.setPos(0, 1000, 1000)
        # self.camera.lookAt(0, 0, 0)

        self.key_state = dict.fromkeys(
            Object.values(config.key_map.character), False)
        self.set_key_state_handler()
        self.paused = True
        self.toggle_pause()
        self.base.accept(config.key_map.utility.pause, self.toggle_pause)
        self.base.cam.node().setCameraMask(BitMask32.bit(0))

        self.minimap = Minimap(self.base.win.makeDisplayRegion(0.7, 1, 0.5, 1))
        self.minimap.node_path.reparentTo(self.base.render)
        # self.geom_node.node().setAttrib(stencil_reader)

        # cm = CardMaker("cardmaker")
        # cm.setFrameFullscreenQuad()
        # cn = self.base.render2d.attachNewNode(cm.generate())
        # cn.node().setAttrib(constant_one_stencil)
        # cn.node().setAttrib(ColorWriteAttrib.make(0))
        # cn.setBin('background', 0)
        # cn.setDepthWrite(0)


        self.player = Player()
        self.base.taskMgr.add(self.move_player_task, "move_player_task")

    # Define a procedure to move the camera.
    def debug(self, task):
        """Debug."""
        angle_degrees = task.time * 20.0
        angle_radians = angle_degrees * (pi / 180.0)
        self.base.camera.setPos(
            1000 * sin(angle_radians), 1000 * cos(angle_radians), 1000
        )
        self.base.camera.lookAt(0, 0, 0)
        # print(self.camera.getPos(), self.camera.getHpr())
        return Task.cont

    def set_lights(self):
        """Set up the lights."""
        dlight = DirectionalLight("directional light")
        light_node = self.base.render.attachNewNode(dlight)
        light_node.setPos(0, -5, 10)
        light_node.lookAt(0, 0, 0)
        self.base.render.setLight(light_node)

        alight = AmbientLight('ambient light')
        alight.setColor((0.5, 0.5, 0.5, 1))
        ambient_light_node = self.base.render.attachNewNode(alight)
        self.base.render.setLight(ambient_light_node)
        return light_node, ambient_light_node

    def set_key_state_handler(self):
        """Accept key and records to key_state."""

        def set_key_state(key, state):
            self.key_state[key] = state

        for key in self.key_state:
            self.base.accept(key, set_key_state, [key, True])
            self.base.accept(key+"-up", set_key_state, [key, False])

    def toggle_pause(self):
        if self.paused:
            self.paused = False
            props = WindowProperties()
            props.setCursorHidden(True)
            props.setMouseMode(WindowProperties.M_relative)
            self.base.win.requestProperties(props)
        else:
            self.paused = True
            props = WindowProperties()
            props.setCursorHidden(False)
            props.setMouseMode(WindowProperties.M_absolute)
            self.base.win.requestProperties(props)
        print("toggled pause")

    def move_player_task(self, task):
        """The task that handles player movement."""
        if not self.paused:
            if not self.base.mouseWatcherNode.hasMouse():
                self.toggle_pause()
                return Task.cont
            self.player.update_pos(
                self.key_state, ClockObject.getGlobalClock().getDt())
            self.player.update_hpr((
                self.base.mouseWatcherNode.getMouseX(),
                self.base.mouseWatcherNode.getMouseY()
            ))
            self.base.camera.setPos(self.player.pos)
            self.minimap.set_pos(self.player.pos, self.player.hpr)
            self.base.camera.setHpr(self.player.hpr)
        return Task.cont

    def run(self):
        """Run."""
        self.base.run()


app = MyApp()
app.run()
