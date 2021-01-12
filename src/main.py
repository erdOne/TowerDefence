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
    loadPrcFileData,
    BitMask32,
    Fog
)
# from panda3d.core import loadPrcFileData
from direct.showbase.ShowBase import ShowBase
from direct.task import Task

from player import Player
from minimap import Minimap
from utils import Object, directions
from terrain.terrain import Terrain
import config


loadPrcFileData("", "framebuffer-stencil #t")
loadPrcFileData("", "want-pstats 1")
# loadPrcFileData('', 'notify-level spam\ndefault-directnotify-level info')

sys.setrecursionlimit(1000000)

nout = MultiplexStream()
Notify.ptr().setOstreamPtr(nout, 0)
nout.addFile(Filename("out.txt"))


class MyApp:
    """The main class."""

    def __init__(self):
        """Start the app."""
        self.base = ShowBase()
        self.base.disableMouse()

        self.terrain = Terrain(self.base.render, self.base.loader)

        minimap_size = 200
        self.minimap = Minimap(self.base.win.makeDisplayRegion(
            1-minimap_size/self.base.win.getProperties().getXSize(), 1,
            1-minimap_size/self.base.win.getProperties().getYSize(), 1)
        )
        self.minimap.node_path.reparentTo(self.base.render)

        self.light_nodes = self.set_lights()
        self.fog = self.set_fog()

        self.key_state = dict.fromkeys(
            Object.values(config.key_map.character), False)
        self.set_key_state_handler()
        self.paused = True
        self.toggle_pause()
        self.base.accept(config.key_map.utility.pause, self.toggle_pause)
        self.base.accept("q", self.debug)
        self.base.cam.node().setCameraMask(BitMask32.bit(0))

        self.player = Player()
        self.base.taskMgr.add(lambda task: self.move_player_task(), "move_player_task")
        # self.base.taskMgr.add(self.terrain.start_up, "move_player_task")
        self.base.setFrameRateMeter(True)

    # Define a procedure to move the camera.
    def debug(self):
        """Debug."""
        # angle_degrees = task.time * 20.0
        # angle_radians = angle_degrees * (pi / 180.0)
        # self.base.camera.setPos(
        #     1000 * sin(angle_radians), 1000 * cos(angle_radians), 1000
        # )
        # self.base.camera.lookAt(0, 0, 0)
        # # print(self.camera.getPos(), self.camera.getHpr())
        print("debug")
        self.base.render.analyze()

    def set_fog(self):
        """Set render distance of camera."""
        fog = Fog("Scene fog")
        fog.setColor(0.7, 0.7, 0.7)
        fog.setExpDensity(0.01)
        self.terrain.geom_node.setFog(fog)
        self.base.camLens.setFar(300.0)
        return fog

    def set_lights(self):
        """Set up the lights."""
        light_nodes = [None]*5
        for i, dirs in zip(range(5), Object.values(directions) + [0]):
            dlight = DirectionalLight(f"directional light {i}")
            if i == 4:
                dlight.setColor((0.5, 0.5, 0.5, 0.5))
            else:
                dlight.setColor((2, 2, 2, 2))
            light_nodes[i] = self.base.render.attachNewNode(dlight)
            if i == 4:
                light_nodes[i].setPos(0, 0, 1)
            else:
                light_nodes[i].setPos(dirs[0]*5, dirs[1]*5, 0)
            light_nodes[i].lookAt(0, 0, 0)
            self.base.render.setLight(light_nodes[i])

        alight = AmbientLight('ambient light')
        alight.setColor((0.3, 0.3, 0.3, 1))
        ambient_light_node = self.base.render.attachNewNode(alight)
        self.base.render.setLight(ambient_light_node)
        return light_nodes, ambient_light_node

    def set_key_state_handler(self):
        """Accept key and records to key_state."""

        def set_key_state(key, state):
            self.key_state[key] = state

        for key in self.key_state:
            self.base.accept(key, set_key_state, [key, True])
            self.base.accept(key+"-up", set_key_state, [key, False])

    def toggle_pause(self):
        """Toggle pause."""
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

    def move_player_task(self, task):  # pylint: disable=unused-argument
        """The task that handles player movement."""
        if not self.paused:
            if not self.base.mouseWatcherNode.hasMouse():
                self.toggle_pause()
                return Task.cont
            self.player.update_pos(
                self.key_state, ClockObject.getGlobalClock().getDt(),
                lambda pos: self.terrain.get_tile(pos).walkable
            )
            self.player.update_hpr((
                self.base.mouseWatcherNode.getMouseX(),
                self.base.mouseWatcherNode.getMouseY()
            ))
            self.base.camera.setPos(self.player.pos)
            self.minimap.set_pos(self.player.pos, self.player.hpr)
            self.base.camera.setHpr(self.player.hpr)
            self.terrain.update_player_pos(tuple(self.player.pos))
        return Task.cont

    def run(self):
        """Run."""
        self.base.run()


app = MyApp()
app.run()
