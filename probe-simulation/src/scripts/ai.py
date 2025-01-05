from panda3d.ai import *
from panda3d.core import NodePath
from direct.stdpy.threading import Thread
from src.scripts.weapons import lasers

from time import monotonic, sleep
from random import randint

shipHealth = None


def setupShipHealth(_shipHealth):
    global shipHealth
    shipHealth = _shipHealth


def behaviors(ai):
    AIbehaviors = ai.getAiBehaviors()

    class internals:
        FLEE = AIbehaviors.flee
        PURSUE = AIbehaviors.pursue
        WANDER = AIbehaviors.wander
        PAUSE = AIbehaviors.pauseAi
        REMOVE = AIbehaviors.removeAi

    return internals


def droneFire(target, origin, self):
    global shipHealth
    newTarget = NodePath("newDroneTarget")
    newTarget.setPos(target.getPos())
    sleep(0.25)
    if target.getDistance(newTarget) > 8:
        totalTarget = newTarget
    else:
        totalTarget = target
        try:
            shipHealth["value"] -= 1
        except:
            ...
    lasers.fire(self=self, origin=origin, target=totalTarget)


def fireLoop(ship, char, self):
    node = char["mesh"]
    if ship.getDistance(node) <= 50:
        droneFire(ship, node, self=self)


def removeChar(ai, ship):
    behaviors(ai["ai"]).FLEE(ship, 100000, 100000, 0)


updateTime = 0


def pauseAll(aiChars):
    for char in aiChars:
        ai = char["ai"]
        behaviors(ai).REMOVE("pursue")


def resumeAll(aiChars, target):
    for char in aiChars:
        ai = char["ai"]
        behaviors(ai).PURSUE(target)


def destroyChar(aiChars, char: dict, waitTime: float):
    def _internal():
        sleep(waitTime)
        char["active"] = False
        char["mesh"].hide()
        aiChars.remove(char)

    return Thread(target=_internal, name="destroyChar").start()


def update(aiChars, ship, self):
    while True:
        for char in aiChars:
            ai = char["ai"]
            node = char["mesh"]
            if char["active"]:
                if ship.getDistance(node) > 400:
                    behaviors(ai).PURSUE(ship)
                else:
                    behaviors(ai).REMOVE("pursue")
                    node.lookAt((ship.get_x(), ship.get_y(), ship.get_z()))
                    node.setP(node.getP() + 180)
                    node.setR(node.getR() + 180)
                    if shipHealth["value"] > 0 and randint(0, 100) < 20:
                        fireLoop(ship=ship, char=char, self=self)
            else:
                behaviors(ai).FLEE(ship, 10000, 10000, 1)
                destroyChar(aiChars=aiChars, char=char, waitTime=0)
        sleep(0.08)
