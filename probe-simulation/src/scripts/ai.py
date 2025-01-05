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
    lasers.fire(origin=origin, target=totalTarget, destroy=False)


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


def update(AIworld, aiChars, ship):
    while True:
        for char in aiChars:
            ai = char["ai"]
            node = char["mesh"]
            if char["active"]:
                if ship.getDistance(node) > 150:
                    behaviors(ai).PURSUE(ship)
                else:
                    behaviors(ai).REMOVE("pursue")
                    node.lookAt((ship.get_x(), ship.get_y(), ship.get_z()))
                    node.setP(node.getP() + 180)
                    node.setR(node.getR() + 180)
                    if shipHealth["value"] > 0 and randint(0, 100) < 5:
                        fireLoop(ship, char, self=aiChars)
            else:
                behaviors(ai).FLEE(ship, 10000, 10000, 1)
        sleep(0.25)
