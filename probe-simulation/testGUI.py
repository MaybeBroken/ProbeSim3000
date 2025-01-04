from src.scripts.display import GUI
from screeninfo import get_monitors

monitor = get_monitors()
from panda3d.core import *
from panda3d.core import (
    TransparencyAttrib,
    loadPrcFileData,
)
from direct.showbase.ShowBase import ShowBase

loadPrcFileData(
    "",
    f"win-size {monitor.copy()[0].width} {monitor.copy()[0].height}\nshow-frame-rate-meter 1\nframerate-meter-update-interval 0.5\n",
)


class main(ShowBase):
    def __init__(self):
        super().__init__()
        self.setBackgroundColor(0, 0, 0, 1)
        self.gui = GUI()
        self.gui.start(self.render2d, self, TransparencyAttrib, monitor)
        self.accept("q", exit)
        self.accept("escape", exit)
        self.gui.setup()


main().run()
