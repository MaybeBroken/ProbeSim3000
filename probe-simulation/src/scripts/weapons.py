from panda3d.core import Material, NodePath, Filename
from direct.stdpy.threading import Thread
import time as t


laserBeams = []


class _firing:
    def addLaser(self, data, hitObjectFull=None, colNode=None):
        origin = data["origin"]
        target = data["target"]
        distance = origin.getDistance(target)
        obj = self.laserModel.instanceTo(self.render)
        model = NodePath("laserBeam")
        model.reparentTo(self.render)
        obj.reparentTo(model)
        if origin.getScale() == (6, 6, 6):
            model.setScale(10)
            model.reparentTo(origin)
            model.setPos(origin.getX() + 5, origin.getY(), origin.getZ() - 4)
            model.reparentTo(self.render)
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
            threadRunningTime = 0
            while model.getDistance(ship) < fireDistance and threadRunningTime < 10 and model.getDistance(target) > 4:
                threadRunningTime += 0.001
                model.setPos(model, 0, 0.12, 0)
                t.sleep(0.001)
            model.removeNode()
            if hitObjectFull is not None:
                if hitObjectFull["health"] == 0:
                    hitObjectFull["health"] -= 1
                    colNode.set_y(-10000)
                    hitObjectFull["active"] = False
                else:
                    hitObjectFull["healthBar"]["value"] = hitObjectFull["health"]
                    hitObjectFull["health"] -= 1

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
        hitObjectFull=None,
        colNode=None,
    ):
        _firing.addLaser(
            self=self,
            data={"origin": origin, "target": target},
            hitObjectFull=hitObjectFull,
            colNode=colNode,
        )
