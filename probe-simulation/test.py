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
        ShowBase.__init__(self)
        self.accept("control-q", sys.exit)
        self.obj = self.loader.loadModel()
        cm = CardMaker("fullscreenCard")
        cm.setFrameFullscreenQuad()
        self.box = NodePath(cm.generate())
        self.box.setShader(self.lensFlareShader)
        self.box.setAttrib(ColorBlendAttrib.make(ColorBlendAttrib.MAdd))
        self.box.set_shader_input(
            "iResolution",
            (
                self.win.getXSize(),
                self.win.getYSize(),
            ),
        )
        self.box.reparentTo(self.render2d)

    def world_to_screen(
        self, world_point, camera_pos, camera_rot, fov, screen_width, screen_height
    ):
        # Translate the point to the camera's coordinate system
        translated_point = world_point - camera_pos

        # Rotate the point according to the camera's rotation
        cos_yaw = cos(degToRad(camera_rot[0]))
        sin_yaw = sin(degToRad(camera_rot[0]))
        cos_pitch = cos(degToRad(camera_rot[1]))
        sin_pitch = sin(degToRad(camera_rot[1]))
        cos_roll = cos(degToRad(camera_rot[2]))
        sin_roll = sin(degToRad(camera_rot[2]))

        rotated_point = Point3(
            translated_point[0] * (cos_yaw * cos_pitch)
            + translated_point[1]
            * (cos_yaw * sin_pitch * sin_roll - sin_yaw * cos_roll)
            + translated_point[2]
            * (cos_yaw * sin_pitch * cos_roll + sin_yaw * sin_roll),
            translated_point[0] * (sin_yaw * cos_pitch)
            + translated_point[1]
            * (sin_yaw * sin_pitch * sin_roll + cos_yaw * cos_roll)
            + translated_point[2]
            * (sin_yaw * sin_pitch * cos_roll - cos_yaw * sin_roll),
            translated_point[0] * (-sin_pitch)
            + translated_point[1] * (cos_pitch * sin_roll)
            + translated_point[2] * (cos_pitch * cos_roll),
        )

        # Perspective projection
        aspect_ratio = screen_width / screen_height
        fov_rad = degToRad(fov[0])
        screen_x = (
            rotated_point[0] / (rotated_point[2] * tan(fov_rad / 2))
        ) * aspect_ratio
        screen_y = rotated_point[1] / (rotated_point[2] * tan(fov_rad / 2))

        # Convert to screen coordinates
        screen_x = (screen_x + 1) / 2 * screen_width
        screen_y = (1 - screen_y) / 2 * screen_height
        print(f"\n{screen_x}\n{screen_y}\n")

        return Point2(screen_x, screen_y)
