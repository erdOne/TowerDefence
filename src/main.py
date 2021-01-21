"""The main module."""

from math import cos, sin, pi
import sys
from random import Random

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
    Fog,
    Vec3,
    Shader,
    TextureStage,
    TextNode
)
# from panda3d.core import loadPrcFileData
from direct.showbase.ShowBase import ShowBase
from direct.task import Task
from direct.filter.CommonFilters import CommonFilters
from direct.gui.OnscreenText import OnscreenText

from player import Player
from enemy.basic import Kikiboss
from minimap import Minimap
from utils import Object, directions
from terrain.terrain import Terrain
from model import Model
from towers import Tower, ShootTower
from tiles import Floor, Empty
from selection import Selection
import config


loadPrcFileData("", "framebuffer-stencil #t")
loadPrcFileData("", "want-pstats 1")
# loadPrcFileData('', 'notify-level spam\ndefault-directnotify-level info')

# sys.setrecursionlimit(1000000)

nout = MultiplexStream()
Notify.ptr().setOstreamPtr(nout, 0)
nout.addFile(Filename("out.txt"))


class MyApp:
    """The main class."""

    def __init__(self):
        """Start the app."""
        self.base = ShowBase()
        self.base.disableMouse()

        filters = CommonFilters(self.base.win, self.base.cam)
        filters.setBloom(blend=(0, 0, 0, 1))
        self.base.render.setShaderAuto(
            BitMask32.allOn() & ~BitMask32.bit(Shader.BitAutoShaderGlow)
        )
        ts = TextureStage('ts')
        ts.setMode(TextureStage.MGlow)
        tex = self.base.loader.loadTexture('models/black.png')
        self.base.render.setTexture(ts, tex)

        self.terrain = Terrain(self.base.render, self.base.loader)

        minimap_size = 200
        self.minimap = Minimap(self.base.win.makeDisplayRegion(
            1-minimap_size/self.base.win.getProperties().getXSize(), 1,
            1-minimap_size/self.base.win.getProperties().getYSize(), 1)
        )
        self.minimap.node_path.reparentTo(self.base.render)

        # self.light_nodes =
        self.set_lights()
        self.set_fog()

        self.key_state = dict.fromkeys(
            Object.values(config.key_map.character), False)
        self.set_key_state_handler()

        self.game_state = "pause"
        self.toggle_pause()

        self.selection = Selection(self.base.loader, self.terrain.geom_node)
        self.selection_text = OnscreenText(
            mayChange=True, scale=0.07, align=TextNode.ALeft,
            pos=(0.02-self.base.getAspectRatio(), 1-0.07)
        )
        self.timer_text = OnscreenText(
            mayChange=True, scale=0.07, align=TextNode.ALeft,
            pos=(0.02-self.base.getAspectRatio(), -1+0.02+0.07)
        )

        self.enemies = set()

        self.base.accept(config.key_map.utility.pause, self.toggle_pause)
        self.base.accept(
            "q", lambda: self.selection.advance_tower(self.base.loader))
        self.base.accept("mouse1", self.player_click)
        self.base.cam.node().setCameraMask(BitMask32.bit(0))
        self.base.setBackgroundColor(*config.map_params.colors.sky)

        self.player = Player()
        self.base.taskMgr.add(lambda task: self.terrain.start_up(), "start up")
        self.mouse_pos = (0.0, 0.0)
        self.base.taskMgr.add(self.move_player_task, "move_player_task")
        self.base.taskMgr.add(self.move_enemies_task, "move_enemies_task")
        self.base.taskMgr.add(self.player_select_task, "player_select_task")
        self.base.taskMgr.add(self.tower_task, "tower_task")
        self.base.taskMgr.add(self.check_end_game, "check_end_game_task")
        rand = Random()
        rand.seed(config.map_params.seed)
        self.base.taskMgr.doMethodLater(
            1, self.clock_task, 'clock_task', extraArgs=[rand])
        self.rounds = 0
        self.coin = 0
        self.base.setFrameRateMeter(True)

    def set_fog(self):
        """Set render distance of camera."""
        fog = Fog("Scene fog")
        fog.setColor(0.7, 0.7, 0.7)
        fog.setExpDensity(0.01)
        # self.terrain.geom_node.setFog(fog)
        self.base.camLens.setFar(4000.0)
        return fog

    def set_lights(self):
        """Set up the lights."""
        light_nodes = [None]*9
        for i, dirs in zip(range(9), [0] + Object.values(directions)*2):
            dlight = DirectionalLight(f"directional light {i}")
            if i <= 4:
                dlight.setColor((0.5, 0.5, 0.5, 0.8))
            else:
                dlight.setColor((2, 2, 2, 2))
            light_nodes[i] = self.base.render.attachNewNode(dlight)
            if i == 0:
                light_nodes[i].setPos(0, 0, 1)
            else:
                light_nodes[i].setPos(*dirs, 0)
            light_nodes[i].lookAt(0, 0, 0)
            if i <= 4:
                self.base.render.setLight(light_nodes[i])
                self.terrain.terrain_node.clearLight(light_nodes[i])
            else:
                # self.terrain.terrain_node.setLight(light_nodes[i])
                pass

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
        if self.game_state == "ended":
            return
        if self.game_state == "pause":
            self.game_state = "active"
            props = WindowProperties()
            props.setCursorHidden(True)
            props.setMouseMode(WindowProperties.M_confined)
            self.base.win.requestProperties(props)
        else:
            self.game_state = "pause"
            props = WindowProperties()
            props.setCursorHidden(False)
            props.setMouseMode(WindowProperties.M_absolute)
            self.base.win.requestProperties(props)
        print("toggled pause")

    def move_player_task(self, task):  # pylint: disable=unused-argument
        """The task that handles player movement."""
        if self.game_state != "active":
            return Task.cont
        if not self.base.mouseWatcherNode.hasMouse():
            self.toggle_pause()
            return Task.cont
        self.player.update_pos(
            self.key_state, ClockObject.getGlobalClock().getDt(),
            lambda pos: self.terrain.get_tile(pos).walkable
        )
        self.mouse_pos = (
            self.mouse_pos[0] + self.base.mouseWatcherNode.getMouseX(),
            self.mouse_pos[1] + self.base.mouseWatcherNode.getMouseY(),
        )
        self.player.update_hpr(self.mouse_pos)
        self.base.win.movePointer(
            0, self.base.win.getXSize() // 2, self.base.win.getYSize() // 2
        )
        self.base.camera.setPos(self.player.pos)
        self.minimap.set_pos(self.player.pos, self.player.hpr)
        self.base.camera.setHpr(self.player.hpr)
        self.terrain.update_player_pos(tuple(self.player.pos))
        return Task.cont

    def move_enemies_task(self, task):  # pylint: disable=unused-argument
        """The task that handles enemy movement."""
        if self.game_state != "active":
            return Task.cont
        for enemy in set(self.enemies):
            if not enemy.generated:
                enemy.generate(
                    self.terrain.path_finder,
                    self.base.loader,
                    self.terrain.geom_node,
                    self.terrain.get_tile
                )
            if not enemy.check_active():
                self.enemies.remove(enemy)
                continue
            # enemy.model.setPos(self.player.pos)
            enemy.move(ClockObject.getGlobalClock().getDt())
        return Task.cont

    def tower_task(self, task):
        if self.game_state != "active":
            return Task.cont
        for tower in set(self.terrain.towers):
            if not tower.generated:
                tower.generate(
                    self.base.loader,
                    self.terrain.geom_node,
                    self.terrain.get_tile
                )
            if not tower.check_active():
                self.terrain.towers.remove(tower)
                self.terrain[tower.grid_pos] = Floor()
                continue
            tower.move(ClockObject.getGlobalClock().getDt(), self.enemies)
            tower.generate_bullet(
                self.base.loader,
                self.terrain.geom_node,
                self.terrain.get_tile
            )
        return Task.cont

    def player_select_task(self, task):
        self.selection.set_selection(
            self.player.view(self.terrain.get_tile, self.enemies)
        )
        self.selection_text.setText(self.selection.get_text())
        if self.selection.tower_class != Empty:
            self.selection.set_disable(
                self.coin < self.selection.tower_class.cost)
        return Task.cont

    def player_click(self):
        if isinstance(self.selection.select, Floor) and \
                issubclass(self.selection.tower_class, Tower) and \
                self.selection.tower_class.cost <= self.coin:
            self.coin -= self.selection.tower_class.cost
            pos = self.selection.model.getPos()
            coord_pos = (int(pos[0]//config.map_params.unit_size),
                         int(pos[1]//config.map_params.unit_size))
            self.terrain[coord_pos] = self.selection.tower_class(coord_pos)

    def spawn_enemies(self, rand):
        if self.game_state != "active":
            return Task.cont
        dsts = [tower.model.getPos().length() for tower in self.terrain.towers]
        radius = max(dsts + [0]) + 100
        num = (self.rounds + config.game.sep//2) // config.game.sep
        for _ in range(num):
            theta = rand.uniform(0, 2*pi)
            self.enemies.add(Kikiboss(Vec3(cos(theta), sin(theta), 0)*radius))
        return Task.again

    def clock_task(self, rand):
        if self.game_state != "active":
            return Task.cont
        self.rounds += 1
        self.coin += 1
        ending = "y" if self.coin <= 1 else "ies"
        self.timer_text.setText(
            f"You have {self.coin} cherr{ending}\n" +
            f"{config.game.sep - self.rounds % config.game.sep}s " +
            f"until wave {self.rounds // config.game.sep + 1}.")
        if self.rounds % config.game.sep == 0:
            return self.spawn_enemies(rand)
        return Task.again

    def check_end_game(self, task):
        if self.terrain[(0, 0)].hp <= 0:
            if self.game_state == "active":
                self.toggle_pause()
            self.game_state = "ended"
            self.terrain.geom_node.setColorScale(0.2, 0.2, 0.2, 1)
            OnscreenText(text="GAME OVER", scale=0.2, fg=(1, 0, 0, 1),
                         align=TextNode.ACenter, pos=(0, 0))
            OnscreenText(text=f"score: {self.rounds}", scale=0.07,
                         align=TextNode.ACenter, pos=(0, -.15))
            return task.done
        return task.cont

    def run(self):
        """Run."""
        self.base.run()


app = MyApp()
app.run()
