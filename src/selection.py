from panda3d.core import (
    CardMaker,
    Point3,
    NodePath,
    TextureStage,
    Vec3,
    TransparencyAttrib
)
from config import map_params
from model import Model
from tiles import Floor, Empty
from utils import abspath

from towers import WallTower, ShootTower


class Selection:
    towers = [Empty, WallTower, ShootTower]

    def __init__(self, loader, parent):
        card_maker = CardMaker("cm")
        pos = map_params.unit_size // 2
        card_maker.setFrame(
            Point3(-pos, -pos, 0),
            Point3(+pos, -pos, 0),
            Point3(+pos, +pos, 0),
            Point3(-pos, +pos, 0)
        )
        card_maker.setColor(map_params.colors.floor)

        self.model = NodePath(card_maker.generate())
        self.model.reparentTo(parent)
        self.model.setPos(Vec3(0, 0, -1))
        # floor_node.setHpr(0, 90, 0)
        # floor_node.setPos(0, 0, 0)
        tex = loader.loadTexture('models/floor.png')
        self.model.setTexture(tex, 1)
        self.model.setTexScale(
            TextureStage.getDefault(),
            1, 1
        )
        self.model.setShaderAuto()

        self.select = None
        self.tower = None
        self.tower_class = Empty
        self.tower_no = 0

    def remove_selection(self):
        if self.select is None:
            return
        if isinstance(self.select, Model):
            self.select.select(False)
        if isinstance(self.select, Floor):
            self.model.setPos(0, 0, -1)

    def set_selection(self, item):
        # print(item)
        if item[0] == self.select:
            return
        self.remove_selection()
        self.select = item[0]
        if self.select is None:
            return
        if isinstance(self.select, Model):
            self.select.select(True)
        if isinstance(self.select, Floor):
            unit = map_params.unit_size
            self.model.setPos(
                (item[1][0]+unit//2)//unit*unit,
                (item[1][1]+unit//2)//unit*unit,
                0.01
            )
            if self.tower:
                self.tower.show()
        elif self.tower:
            self.tower.hide()

    def remove_tower(self):
        if self.tower:
            self.tower.removeNode()
        self.tower_class = Empty

    def set_tower(self, loader, tower_class):
        self.remove_tower()
        self.tower = loader.loadModel(
            abspath(f"models/{tower_class.name}.dae")
        )
        self.tower.reparentTo(self.model)
        self.tower.setHpr(0, 90, 0)
        self.tower.setTransparency(TransparencyAttrib.MAlpha)
        self.tower.setAlphaScale(0.5)
        self.tower.setScale(tower_class.scale)
        self.tower_class = tower_class

    def get_text(self):
        if isinstance(self.select, Model):
            return self.select.get_text()
        return ""

    def set_disable(self, disabled):
        if disabled:
            self.tower.setColorScale(1, 0.5, 0.5, 0.5)
        else:
            self.tower.clearColorScale()

    def advance_tower(self, loader):
        self.tower_no += 1
        self.tower_no %= len(self.towers)
        if self.towers[self.tower_no] == Empty:
            self.remove_tower()
        else:
            self.set_tower(loader, self.towers[self.tower_no])
