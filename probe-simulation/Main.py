from math import pi, sin, cos, sqrt, tan
from random import randint
import time as t
import sys
import websockets as ws
import src.scripts.vars as Wvars
import src.scripts.physics as physics
import src.scripts.display as disp
import src.scripts.fileManager as fMgr
import src.scripts.client as cli
import src.scripts.weapons as weapons
import src.scripts.ai as ai
import src.scripts.guiUtils as guiUtils
import asyncio
import codecs

from screeninfo import get_monitors
from direct.showbase.ShowBase import ShowBase

from panda3d.ai import *
from panda3d.ai import AIWorld, AICharacter, Flock
from panda3d.core import *
from panda3d.core import (
    TransparencyAttrib,
    AmbientLight,
    loadPrcFile,
    ConfigVariableString,
    AntialiasAttrib,
    WindowProperties,
    NodePath,
    Spotlight,
    OrthographicLens,
    CollisionTraverser,
    CollisionNode,
    CollisionBox,
    CollisionSphere,
    CollisionRay,
    CollisionHandlerQueue,
    Vec4,
    CollisionHandlerPusher,
    MovieTexture,
    CardMaker,
    BitMask32,
    Shader,
    Point2,
    Point3,
    StringStream,
    PNMImage,
    ColorBlendAttrib,
)


from direct.gui.OnscreenImage import OnscreenImage
import direct.stdpy.threading as thread
import direct.stdpy.file as panda_fMgr
from direct.gui.DirectGui import *
from direct.motiontrail.MotionTrail import MotionTrail

monitor = get_monitors()
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


class Main(ShowBase):
    def __init__(self):
        # this should be only the absolute startup tasks, launching submodules. all other configs should go in postLoad
        ShowBase.__init__(self)
        self.accept("control-q", sys.exit)
        disp.monitor = monitor
        self.tex = {}
        disp.settingsScreen.start(self)
        self.ipEntry = DirectEntry(
            parent=self.settingsFrame,
            scale=0.05,
            pos=(0.05, 0, -0.55),
            initialText=cli.serveIPAddr,
            cursorKeys=True,
            focusOutCommand=self.configIp,
        )

    def load(self):
        self.guiFrame.hide()
        self.startupMenuBackgroundImage.hide()
        self.backfaceCullingOn()
        self.disableMouse()

        # do setup tasks
        # ...

        self.setupControls()

        disp.GUI.start(
            self=disp.GUI,
            render=self.render2d,
            _main=self,
            TransparencyAttrib=TransparencyAttrib,
        )
        physics.physicsMgr.enable(
            self=physics.physicsMgr,
            drag=0.001,
            gravity=(0, 0, 0),
            rotational_drag=0.15,
        )

        self.loadModels()
        self.setupLights()
        self.setupCamera()
        self.setupSkybox()
        self.setupScene()
        self.setupAiWorld()
        weapons.lasers.__init__(
            self=self,
            internalArgs=[
                [
                    "objects",
                    ["cube", self.loader.loadModel("src/models/drone/cube.egg")],
                ],
                ["sceneGraphs", ["render3d", self.render]],
            ],
        )
        self.postLoad()

        # end of setup tasks
        self.update_time = 0
        self.currentDroneCount = Wvars.droneNum
        self.lastDroneCount = 0
        thread.Thread(target=self.update, name="update_task").start()
        thread.Thread(
            target=cli.runClient, args=[self, "client"], name="ClientThread"
        ).start()

    def postLoad(self):
        disp.GUI.miniMap(disp.GUI)
        Wvars.shipHitPoints = Wvars.shipHealth

        #

        self.static = self.startPlayer(
            media_file="src/movies/GUI/static.mp4", name="static"
        )
        self.static.setTransparency(True)
        self.static.setAlphaScale(0)
        self.playTex("static")
        self.death = self.startPlayer(
            media_file="src/movies/GUI/death.mp4", name="death"
        )
        self.death.setTransparency(True)
        self.death.hide()
        self.playTex("death")

        self.velocityMeter.hide()
        self.posMeter.hide()
        self.HpIndicator["range"] = Wvars.shipHealth
        self.HpIndicator["value"] = Wvars.shipHitPoints
        ai.setupShipHealth(self.HpIndicator)
        self.render.prepareScene(self.win.getGsg())
        self.voyager.flattenLight()
        self.taskMgr.add(self.update_shader_inputs, "update_shader_inputs_task")

    def configIp(self):
        cli.serveIPAddr = self.ipEntry.get()
        cli.serveIp = f"ws://{cli.serveIPAddr}"
        try:
            asyncio.run(cli.testServerConnection())
            print("Connected to server")
            self.notify_win("Connected to server")
            self.startupMenuStartButton["command"] = self.load
            self.startupMenuStartButton["extraArgs"] = []
            self.startupMenuStartButton.setColor(1, 1, 1, 1)
            self.startupMenuStartButton["text"] = ""
        except:
            print("Failed to connect to server")
            self.notify_win("Failed to connect to server")

    def startPlayer(self, media_file, name):
        self.tex[name] = MovieTexture("name")
        success = self.tex[name].read(media_file)
        try:
            assert success, "Failed to load video!"
        except:
            ...
        cm = CardMaker("fullscreenCard")
        cm.setFrameFullscreenQuad()
        cm.setUvRange(self.tex[name])
        card = NodePath(cm.generate())
        card.reparentTo(self.render2d)
        card.setTexture(self.tex[name])
        return card

    def stopTex(self, name):
        self.tex[name].stop()

    def playTex(self, name):
        self.tex[name].play()

    nodePositions = []
    doneDeath = False

    def update(self):
        while True:
            md = self.win.getPointer(0)
            mouseX = md.getX()
            mouseY = md.getY()
            dt = 1 / 60
            self.nodePositions = {
                "drones": [tuple(ai["mesh"].getPos()) for ai in self.aiChars],
                "ship": tuple(self.ship.getPos()),
                "voyager": tuple(self.voyager.getPos()),
            }

            playerMoveSpeed = Wvars.speed / 100
            if (
                self.ship.getDistance(self.voyager) > 9000
                or self.HpIndicator["value"] <= 0
                or cli.serverDeath
            ):
                if not self.doneDeath:
                    self.doneDeath = True
                    cli.serverDeath = False
                    cli.cliDead = True
                    self.ship.setPos(0, 0, 0)
                    physics.physicsMgr.removeObject(
                        physics.physicsMgr, self.ship, "ship"
                    )
                    physics.physicsMgr.removeObject(
                        physics.physicsMgr, self.camNodePath, "camNodePath"
                    )
                    self.updateOverlay()
                    self.silenceInput()
                    self.fullStop()
                    ai.pauseAll(self.aiChars)
                    self.pauseFrame = DirectFrame(
                        parent=self.render2d,
                        frameSize=(-1, 1, -1, 1),
                        frameColor=(0, 0, 0, 1),
                    )
                    self.death.show()
                    self.check_resume()
            else:
                ai.update(AIworld=self.AIworld, aiChars=self.aiChars, ship=self.ship)
                self.currentDroneCount = len(
                    list(_ai for _ai in self.aiChars if _ai["active"])
                )
                self.droneCount.setText(f"Drones Remaining: {self.currentDroneCount}")
                if self.currentDroneCount != self.lastDroneCount:
                    for node in self.droneTargetIndicator.getChildren():
                        node.destroy()
                    for char in self.aiChars:
                        node = char["mesh"]
                        img = OnscreenImage(
                            image=self.loader.loadTexture(
                                "src/textures/raw/target.png"
                            ),
                            pos=(0, -2, 0),
                            scale=4,
                            parent=node,
                        )
                        img.setTransparency(1)
                        self.droneTargetList.append([node, img])

                # update velocities
                if self.update_time > 4:
                    self.update_time = 0
                    try:
                        self.velocity = physics.physicsMgr.getObjectVelocity(
                            physics.physicsMgr, self.ship, "ship"
                        )
                        self.vel_text = (
                            "Thrust: "
                            + str(
                                round(
                                    number=(
                                        ((round(abs(self.velocity[0]) * 1000)) ^ 2)
                                        + ((round(abs(self.velocity[1]) * 1000)) ^ 2)
                                        + ((round(abs(self.velocity[2]) * 1000)) ^ 2)
                                        / 1000
                                    )
                                    - 4,
                                    ndigits=2,
                                )
                            )
                            + " km/s"
                        )
                        self.velocityMeter.configure(text=self.vel_text)
                        self.posMeter.configure(
                            text="pos XYZ: " + str(self.ship.getPos())
                        )
                    except:
                        ...
                else:
                    self.update_time += 1

                # do system updates
                self.camera.lookAt(self.ship)
                self.skybox.setPos(self.camNodePath.getPos())

                self.SceneLightNode_sm.lookAt(self.ship)

                # calculate thrust
                if Wvars.movementEnabled == True:
                    if self.keyMap["left"]:
                        physics.physicsMgr.addRotationalForce(
                            self=physics.physicsMgr,
                            object=self.ship,
                            name="ship",
                            rotational_vector=[Wvars.turnspeed / 250, 0, 0],
                        )
                    if self.keyMap["right"]:
                        physics.physicsMgr.addRotationalForce(
                            self=physics.physicsMgr,
                            object=self.ship,
                            name="ship",
                            rotational_vector=[-Wvars.turnspeed / 250, 0, 0],
                        )
                    if self.keyMap["up"]:
                        physics.physicsMgr.addRotationalForce(
                            self=physics.physicsMgr,
                            object=self.ship,
                            name="ship",
                            rotational_vector=[0, Wvars.turnspeed / 250, 0],
                        )
                    if self.keyMap["down"]:
                        physics.physicsMgr.addRotationalForce(
                            self=physics.physicsMgr,
                            object=self.ship,
                            name="ship",
                            rotational_vector=[0, -Wvars.turnspeed / 250, 0],
                        )
                    if self.keyMap["tiltRight"]:
                        physics.physicsMgr.addRotationalForce(
                            self=physics.physicsMgr,
                            object=self.ship,
                            name="ship",
                            rotational_vector=[0, 0, Wvars.turnspeed / 250],
                        )
                    if self.keyMap["tiltLeft"]:
                        physics.physicsMgr.addRotationalForce(
                            self=physics.physicsMgr,
                            object=self.ship,
                            name="ship",
                            rotational_vector=[0, 0, -Wvars.turnspeed / 250],
                        )
                    if self.keyMap["forward"]:
                        self.x_movement -= (
                            dt * playerMoveSpeed * sin(degToRad(self.ship.getH()))
                        )
                        self.y_movement += (
                            dt * playerMoveSpeed * cos(degToRad(self.ship.getH()))
                        )
                        self.z_movement += (
                            dt * playerMoveSpeed * cos(degToRad(self.ship.getP() - 90))
                        )
                    if self.keyMap["backward"]:
                        self.x_movement += (
                            dt * playerMoveSpeed * sin(degToRad(self.ship.getH()))
                        )
                        self.y_movement -= (
                            dt * playerMoveSpeed * cos(degToRad(self.ship.getH()))
                        )
                        self.z_movement -= (
                            dt * playerMoveSpeed * cos(degToRad(self.ship.getP() - 90))
                        )

                physics.physicsMgr.addVectorForce(
                    physics.physicsMgr,
                    self.ship,
                    "ship",
                    [self.x_movement, self.y_movement, self.z_movement],
                )
                self.x_movement = 0
                self.y_movement = 0
                self.z_movement = 0
                physics.physicsMgr.updateWorldPositions(physics.physicsMgr)

                self.camNodePath.setPos(self.ship.getPos())
                Wvars.camX = self.camNodePath.getX()
                Wvars.camY = self.camNodePath.getY()
                Wvars.camZ = self.camNodePath.getZ()

                # move cursor to stay within screen bounds
                if Wvars.cursorLock == True:

                    def moveCam():
                        mouseChangeX = mouseX - self.lastMouseX
                        mouseChangeY = mouseY - self.lastMouseY

                        physics.physicsMgr.addRotationalForce(
                            self=physics.physicsMgr,
                            object=self.camNodePath,
                            name="camNodePath",
                            rotational_vector=[
                                -mouseChangeX / 100,
                                -mouseChangeY
                                / 100
                                * (monitor[0].width / monitor[0].height),
                                0,
                            ],
                        )

                        disp.GUI.mapFrame.setR(self.camera.getH())

                        self.lastMouseX = mouseX
                        self.lastMouseY = mouseY

                    if sys.platform == "darwin":
                        moveCam()
                    elif int(monitor[0].width / 2) - mouseX >= int(
                        monitor[0].width / 4
                    ):
                        self.win.movePointer(
                            0, x=int(monitor[0].width / 2), y=int(mouseY)
                        )
                        self.lastMouseX = int(monitor[0].width / 2)
                    elif int(monitor[0].width / 2) - mouseX <= -int(
                        monitor[0].width / 4
                    ):
                        self.win.movePointer(
                            0, x=int(monitor[0].width / 2), y=int(mouseY)
                        )
                        self.lastMouseX = int(monitor[0].width / 2)
                    elif int(monitor[0].height / 2) - mouseY >= int(
                        monitor[0].height / 4
                    ):
                        self.win.movePointer(
                            0, x=int(mouseX), y=int(monitor[0].height / 2)
                        )
                        self.lastMouseY = int(monitor[0].height / 2)
                    elif int(monitor[0].height / 2) - mouseY <= -int(
                        monitor[0].height / 4
                    ):
                        self.win.movePointer(
                            0, x=int(mouseX), y=int(monitor[0].height / 2)
                        )
                        self.lastMouseY = int(monitor[0].height / 2)
                    else:
                        # move camera based on mouse position
                        moveCam()

                if Wvars.aiming == True:
                    md = self.win.getPointer(0)
                    self.lastMouseX = md.getX()
                    self.lastMouseY = md.getY()

                    self.crosshair.setPos(
                        (2 / monitor[0].width) * md.getX() - 1,
                        0,
                        -((2 / monitor[0].height) * md.getY() - 1),
                    )
                    if self.progress["value"] < 100:
                        self.progress["value"] += 1

            if self.ship.getDistance(self.voyager) > 4000:
                self.updateOverlay()
            t.sleep(1 / 60)

    def check_resume(self):
        def _loop():
            dead = True
            while dead:
                if cli.cliRespawn:
                    dead = False
                    cli.serverDeath = False
                    cli.cliDead = False
                    cli.cliRespawn = False
                    self.resume()
                    break
                t.sleep(0.25)

        thread.Thread(target=_loop).start()

    def resume(self):
        self.pauseFrame.destroy()
        self.death.hide()
        self.HpIndicator["range"] = Wvars.shipHealth
        self.HpIndicator["value"] = Wvars.shipHitPoints
        self.reviveInput()
        physics.physicsMgr.registerObject(
            self=physics.physicsMgr,
            object=self.ship,
            name="ship",
            velocity=[0, 0, 0],
            rotational_velocity=[0, 0, 0],
        )
        physics.physicsMgr.registerObject(
            self=physics.physicsMgr,
            object=self.camNodePath,
            name="camNodePath",
            velocity=[0, 0, 0],
            rotational_velocity=[0, 0, 0],
        )
        ai.resumeAll(self.aiChars, self.ship)
        self.doneDeath = False

    def updateOverlay(self):
        self.static.setAlphaScale(
            1 / (6000 / (self.ship.getDistance(self.voyager) - 4000))
        )

    def setupControls(self):
        self.lastMouseX = self.win.getPointer(0).getX()
        self.lastMouseY = self.win.getPointer(0).getX()
        self.x_movement = 0
        self.y_movement = 0
        self.z_movement = 0
        self.keyMap = {
            "forward": False,
            "backward": False,
            "left": False,
            "right": False,
            "up": False,
            "down": False,
            "tiltLeft": False,
            "tiltRight": False,
            "primary": False,
            "secondary": False,
        }

        # self.accept("escape", sys.exit)
        self.accept("mouse1", self.MouseClicked)
        self.accept("mouse1-up", self.doNothing)
        # self.accept("mouse3", self.toggleTargetingGui)
        # self.accept("mouse3-up", self.toggleTargetingGui)

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
        self.accept("q", self.updateKeyMap, ["tiltLeft", True])
        self.accept("q-up", self.updateKeyMap, ["tiltLeft", False])
        self.accept("e", self.updateKeyMap, ["tiltRight", True])
        self.accept("e-up", self.updateKeyMap, ["tiltRight", False])
        self.accept("wheel_up", self.devModeOn)
        self.accept("wheel_down", self.devModeOff)
        # self.accept("control-wheel_up", self.cameraZoom, ["in"])
        # self.accept("control-wheel_down", self.cameraZoom, ["out"])
        # self.accept("f", self.fullStop)

    def cameraZoom(self, inOrOut):
        if inOrOut == "in":
            self.camera.setPos(
                self.camera.getPos()
                - (1 + (self.camera.getDistance(self.camNodePath) / 500))
            )
        elif inOrOut == "out":
            self.camera.setPos(
                self.camera.getPos()
                + (1 + (self.camera.getDistance(self.camNodePath) / 500))
            )

    def devModeOn(self):
        self.cTrav.showCollisions(self.render)
        self.wireframeOn()
        self.velocityMeter.show()
        self.posMeter.show()

    def devModeOff(self):
        self.cTrav.hideCollisions()
        self.wireframeOff()
        self.velocityMeter.hide()
        self.posMeter.hide()

    def toggleTargetingGui(self):
        if Wvars.aiming == False:
            Wvars.aiming = True
            Wvars.cursorLock = False
            self.hideCursor(True)
            Wvars.movementEnabled = False
            self.progress["value"] = 0
            disp.GUI.show(disp.GUI)
        elif Wvars.aiming == True:
            Wvars.aiming = False
            Wvars.cursorLock = True
            self.hideCursor(True)
            Wvars.movementEnabled = True
            disp.GUI.hide(disp.GUI)
            self.progress["value"] = 0

    def chargeLaser(self):
        self.laserPower = 0

    def updateKeyMap(self, key, value):
        self.keyMap[key] = value

    def doNothing(self): ...

    def fullStop(self):
        self.x_movement = 0
        self.y_movement = 0
        self.z_movement = 0
        for pos in ["left", "right", "up", "down", "forward", "backward"]:
            self.updateKeyMap(pos, False)
        physics.physicsMgr.clearVectorForce(
            self=physics.physicsMgr,
            object=self.ship,
            name="ship",
        )
        physics.physicsMgr.clearRotationalForce(
            self=physics.physicsMgr,
            object=self.ship,
            name="ship",
        )
        physics.physicsMgr.clearRotationalForce(
            self=physics.physicsMgr,
            object=self.camNodePath,
            name="camNodePath",
        )

    def loadModels(self):
        self.sun = self.loader.loadModel("src/models/sun/sun.egg")
        self.skybox = self.loader.loadModel("src/models/skybox/box.bam")
        self.ship = self.loader.loadModel("src/models/simple_ship/model.egg")
        try:
            self.voyager = self.loader.loadModel("src/models/voyager/voyager.bam")
        except:
            self.voyager = self.loader.loadModel("src/models/drone/cube.egg")
        try:
            self.drone = self.loader.loadModel("src/models/drone/drone.bam")
        except:
            self.drone = self.loader.loadModel("src/models/drone/cube.egg")
        disp.GUI.setup(disp.GUI)

    def setupLights(self):
        ambientLight = AmbientLight("ambientLight")
        ambientLight.setColor((0.3, 0.3, 0.3, 1))
        ambientLightNP = self.render.attachNewNode(ambientLight)
        self.render.setLight(ambientLightNP)

        slight = Spotlight("slight")
        slight.setColor((2, 2, 2, 1))
        lens = OrthographicLens()
        lens.setFocalLength(20)
        slight.setLens(lens)

        self.SceneLightNode_sm = self.render.attachNewNode(slight)
        self.SceneLightNode_sm.setPos(10000, 0, 1000)
        self.SceneLightNode_sm.lookAt(self.ship)
        self.render.setLight(self.SceneLightNode_sm)

    def setupCamera(self):
        self.camNodePath = NodePath("Camera_ship")
        self.camNodePath.reparentTo(self.render)

        self.ship.reparentTo(self.render)

        physics.physicsMgr.registerObject(
            self=physics.physicsMgr,
            object=self.ship,
            name="ship",
            velocity=[0, 0, 0],
            rotational_velocity=[0, 0, 0],
        )
        physics.physicsMgr.registerObject(
            self=physics.physicsMgr,
            object=self.camNodePath,
            name="camNodePath",
            velocity=[0, 0, 0],
            rotational_velocity=[0, 0, 0],
        )

        self.lensFlareShader = Shader.load(
            Shader.SL_GLSL,
            vertex="src/shaders/flat_v.glsl",
            fragment="src/shaders/post1_hsv_f.glsl",
        )

        # Add a transparent card over the screen
        cm = CardMaker("fullscreenCard")
        cm.setFrameFullscreenQuad()
        self.shaderCard = NodePath(cm.generate())
        self.shaderCard.setShader(self.lensFlareShader)
        self.shaderCard.setAttrib(ColorBlendAttrib.make(ColorBlendAttrib.MAdd))
        self.shaderCard.set_shader_input(
            "iResolution",
            (
                self.win.getXSize(),
                self.win.getYSize(),
            ),
        )
        self.shaderCard.reparentTo(self.render2d)
        self.shaderCard.setColor(0, 0, 0, 1)

        self.camera.reparentTo(self.camNodePath)
        self.camera.setPos(0, -50, 40)
        self.camLens.setFov(Wvars.camFOV)
        self.camera.lookAt(self.ship)

        self.cTrav = CollisionTraverser()

        fromObject = self.ship.attachNewNode(CollisionNode("shipColNode"))
        fromObject.node().addSolid(CollisionSphere(0, 0, 0, Wvars.shipHitRadius))
        fromObject.node().set_from_collide_mask(1)
        fromObject.node().set_from_collide_mask(0)
        pusher = CollisionHandlerPusher()
        pusher.addCollider(fromObject, self.ship)
        self.cTrav.addCollider(fromObject, pusher)

        fromObject = self.camera.attachNewNode(CollisionNode("cameraColNode"))
        fromObject.node().addSolid(CollisionSphere(0, 0, 0, 1.5))
        fromObject.node().set_from_collide_mask(1)
        fromObject.node().set_from_collide_mask(0)
        pusher.addCollider(fromObject, self.camera, self.drive.node())
        self.cTrav.addCollider(fromObject, pusher)

        self.ray = CollisionRay()
        self.ray.setFromLens(self.camNode, (0, 0))
        self.rayNode = CollisionNode("line-of-sight")
        self.rayNode.addSolid(self.ray)
        self.rayNode.set_into_collide_mask(0)
        self.rayNode.set_into_collide_mask(1)
        self.rayNodePath = self.ship.attachNewNode(self.rayNode)
        self.rayQueue = CollisionHandlerQueue()
        self.cTrav.addCollider(self.rayNodePath, self.rayQueue)

        targetNode = NodePath("targetingNode")
        targetNode.reparentTo(self.ship)
        targetNode.set_y(45)

        size = 3

        fromObject = self.ship.attachNewNode(CollisionNode("colNode"))
        fromObject.node().addSolid(CollisionSphere(0, 0, 0, size))
        fromObject.node().set_from_collide_mask(0)
        fromObject.node().setPythonTag("owner", targetNode)
        fromObject.set_y(10000)

        sNodeSolid = CollisionNode("block-collision-node")
        collider = self.ship.attachNewNode(sNodeSolid)
        collider.setPythonTag("owner", targetNode)

        self.cTrav.addCollider(fromObject, self.rayQueue)

        disp.ShaderCall.setupShaders(
            self=disp.ShaderCall,
            mainApp=self,
            light=self.SceneLightNode_sm,
            wantShaders=True,
        )

        self.hideCursor(True)
        self.velocityMeter = OnscreenText(
            text="",
            scale=(0.1 * (monitor[0].height / monitor[0].width), 0.1, 0.1),
            pos=(-0.5, -0.95),
            fg=(1, 1, 1, 1),
            parent=self.render2d,
        )
        self.posMeter = OnscreenText(
            text="",
            scale=(0.1 * (monitor[0].height / monitor[0].width), 0.1, 0.1),
            pos=(-0.5, -0.8),
            fg=(1, 1, 1, 1),
            parent=self.render2d,
        )

    def hideCursor(self, boolVar):
        properties = WindowProperties()
        properties.setCursorHidden(boolVar)
        properties.setMouseMode(WindowProperties.M_relative)
        self.win.requestProperties(properties)

    def setupSkybox(self):
        self.skybox.setScale(5000)
        self.skybox.setBin("background", 1)
        self.skybox.setDepthWrite(0)
        self.skybox.setLightOff()
        self.skybox.setAntialias(AntialiasAttrib.MNone)
        self.skybox.setColor(0.5, 0.5, 0.5, 0.5)
        self.skybox.reparentTo(self.render)

    def setupAiWorld(self):
        self.AIworld = AIWorld(self.render)
        self.aiChars = []
        for num in range(Wvars.droneNum):
            dNode = self.loader.loadModel("src/models/drone/cube.egg")
            dNode.instanceTo(self.droneMasterNode)
            dNode.setPos(randint(-500, 500), randint(-400, 300), randint(-50, 50))
            dNode.setScale(3)
            AIchar = AICharacter(
                model_name="seeker",
                model_np=dNode,
                mass=100,
                movt_force=80,
                max_force=50,
            )
            self.AIworld.addAiChar(AIchar)

            size = Wvars.droneHitRadius

            fromObject = dNode.attachNewNode(CollisionNode("colNode"))
            fromObject.node().addSolid(CollisionSphere(0, 0, 0, size))
            fromObject.node().set_from_collide_mask(0)
            fromObject.node().setPythonTag("owner", num)
            fromObject.node().setPythonTag("collision", fromObject)
            pusher = CollisionHandlerPusher()
            pusher.addCollider(fromObject, dNode)
            self.cTrav.addCollider(fromObject, pusher)

            healthIndicatorFrame = DirectFrame(parent=dNode, pos=(0, 0, 1), scale=5)
            healthBar = DirectWaitBar(
                parent=healthIndicatorFrame,
                range=Wvars.droneHealth,
                value=Wvars.droneHealth,
                barColor=(1, 0.1, 0.2, 1),
                relief=None,
            )
            aiObject = {
                "mesh": dNode,
                "ai": AIchar,
                "active": True,
                "firing": False,
                "id": num,
                "health": Wvars.droneHealth,
                "healthBar": healthBar,
            }

            self.aiChars.append(aiObject)
            ai.fireLoop(self.ship, aiObject)

    def setupScene(self):

        droneNode = CollisionSphere(0, 0, 0, 1)
        droneNodeSolid = CollisionNode("block-collision-node")
        droneNodeSolid.addSolid(droneNode)

        self.voyager.reparentTo(self.render)
        self.voyager.setScale(280)
        self.voyager.setPos(-3000, 1500, 100)
        self.camera.lookAt(self.voyager)

        self.droneMasterNode = NodePath("drone-MN")
        self.droneMasterNode.reparentTo(self.render)

        self.shipTrailNode = NodePath("shipTrailNode")
        self.shipTrailNode.reparentTo(self.ship)
        self.shipTrailNode.set_y(-10)

        for x in [-6, 6]:
            shipTrail = MotionTrail("shipTrail", self.shipTrailNode)

            flame_colors = (
                Vec4(0, 0.0, 1.0, 1),
                Vec4(0, 0.2, 1.0, 1),
                Vec4(0, 0.1, 1.0, 1),
                Vec4(0.0, 0.0, 0.4, 1),
            )
            center = self.render.attach_new_node("center")
            around = center.attach_new_node("around")
            around.set_z(1.5)
            center.set_x(x)
            res = 8
            for i in range(res + 1):
                center.set_r((360 / res) * i)
                vertex_pos = around.get_pos(self.render)
                shipTrail.add_vertex(vertex_pos)

                start_color = flame_colors[i % len(flame_colors)] * 1.7
                end_color = Vec4(0, 0, 0, 1)
                shipTrail.set_vertex_color(i, start_color, end_color)
            shipTrail.update_vertices()

            shipTrail.register_motion_trail()
            shipTrail.geom_node_path.reparentTo(self.render)
        self.enableParticles()

    def MouseClicked(self):
        # self.ray.setFromLens(self.camNode, mpos.getX(), mpos.getY())
        self.cTrav.traverse(self.render)
        destroy = False
        if self.rayQueue.getNumEntries() > 1:
            self.rayQueue.sortEntries()
            try:
                rayHit = self.rayQueue.getEntry(1)
                hitNodePath = rayHit.getIntoNodePath()
                normal = rayHit.getSurfaceNormal(hitNodePath)
            except:
                None
            try:
                self.aiChars[hitNodePath.getPythonTag("owner")]["health"] -= 1
                hitObject = self.aiChars[hitNodePath.getPythonTag("owner")]["mesh"]
                if self.aiChars[hitNodePath.getPythonTag("owner")]["health"] == 0:
                    destroy = True
                    colNode = hitNodePath.getPythonTag("collision")
                    colNode.set_y(-10000)
                    self.aiChars[hitNodePath.getPythonTag("owner")]["active"] = False
                    ai.removeChar(
                        self.aiChars[hitNodePath.getPythonTag("owner")], ship=self.ship
                    )
                else:
                    self.aiChars[hitNodePath.getPythonTag("owner")]["healthBar"][
                        "value"
                    ] = self.aiChars[hitNodePath.getPythonTag("owner")]["health"]
                    destroy = False
            except:
                hitObject = hitNodePath.getPythonTag("owner")
                destroy = False
            if type(hitObject) == int:
                return
            else:
                weapons.lasers.fire(
                    origin=self.ship, target=hitObject, normal=normal, destroy=destroy
                )

    def update_shader_inputs(self, task):
        self.shaderCard.set_shader_input(
            "iResolution", (self.win.getXSize(), self.win.getYSize())
        )
        self.shaderCard.set_shader_input("iTime", globalClock.getFrameTime())  # type: ignore
        return task.cont

    def notify_win(self, message):
        def destroyThread(obj, wait=2, time=0.6):
            t.sleep(wait)
            if not self.objDestroyed:
                self.objDestroyed = True
                obj.find("**/button").removeNode()
                obj.colorScaleInterval(
                    time,
                    (
                        obj.getColorScale()[0],
                        obj.getColorScale()[1],
                        obj.getColorScale()[2],
                        0,
                    ),
                ).start()
                t.sleep(time + 0.1)
                obj.destroy()

        self.objDestroyed = False

        notifyFrame = DirectFrame(
            parent=self.aspect2d,
            frameSize=(-0.3, 0.3, -0.15, 0.15),
            frameColor=(0, 0, 0, 0.6),
            pos=(-1.2, 5, -0.5),
        )
        notifyLabel = DirectLabel(
            parent=notifyFrame,
            text=message,
            scale=0.05,
            pos=(0, 0, 0),
            text_fg=(1, 1, 1, 1),
            text_wordwrap=10,
            frameColor=(0, 0, 0, 0),
        )
        destroyButton = DirectButton(
            parent=notifyFrame,
            text="X",
            scale=0.05,
            pos=(-0.275, 0, 0),
            command=thread.Thread(
                target=destroyThread, args=[notifyFrame, 0, 0.3]
            ).start,
        )
        destroyButton.setName("button")
        notifyFrame.setTransparency(True)

        thread.Thread(target=destroyThread, args=[notifyFrame, 2, 0.6]).start()
        return notifyFrame


Main().run()
