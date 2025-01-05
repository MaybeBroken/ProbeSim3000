from panda3d.core import Material, NodePath, Filename
from direct.stdpy.threading import Thread
from src.scripts.guiUtils import fade
from direct.particles.ParticleEffect import ParticleEffect
from src.scripts.UTILS import getDistance
import time as t


laserBeams = []


class _firing:
    def addLaser(self, data, destroy):
        origin = data["origin"]
        target = data["target"]
        distance = origin.getDistance(target)
        obj = self.laserModel.instanceTo(self.render)
        model = NodePath("laserBeam")
        model.reparentTo(self.render)
        obj.reparentTo(model)
        if origin.getScale() == (6, 6, 6):
            model.setScale(12)
            model.setPos(origin.getX(), origin.getY(), origin.getZ())
        else:
            model.setScale(20)
            model.setPos(origin.getX(), origin.getY(), origin.getZ())
        model.setColor(3, 0, 0, 1)
        model.lookAt(target)
        material = Material()
        material.setEmission(
            (10, 0, 0, 1)
        )  # Increase the emission value for brightness
        obj.setMaterial(material)
        obj.setColorScale((10, 0, 0, 1))  # Set color scale to enhance brightness

        def _moveThread(model, ship):
            fireDistance = 150
            while model.getDistance(ship) < fireDistance:
                model.setPos(model, 0, 0.01, 0)
                t.sleep(0.0001)
            model.removeNode()

        Thread(target=_moveThread, name="Lsr-move", args=(model, self.ship)).start()


class lasers:
    _self = None

    def __init__(self):
        self._self = self

    def fire(
        self,
        origin=None,
        target=None,
        normal=(0, 0, 0),
        destroy=True,
    ):
        _firing.addLaser(
            self=self,
            data={"origin": origin, "target": target},
            destroy=destroy,
        )
