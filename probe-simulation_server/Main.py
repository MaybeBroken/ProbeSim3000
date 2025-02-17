from math import *
from random import *
import time as t
import sys
import os

from screeninfo import get_monitors
from direct.showbase.ShowBase import ShowBase
from panda3d.core import *
from panda3d.core import (
    TransparencyAttrib,
    DirectionalLight,
    AmbientLight,
    loadPrcFile,
    ConfigVariableString,
    Vec3,
    MovieTexture,
    CardMaker,
    NodePath,
    LineSegs,
)

try:
    import direct.stdpy.threading as thread
    from direct.gui.DirectGui import *
    import src.scripts.server as server
    import src.scripts.vars as Wvars
    import src.scripts.physics as physics
except:
    print(
        "\nFailed to import required modules, your installation may be corrupt. \nContact the Developer for assistance at \033[92m@_maybebroken\033[0m on Discord or \033[96m@MaybeBroken\033[0m on Github\n"
    )
    exit(1)


monitor = get_monitors()
spriteSheet: dict = {"menuBackground": None}


loadPrcFile("src/settings.prc")
if Wvars.winMode == "full-win":
    ConfigVariableString(
        "win-size", str(monitor[0].width) + " " + str(monitor[0].height)
    ).setValue(str(monitor[0].width) + " " + str(monitor[0].height))
    ConfigVariableString("fullscreen", "false").setValue("false")
    ConfigVariableString("undecorated", "true").setValue("true")

if Wvars.winMode == "full":
    ConfigVariableString(
        "win-size", str(Wvars.resolution[0]) + " " + str(Wvars.resolution[1])
    ).setValue(str(Wvars.resolution[0]) + " " + str(Wvars.resolution[1]))
    ConfigVariableString("fullscreen", "true").setValue("true")
    ConfigVariableString("undecorated", "true").setValue("true")

if Wvars.winMode == "win":
    ConfigVariableString(
        "win-size",
        str(int(monitor[0].width / 2) + int(monitor[0].width / 4))
        + " "
        + str(int(monitor[0].height / 2) + int(monitor[0].height / 4)),
    ).setValue(
        str(int(monitor[0].width / 2) + int(monitor[0].width / 4))
        + " "
        + str(int(monitor[0].height / 2) + int(monitor[0].height / 4)),
    )
    ConfigVariableString("fullscreen", "false").setValue("false")
    ConfigVariableString("undecorated", "false").setValue("false")


def degToRad(degrees):
    return degrees * (pi / 180.0)


# This class controls most of the flight director management


class Main(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)
        self.backfaceCullingOn()
        self.disableMouse()
        physics.physicsMgr.enable(physics.physicsMgr, gravity=(0, 0, 0))

        # do setup tasks
        # ...

        self.setupControls()
        self.setupLights()
        self.loadInitialTextures()
        Wvars.cursorLock = False

        self.startGui()
        # end of setup tasks

    def update(self, task):
        try:
            result = task.cont
            self.dronesReminingText.setText(f"Drones remaining: {server.droneCount}")
            if server.cliConnected:
                self.ship.setPos(
                    server.nodePositions["ship"][0] / 100,
                    server.nodePositions["ship"][1] / 100,
                    server.nodePositions["ship"][2] / 100,
                )
                self.CamPosNode.setPos(self.ship.getPos())

                self.shipSegNP.removeNode()

                self.shipSeg.reset()
                self.shipSeg.setColor(self.ship.getColor())
                self.shipSeg.moveTo(self.ship.getPos())
                self.shipSeg.setColor(1, 1, 1, 1)
                self.shipSeg.drawTo(self.ship.getX(), self.ship.getY(), -10)

                self.shipSegNode = self.shipSeg.create(False)
                self.shipSegNP = self.renderNode.attachNewNode(self.shipSegNode)

                self.relaunchButton.show()
                self.noClientConnectedText.hide()
                self.renderNode.show()
                self.noClientConnectedText.hide()
                if server.cliDead:
                    self.relaunchButton["image"] = spriteSheet["respawnReady"]
                    self.destroyButton.hide()
                else:
                    self.relaunchButton["image"] = spriteSheet["respawnDefault"]
                # do all systems updates
                if server.cliKill:
                    self.destroyButton.hide()
                else:
                    self.destroyButton.show()
                # if self.lastDroneAmount != server.droneCount:
                #     for node in self.droneNodePath.getChildren():
                #         node.removeNode()
                #     for dronePos in server.nodePositions["drones"]:
                #         droneNode = NodePath("droneNode")
                #         droneMesh = self.cube.instanceTo(self.droneNodePath)
                #         droneMesh.reparentTo(droneNode)
                #         droneNode.setScale(2)
                #         droneNode.setColor(1, 0.3, 0.2, 1)
                #         droneNode.setPos(
                #             dronePos[0] / 100, dronePos[1] / 100, dronePos[2] / 100
                #         )
                # else:
                #     for dronePos, node in (
                #         server.nodePositions["drones"],
                #         self.droneNodePath.getChildren(),
                #     ):
                #         node.setPos(
                #             dronePos[0] / 1000, dronePos[1] / 1000, dronePos[2] / 1000
                #         )
                # self.lastDroneAmount = server.droneCount
            else:
                self.renderNode.hide()
                self.renderNode.hide()
                self.relaunchButton.hide()
                self.destroyButton.hide()
                self.noClientConnectedText.show()
                self.relaunchButton["image"] = spriteSheet["respawnDefault"]
                server.droneCount = " -- "
        except:
            ...
        return result

    def setupControls(self):
        self.lastMouseX = 0
        self.lastMouseY = 0
        self.keyMap = {
            "forward": False,
            "backward": False,
            "left": False,
            "right": False,
            "up": False,
            "down": False,
            "primary": False,
            "secondary": False,
        }

        self.accept("escape", self.doNothing)
        self.accept("mouse1", self.doNothing)
        self.accept("mouse1-up", self.doNothing)
        self.accept("mouse3", self.doNothing)
        self.accept("q", sys.exit)
        self.accept("w", self.updateKeyMap, ["forward", True])
        self.accept("w-up", self.updateKeyMap, ["forward", False])
        self.accept("a", self.updateKeyMap, ["left", True])
        self.accept("a-up", self.updateKeyMap, ["left", False])
        self.accept("s", self.updateKeyMap, ["backward", True])
        self.accept("s-up", self.updateKeyMap, ["backward", False])
        self.accept("d", self.updateKeyMap, ["right", True])
        self.accept("d-up", self.updateKeyMap, ["right", False])
        self.accept("space", self.updateKeyMap, ["up", True])
        self.accept("space-up", self.updateKeyMap, ["up", False])
        self.accept("lshift", self.updateKeyMap, ["down", True])
        self.accept("lshift-up", self.updateKeyMap, ["down", False])

    def updateKeyMap(self, key, value):
        self.keyMap[key] = value

    def doNothing(self):
        return None

    def loadInitialTextures(self):
        global spriteSheet
        spriteSheet["menuBackground"] = self.loader.loadTexture(
            "src/textures/raw/menuBackground.png"
        )
        spriteSheet["startButton"] = self.loader.loadTexture(
            "src/textures/raw/startButton.png"
        )
        spriteSheet["exitButton"] = self.loader.loadTexture(
            "src/textures/raw/exitButton.png"
        )
        spriteSheet["voyagerLogo"] = self.loader.loadTexture(
            texturePath="src/textures/raw/Voyager_Logo.png",
        )
        spriteSheet["flightDirector"] = self.loader.loadTexture(
            texturePath="src/textures/raw/flightDirectorTile.png",
        )
        spriteSheet["respawnDefault"] = self.loader.loadTexture(
            texturePath="src/textures/raw/respawn_default.png",
        )
        spriteSheet["respawnReady"] = self.loader.loadTexture(
            texturePath="src/textures/raw/respawn_ready.png",
        )
        spriteSheet["destroy"] = self.loader.loadTexture(
            texturePath="src/textures/raw/destroy.png",
        )

    def loadAllTextures(self):
        spriteSheet["play_blue"] = self.loader.load_texture(
            "src/textures/raw/icon_play_blue.png"
        )
        spriteSheet["X_blue"] = self.loader.load_texture(
            "src/textures/raw/icon_X_blue.png"
        )

    def load(self):
        self.loadAllTextures()
        self.voyager = self.loader.loadModel("src/models/voyager/voyager.bam")
        self.worldMapObject = self.loader.loadModel("src/models/plane/mesh.bam")
        self.cube = self.loader.loadModel("src/models/cube/cube.egg")
        t.sleep(1)
        thread.Thread(
            target=self.fadeOutGuiElement_ThreadedOnly,
            kwargs={
                "element": self.guiFrame,
                "timeToFade": 80,
                "execBeforeOrAfter": "After",
                "target": self.alertReady,
            },
        ).start()

    def setupLights(self):
        ambientLight = AmbientLight("ambientLight")
        ambientLight.setColor((0.5, 0.5, 0.5, 1))
        self.render.setLight(self.render.attachNewNode(ambientLight))

        directionalLight = DirectionalLight("directionalLight")
        directionalLight.setDirection(Vec3(0.3, 0.5, -0.7))
        directionalLight.setColor((1, 1, 1, 1))
        self.render.setLight(self.render.attachNewNode(directionalLight))

    def startGui(self):
        self.guiFrame = DirectFrame(parent=self.aspect2d)
        self.setupIntroMenu()

    tex = {}

    def startPlayer(self, media_file, name):
        self.tex[name] = MovieTexture(name)
        self.tex[name].setLoop(True)
        success = self.tex[name].read(media_file)
        try:
            assert success, "Failed to load video!"
        except AssertionError as e:
            print(e)
            return None
        self.tex[name].play()  # Start playing immediately after loading
        cm = CardMaker("fullscreenCard")
        cm.setFrameFullscreenQuad()
        cm.setUvRange(self.tex[name])
        card = NodePath(cm.generate())
        card.reparentTo(self.render2d)
        card.setPos(0, 0, 0)
        card.setTransparency(TransparencyAttrib.MAlpha)
        card.setTexture(self.tex[name])
        return card

    def stopTex(self, name):
        self.tex[name].stop()

    def playTex(self, name):
        self.tex[name].play()

    def spinImageTask(self, task):
        self.startupMenuBackgroundImage2.setH(
            self.startupMenuBackgroundImage2.getH() + 0.5
        )
        return task.cont

    def setupIntroMenu(self):
        self.setBackgroundColor(r=0, g=0, b=0, a=1)
        self.startupMenuFrame = DirectFrame(parent=self.guiFrame)
        self.startupMenuFrame.set_transparency(1)

        self.startupMenuBackgroundImage1 = self.startPlayer(
            "src/movies/GUI/menu.mp4", "menuBackground"
        )
        self.startupMenuBackgroundImage1.setBin("fixed", 1)

        self.startupMenuBackgroundImage2 = OnscreenImage(
            parent=self.startupMenuFrame,
            image=spriteSheet["voyagerLogo"],
            scale=0.25,
            pos=(0.825 * monitor[0].width / monitor[0].height, 0, -0.725),
        )
        self.spinTask = self.taskMgr.add(self.spinImageTask, "spinImageTask")

        self.startupMenuBackgroundImage3 = OnscreenImage(
            parent=self.startupMenuFrame,
            image=spriteSheet["flightDirector"],
            scale=(0.05 * (569 / 127), 1, 0.05),
            pos=(-0.86 * monitor[0].width / monitor[0].height, 0, 0.95),
        )

        self.startupMenuStartButton = DirectButton(
            parent=self.startupMenuFrame,
            pos=(-0.7 * monitor[0].width / monitor[0].height, 0, 0.6),
            scale=(0.12 * (553 / 194), 1, 0.12),
            relief=None,
            image=spriteSheet["startButton"],
            geom=None,
            frameColor=(1.0, 1.0, 1.0, 0.0),
            command=thread.Thread(
                target=self.fadeOutGuiElement_ThreadedOnly,
                args=[
                    self.startupMenuFrame,
                    25,
                    "Before",
                    self.setupLoaderFromMenu,
                ],
            ).start,
        )

        self.startupMenuQuitButton = DirectButton(
            parent=self.startupMenuFrame,
            pos=(-0.7 * monitor[0].width / monitor[0].height, 0, 0.3),
            scale=(0.12 * (553 / 194), 1, 0.12),
            relief=DGG.FLAT,
            image=spriteSheet["exitButton"],
            geom=None,
            frameColor=(1.0, 1.0, 1.0, 0.0),
            command=sys.exit,
        )

        self.startupMenuCreditsText = OnscreenText(
            parent=self.startupMenuFrame,
            text="Programmed by David Sponseller\nVersion 1.4",
            pos=(-0.7 * monitor[0].width / monitor[0].height, -0.9),
            scale=0.0475,
            fg=(0.5, 7, 7, 0.75),
        )

    def setupLoaderFromMenu(self):
        # self.stopTex("menuBackground")
        self.startupLoaderFrame = DirectFrame(
            parent=self.guiFrame,
        )
        self.startupLoaderFrame.set_transparency(1)

        self.startupLoaderVoyagerLogo = OnscreenImage(
            parent=self.startupLoaderFrame,
            image=spriteSheet["voyagerLogo"],
            scale=0.5,
            pos=(0, 0, 0.25),
        )

        self.startupLoaderLoadingText = OnscreenText(
            "Loading...",
            pos=(0 * monitor[0].width / monitor[0].height, -0.5),
            scale=0.05,
            parent=self.startupLoaderFrame,
            fg=(0.6, 1, 1, 1),
        )
        thread.Thread(
            target=self.fadeInGuiElement_ThreadedOnly,
            args=[
                self.startupLoaderFrame,
                50,
            ],
        ).start()
        self.readyContinue = 30
        self.continueCount = 0
        self.taskMgr.add(self.setupMainframe)

    def fadeOutGuiElement_ThreadedOnly(
        self,
        element,
        timeToFade,
        execBeforeOrAfter=None,
        target=None,
        args=(),
        kwArgs={},
    ):
        element.set_transparency(1)
        if execBeforeOrAfter == "Before":
            if len(args) > 0:
                target(*args)
            else:
                target(**kwArgs)
        for i in range(timeToFade):
            val = 1 - (1 / timeToFade) * (i + 1)
            try:
                element.setAlphaScale(val)
            except:
                None
            t.sleep(0.01)
        element.hide()
        if execBeforeOrAfter == "After":
            if len(args) > 0:
                target(*args)
            else:
                target(**kwArgs)

    def fadeInGuiElement_ThreadedOnly(
        self,
        element,
        timeToFade,
        execBeforeOrAfter=None,
        target=None,
        args=(),
        kwArgs={},
    ):
        element.show()
        element.set_transparency(1)
        if execBeforeOrAfter == "Before":
            if len(args) > 0:
                target(*args)
            else:
                target(**kwArgs)

        for i in range(timeToFade):
            val = abs(0 - (1 / timeToFade) * (i + 1))
            element.setAlphaScale(val)
            t.sleep(0.01)
        if execBeforeOrAfter == "After":
            if len(args) > 0:
                target(*args)
            else:
                target(**kwArgs)

    def showGuiFrame(self):
        self.guiFrame.show()

    def hideGuiFrame(self):
        self.guiFrame.hide()

    def setupMainframe(self, task):
        if self.readyContinue >= self.continueCount:
            thread.Thread(target=server.startServer, args=[8765, "dataServer"]).start()
            thread.Thread(target=self.load).start()
            self.readyLoad = False
            self.taskMgr.add(self.awaitStartTask)
        else:
            self.continueCount += 1
            return task.cont

    def alertReady(self):
        self.readyLoad = True

    def awaitStartTask(self, task):
        if self.readyLoad:
            self.loadFinal()
        else:
            return task.cont

    def loadFinal(self):
        for node in self.guiFrame.getChildren():
            node.removeNode()

        def setReady():
            if server.cliDead:
                server.sendRespawn = True
                server.cliKill = False

        def destroyProbe():
            server.sendRespawn = False
            server.cliKill = True

        self.startupMenuBackgroundImage1.hide()

        self.relaunchButton = DirectButton(
            parent=self.guiFrame,
            pos=(-0.0 * monitor[0].width / monitor[0].height, 0, 0.8),
            scale=(0.12 * (1005 / 404), 1, 0.12),
            relief=DGG.FLAT,
            image=spriteSheet["respawnDefault"],
            geom=None,
            frameColor=(1.0, 1.0, 1.0, 0.0),
            command=setReady,
        )
        self.destroyButton = DirectButton(
            parent=self.guiFrame,
            pos=(-0.5 * monitor[0].width / monitor[0].height, 0, 0.8),
            scale=(0.12 * (1005 / 404), 1, 0.12),
            relief=DGG.FLAT,
            image=spriteSheet["destroy"],
            geom=None,
            frameColor=(1.0, 1.0, 1.0, 0.0),
            command=destroyProbe,
        )
        self.destroyButton.hide()
        self.CreditsText = OnscreenText(
            parent=self.guiFrame,
            text="Programmed by David Sponseller\nVersion 1.4",
            pos=(-0.7 * monitor[0].width / monitor[0].height, -0.9),
            scale=0.0475,
            fg=(0.5, 7, 7, 0.75),
        )
        self.IpAddrText = OnscreenText(
            text=f"Server address + port\n{server.IPAddr} : 8765\n{server.hostname} : 8765",
            pos=(0 * monitor[0].width / monitor[0].height, -0.8),
            scale=0.06,
            parent=self.guiFrame,
            fg=(0.5, 7, 7, 0.75),
        )
        self.QuitButton = DirectButton(
            parent=self.guiFrame,
            pos=(-0.8 * monitor[0].width / monitor[0].height, 0, -0.7),
            scale=(0.1099 * (553 / 194), 1, 0.11),
            relief=DGG.FLAT,
            image=spriteSheet["exitButton"],
            geom=None,
            frameColor=(1.0, 1.0, 1.0, 0.0),
            command=sys.exit,
        )
        self.BackgroundImage3 = OnscreenImage(
            parent=self.guiFrame,
            image=spriteSheet["flightDirector"],
            scale=(0.05 * (569 / 127), 1, 0.05),
            pos=(-0.86 * monitor[0].width / monitor[0].height, 0, 0.95),
        )
        self.dronesReminingText = OnscreenText(
            text=f"Drones remaining: {server.droneCount}",
            pos=(0.8 * monitor[0].width / monitor[0].height, -0.95),
            scale=0.06,
            parent=self.guiFrame,
            fg=(0.5, 7, 7, 0.75),
        )
        self.noClientConnectedText = OnscreenText(
            text="No client connected",
            pos=(0 * monitor[0].width / monitor[0].height, 0.8),
            scale=0.1,
            parent=self.guiFrame,
            fg=(0.5, 7, 7, 0.75),
        )

        self.renderNode = self.render.attachNewNode("renderNode")

        self.worldMapObject.setDepthTest(True)
        self.worldMapObject.setScale(1)
        self.worldMapObject.setDepthWrite(True)
        self.worldMapObject.setBin("opaque", 0)
        self.worldMapObject.reparentTo(self.renderNode)
        self.worldMapObject.setPos(0, 0, -10)
        self.worldMapObject.setHpr(0, 0, 0)

        self.shipSeg = LineSegs("shipSeg")
        self.shipSeg.setThickness(2)
        self.shipSegNode = self.shipSeg.create(False)
        self.shipSegNP = self.render.attachNewNode(self.shipSegNode)

        self.voyager.reparentTo(self.renderNode)
        self.voyager.setScale(2.8)
        self.voyager.setPos(-30, 15, 1)
        cube = self.cube.instanceTo(self.renderNode)
        self.ship = NodePath("ship")
        self.ship.reparentTo(self.renderNode)
        cube.reparentTo(self.ship)
        self.ship.setScale(0.2)
        self.ship.setColor(0.2, 0.3, 1, 1)

        self.lastDroneAmount = 0
        self.droneNodePath = NodePath("droneNodePath")
        self.droneNodePath.reparentTo(self.renderNode)

        self.CamPosNode = self.render.attachNewNode("CamPosNode")
        self.camera.reparentTo(self.CamPosNode)
        self.camera.setPos(0, -150, 0)
        self.camera.lookAt(self.renderNode)
        self.CamPosNode.setHpr(0, -22, 0)
        self.accept("mouse3", self.startRotateCamera)
        self.accept("mouse3-up", self.stopRotateCamera)
        self.accept("mouse1", self.startRotateCamera)
        self.accept("mouse1-up", self.stopRotateCamera)
        self.accept(
            "wheel_up",
            self.moveCamPos,
            extraArgs=[1],
        )
        self.accept(
            "wheel_down",
            self.moveCamPos,
            extraArgs=[-1],
        )
        self.taskMgr.add(self.rotateCameraTask, "rotateCameraTask")
        self.isRotatingCamera = False

        self.noClientConnectedText.hide()
        self.renderNode.setBin("fixed", 2)
        self.renderNode.hide()
        thread.Thread(
            target=self.fadeInGuiElement_ThreadedOnly,
            kwargs={
                "element": self.guiFrame,
                "timeToFade": 80,
            },
        ).start()
        self.madeCliPicture = False
        self.taskMgr.add(self.update, "update")

    def moveCamPos(self, pos):
        current_y = self.camera.getY()
        new_y = current_y - pos * (1 - abs(current_y) / 20)
        self.camera.setY(new_y)

    def startRotateCamera(self):
        self.isRotatingCamera = True
        self.lastMouseX, self.lastMouseY = (
            self.win.getPointer(0).getX(),
            self.win.getPointer(0).getY(),
        )

    def stopRotateCamera(self):
        self.isRotatingCamera = False

    def rotateCameraTask(self, task):
        if self.isRotatingCamera:
            md = self.win.getPointer(0)
            x, y = md.getX(), md.getY()
            deltaX, deltaY = x - self.lastMouseX, y - self.lastMouseY
            self.lastMouseX, self.lastMouseY = x, y
            self.CamPosNode.setH(self.CamPosNode.getH() - deltaX * 0.1)
            self.CamPosNode.setP(self.CamPosNode.getP() - deltaY * 0.1)
        return task.cont


Main().run()
