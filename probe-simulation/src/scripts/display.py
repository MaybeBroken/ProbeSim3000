from direct.filter.CommonFilters import CommonFilters
from direct.gui.DirectGui import *
from src.scripts.guiUtils import fade
import src.scripts.vars as Wvars
from direct.directtools.DirectGrid import DirectGrid
from panda3d.core import deg2Rad, TextNode
import simplepbr as pbr
import sys
import time as t

monitor = None
main = None
guiClass = None
spriteSheet = {}


class ShaderCall:
    def setupShaders(self, mainApp, light, wantShaders):
        if wantShaders == True:
            mainApp.render.setShaderAuto()
            filters = CommonFilters(mainApp.win, mainApp.cam)
            filters.setExposureAdjust(1)
            filters.setBloom(
                blend=(0.3, 0.4, 0.3, 0.8),
                mintrigger=0.65,
                maxtrigger=1,
                desat=0.1,
                intensity=0.25,
                size="medium",
            )
            filters.setSrgbEncode()
            filters.setHighDynamicRange()
            filters.setBlurSharpen(0.5)
        ...


class settingsScreen:
    def start(self):
        def updateDifficulty(arg):
            if arg == "Blank":
                self.shipHealthSlider["value"] = 0
                self.shipHitRadiusSlider["value"] = 0
                self.droneHitRadiusSlider["value"] = 25
                self.droneNum.set("0")
                self.droneHealthSlider["value"] = 1

            elif arg == "Easy":
                self.shipHealthSlider["value"] = 200
                self.shipHitRadiusSlider["value"] = 3
                self.droneHitRadiusSlider["value"] = 25
                self.droneNum.set("10")
                self.droneHealthSlider["value"] = 5
            elif arg == "Medium":
                self.shipHealthSlider["value"] = 120
                self.shipHitRadiusSlider["value"] = 5
                self.droneHitRadiusSlider["value"] = 20
                self.droneNum.set("20")
                self.droneHealthSlider["value"] = 12
            elif arg == "Difficult":
                self.shipHealthSlider["value"] = 60
                self.shipHitRadiusSlider["value"] = 8
                self.droneHitRadiusSlider["value"] = 18
                self.droneNum.set("32")
                self.droneHealthSlider["value"] = 20
            elif arg == "Hard":
                self.shipHealthSlider["value"] = 40
                self.shipHitRadiusSlider["value"] = 10
                self.droneHitRadiusSlider["value"] = 14
                self.droneNum.set("45")
                self.droneHealthSlider["value"] = 30

        def updateGuiValues():
            try:
                self.shipHealthTitle["text"] = (
                    f"Ship Hit Points: {int(self.shipHealthSlider['value'])}"
                )
                self.shipHitRadiusTitle["text"] = (
                    f"Ship Hitbox Radius: {int(self.shipHitRadiusSlider['value'])}"
                )
                self.droneHitRadiusTitle["text"] = (
                    f"Drone Hitbox Radius: {int(self.droneHitRadiusSlider['value'])}"
                )
                self.droneHealthTitle["text"] = (
                    f"Drone Hit Points: {int(self.droneHealthSlider['value'])}"
                )
                Wvars.shipHealth = int(self.shipHealthSlider["value"])
                Wvars.shipHitRadius = int(self.shipHitRadiusSlider["value"])
                Wvars.droneHitRadius = int(self.droneHitRadiusSlider["value"])
                Wvars.droneNum = int(self.droneNum.get())
                Wvars.droneHealth = int(self.droneHealthSlider["value"])
            except Exception as e:
                print(e)
                self.notify_win(f"error updating gui values, check the console")

        global spriteSheet
        self.setBackgroundColor(0, 0, 0, 1)
        self.guiFrame = DirectFrame(parent=self.aspect2d)
        spriteSheet["menuBackground"] = self.loader.loadTexture(
            "src/textures/raw/menuBackground.png"
        )
        spriteSheet["startButton"] = self.loader.loadTexture(
            "src/textures/raw/startButton.png"
        )
        spriteSheet["startButton"]
        spriteSheet["exitButton"] = self.loader.loadTexture(
            "src/textures/raw/exitButton.png"
        )
        spriteSheet["voyagerLogo"] = self.loader.loadTexture(
            texturePath="src/textures/raw/Voyager_Logo.png",
        )
        spriteSheet["flightDirector"] = self.loader.loadTexture(
            texturePath="src/textures/raw/flightDirectorTile.png",
        )

        self.startupMenuFrame = DirectFrame(parent=self.guiFrame)
        self.startupMenuFrame.set_transparency(1)

        self.startupMenuBackgroundImage = self.startPlayer(
            "src/movies/GUI/menu.mp4", "menu"
        )
        self.playTex("menu")

        self.startupMenuBackgroundImage2 = OnscreenImage(
            parent=self.startupMenuFrame,
            image=spriteSheet["voyagerLogo"],
            scale=0.25,
            pos=(0.825 * monitor[0].width / monitor[0].height, 0, -0.725),
        )

        self.startupMenuStartButton = DirectButton(
            parent=self.startupMenuFrame,
            pos=(-0.7 * monitor[0].width / monitor[0].height, 0, 0.6),
            scale=(0.12 * (553 / 194), 1, 0.12),
            relief=None,
            text="connect to server first",
            text_scale=(0.1 / (553 / 194) * 5, 0.5, 0.6),
            text_pos=(0, -0.65),
            text_fg=(1, 1, 1, 1),
            image=spriteSheet["startButton"],
            geom=None,
            frameColor=(1.0, 1.0, 1.0, 0.0),
            command=self.notify_win,
            extraArgs=["attempted to start without connection"],
        )
        self.startupMenuStartButton.setColor(0, 0, 0, 0.5)

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
            text="Programmed by David Sponseller\nVersion 1.2",
            pos=(-0.7 * monitor[0].width / monitor[0].height, -0.9),
            scale=0.02,
            parent=self.startupMenuFrame,
            fg=(0.5, 7, 7, 0.75),
            font=self.loader.loadFont("src/fonts/sector_034.ttf"),
        )

        self.settingsFrame = DirectFrame(
            parent=self.guiFrame,
            frameSize=(-0.25, 0.75, -0.75, 0.75),
            frameColor=(0, 0, 0, 0.4),
        )
        self.settingsTopBar = DirectFrame(
            parent=self.settingsFrame,
            frameSize=(-0.25, 0.75, 0.65, 0.75),
            frameColor=(0, 0, 0, 0.4),
        )
        self.presetsTitle = OnscreenText(
            text="Presets: ",
            parent=self.settingsTopBar,
            scale=0.025,
            pos=(-0.1, 0.69),
            fg=(1, 1, 1, 1),
            font=self.loader.loadFont("src/fonts/sector_034.ttf"),
        )
        self.presetsMenu = DirectOptionMenu(
            parent=self.settingsTopBar,
            items=[
                "Blank",
                "Easy",
                "Medium",
                "Difficult",
                "Hard",
            ],
            command=updateDifficulty,
            relief=DGG.FLAT,
            scale=0.055,
            pos=(0.05, 1, 0.69),
            text_font=self.loader.loadFont("src/fonts/sector_034.ttf"),
            text_scale=0.6,
            text_pos=(0.3, 0, 0),
            item_relief=DGG.FLAT,
            item_text_font=self.loader.loadFont("src/fonts/sector_034.ttf"),
            item_scale=1,
            item_text_scale=0.6,
            item_text_pos=(0, 0, 0.1),
            item_frameSize=(-0.3, 1.3, -0.4, 0.8),
        )

        self.shipHealthTitle = OnscreenText(
            text=f"Ship Hit Points: 1",
            parent=self.settingsFrame,
            scale=0.03,
            pos=(0.25, 0.55),
            fg=(1, 1, 1, 1),
            font=self.loader.loadFont("src/fonts/sector_034.ttf"),
        )
        self.shipHealthSlider = DirectSlider(
            parent=self.settingsFrame,
            range=(40, 200),
            pageSize=1,
            scale=0.2,
            thumb_frameSize=(-0.05, 0.05, -0.08, 0.08),
            thumb_relief=DGG.FLAT,
            thumb_geom=None,
            thumb_frameColor=(0.2, 0.3, 1, 1),
            pos=(0.25, 0, 0.485),
            command=updateGuiValues,
        )

        self.shipHitRadiusTitle = OnscreenText(
            text=f"Ship Hitbox Radius: 3",
            parent=self.settingsFrame,
            scale=0.03,
            pos=(0.25, 0.4),
            fg=(1, 1, 1, 1),
            font=self.loader.loadFont("src/fonts/sector_034.ttf"),
        )
        self.shipHitRadiusSlider = DirectSlider(
            parent=self.settingsFrame,
            range=(3, 15),
            pageSize=1,
            scale=0.2,
            thumb_frameSize=(-0.05, 0.05, -0.08, 0.08),
            thumb_relief=DGG.FLAT,
            thumb_geom=None,
            thumb_frameColor=(0.2, 0.3, 1, 1),
            pos=(0.25, 0, 0.335),
            command=updateGuiValues,
        )

        self.droneHitRadiusTitle = OnscreenText(
            text=f"Drone Hitbox Radius: 3",
            parent=self.settingsFrame,
            scale=0.03,
            pos=(0.25, 0.25),
            fg=(1, 1, 1, 1),
            font=self.loader.loadFont("src/fonts/sector_034.ttf"),
        )
        self.droneHitRadiusSlider = DirectSlider(
            parent=self.settingsFrame,
            range=(1, 25),
            pageSize=1,
            scale=0.2,
            thumb_frameSize=(-0.05, 0.05, -0.08, 0.08),
            thumb_relief=DGG.FLAT,
            thumb_geom=None,
            thumb_frameColor=(0.2, 0.3, 1, 1),
            pos=(0.25, 0, 0.175),
            command=updateGuiValues,
        )

        self.droneNumTitle = OnscreenText(
            text=f"Number of Drones:",
            parent=self.settingsFrame,
            scale=0.03,
            pos=(0.25, 0.05),
            fg=(1, 1, 1, 1),
            font=self.loader.loadFont("src/fonts/sector_034.ttf"),
        )
        self.droneNum = DirectEntry(
            parent=self.settingsFrame,
            scale=0.05,
            pos=(0.05, 0, -0.05),
            initialText="0",
            cursorKeys=True,
            focusOutCommand=updateGuiValues,
        )

        self.droneHealthTitle = OnscreenText(
            text=f"Drone Hit Points: 1",
            parent=self.settingsFrame,
            scale=0.03,
            pos=(0.25, -0.225),
            fg=(1, 1, 1, 1),
            font=self.loader.loadFont("src/fonts/sector_034.ttf"),
        )
        self.droneHealthSlider = DirectSlider(
            parent=self.settingsFrame,
            range=(1, 50),
            pageSize=1,
            scale=0.2,
            thumb_frameSize=(-0.05, 0.05, -0.08, 0.08),
            thumb_relief=DGG.FLAT,
            thumb_geom=None,
            thumb_frameColor=(0.2, 0.3, 1, 1),
            pos=(0.25, 0, -0.3),
            command=updateGuiValues,
        )
        self.serverIpTitle = OnscreenText(
            text=f"Server IP",
            parent=self.settingsFrame,
            scale=0.03,
            pos=(0.25, -0.45),
            fg=(1, 1, 1, 1),
            font=self.loader.loadFont("src/fonts/sector_034.ttf"),
        )


class GUI:
    def start(self, render, _main, TransparencyAttrib, _monitor):
        self.guiFrame = DirectFrame(parent=render)
        self.render = render
        self.main = _main
        self.TransparencyAttrib = TransparencyAttrib
        global main, guiClass, monitor
        monitor = _monitor
        main = _main
        guiClass = self

    def setup(self):
        t.sleep(0.1)
        self.main.guiOverlay = OnscreenImage(
            parent=self.guiFrame,
            image="src/textures/raw/GUI_MAIN_1.png",
            scale=(1, 1, 1),
            pos=(0, 0, 0),
        )
        self.main.guiOverlay.setTransparency(self.TransparencyAttrib.MAlpha)
        self.main.guiOverlay.setBin("background", 0)
        self.main.guiOverlay.hide()

        self.main.HpIndicatorOutlineFrame = DirectFrame(
            parent=self.guiFrame,
            frameSize=(-0.55, 0.55, -0.05, 0.05),
            frameColor=(0.1, 0.1, 0.1, 0.8),
            pos=(-0.015, 1, 0.9175),
        )
        self.main.HpIndicator = DirectWaitBar(
            parent=self.guiFrame,
            value=60,
            range=100,
            scale=(0.525, 1, 0.33),
            pos=(-0.015, 1, 0.9175),
            barColor=(0, 0, 1, 1),
        )
        self.main.HpIndicatorOutlineFrame.setBin("background", 0)
        t.sleep(0.3)
        self.main.droneCountFrame = DirectFrame(
            parent=self.guiFrame,
            frameSize=(-0.15, 0.15, -0.04, 0.04),
            frameColor=(0.1, 0.1, 0.1, 0.8),
            pos=(-0.75, 1, 0.9175),
        )
        self.main.droneCountFrame.setBin("background", 0)
        self.main.droneCount = OnscreenText(
            text="Drones Remaining: -",
            pos=(-0.875, 0.91),
            parent=self.guiFrame,
            scale=(0.02 * (monitor[0].height / monitor[0].width), 0.02, 0.02),
            font=self.main.loader.loadFont("src/fonts/sector_034.ttf"),
            align=TextNode.ALeft,
            fg=(1, 1, 1, 1),
        )
        self.main.droneCount.hide()
        t.sleep(0.3)
        self.main.displayOverlay = DirectFrame(parent=self.guiFrame)
        self.main.droneTargetIndicator = DirectFrame(parent=self.main.displayOverlay)
        self.main.droneTargetList = []

    def miniMap(self):
        t.sleep(0.1)
        self.mapFrame = DirectFrame(
            parent=guiClass.guiFrame,
            pos=(0.9, 1, 0.9),
            scale=(0.3),
        )
        self.mapGeom = main.loader.loadModel("src/models/circle_grid/mesh.bam")
        self.mapGeom.reparentTo(self.mapFrame)
        self.mapGeom.setHpr(0, 90, 0)
        self.mapGeom.setScale(
            0.025 / (monitor[0].width / monitor[0].height),
            0.025 / (monitor[0].width / monitor[0].height),
            0.025,
        )
        self.mapGeom.hide()
