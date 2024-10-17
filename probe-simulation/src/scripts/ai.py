from panda3d.ai import *
from panda3d.ai import AIWorld, AICharacter
from panda3d.core import NodePath
from direct.stdpy.threading import Thread
from src.scripts.weapons import lasers

from time import monotonic, sleep
from random import randint

def behaviors(ai):
    AIbehaviors = ai.getAiBehaviors()

    class internals:
        FLEE = AIbehaviors.flee
        PURSUE = AIbehaviors.pursue
        WANDER = AIbehaviors.wander
        PAUSE = AIbehaviors.pauseAi
        REMOVE = AIbehaviors.removeAi

    return internals


def droneFire(target, origin, lastFire):
    if abs(int(abs(monotonic())) - int(abs(lastFire))) > 3:
        lasers.fire(origin=origin, target=target, destroy=False)
        print(abs(int(abs(monotonic())) - int(abs(lastFire))))
        lastFire = int(abs(monotonic()))


def fireLoop(ship, char):
    def _loop():
        while True:
            ai = char["ai"]
            node = char["mesh"]
            if ship.getDistance(node) <= 50:
                droneFire(ship, node, char["lastFire"])
            sleep(randint(2, 5))

    Thread(target=_loop).start()


def removeChar(ai, ship):
    behaviors(ai["ai"]).FLEE(ship, 100000, 100000, 0)


updateTime = 0


def update(AIworld, aiChars, ship):
    global updateTime
    updateTime += 1
    if updateTime == 8:
        updateTime = 0
        for aiChar in aiChars:
            char = aiChars[aiChar]
            ai = aiChars[aiChar]["ai"]
            node = aiChars[aiChar]["mesh"]
            if char["active"]:
                if ship.getDistance(node) > 50:
                    behaviors(ai).PURSUE(ship)
                else:
                    behaviors(ai).REMOVE("pursue")
                    node.lookAt((ship.get_x(), ship.get_y(), ship.get_z()))
                    node.setP(node.getP() + 180)
                    node.setR(node.getR() + 180)
            else:
                behaviors(ai).FLEE(ship, 10000, 10000, 1)
    AIworld.update()
