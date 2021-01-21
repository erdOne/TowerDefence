from utils import abspath, set_default
from panda3d.core import Vec3, VBase3, Shader, BitMask32

class Model:
    max_hp = 1
    def __init__(self):
        set_default(self, "pos", Vec3(0, 0, 0))
        set_default(self, "hpr", VBase3(0, 90, 0))
        set_default(self, "scale", 1.0)
        self.hp = self.max_hp
        self.generated = False
        self.model = None
        self.get_tile = None
        self.active = False

    def generate(self, loader, parent, get_tile):
        self.model = loader.loadModel(abspath(f"models/{self.name}.dae"))
        self.model.clearModelNodes()
        self.model.flattenStrong()
        self.model.reparentTo(parent)
        self.model.setHpr(self.hpr)
        self.model.setScale(self.scale)
        self.model.setPos(self.pos)
        self.active = True
        self.generated = True
        self.get_tile = get_tile
        del self.pos
        del self.hpr

    def select(self, selected):
        if not self.active:
            return
        if selected:
            self.model.setShaderAuto()
        else:
            self.model.setShaderAuto(
                BitMask32.allOn() & ~BitMask32.bit(Shader.BitAutoShaderGlow)
            )

    def hit(self, damage):
        self.hp -= damage

    def check_active(self):
        if self.hp <= 0:
            self.model.removeNode()
            self.active = False
        return self.hp > 0

    def get_text(self):
        return f"{self.name}\nHP: {self.hp:.{2}f}/{self.max_hp}"

        # print(self.model.findAllMatches("**/*"))
        # self.model.clearModelNodes()
        # self.model.flattenStrong()
