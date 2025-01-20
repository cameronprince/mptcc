from ..hardware import Hardware
from .display import Display
from ssd1309 import Display as driver

class SSD1309(Display):

    DISPLAY_WIDTH = 128
    DISPLAY_HEIGHT = 64
    DISPLAY_LINE_HEIGHT = 12
    DISPLAY_FONT_WIDTH = 8
    DISPLAY_FONT_HEIGHT = 8
    DISPLAY_HEADER_HEIGHT = 10
    DISPLAY_ITEMS_PER_PAGE = 4

    def __init__(self, init):
        super().__init__()
        self.driver = driver(i2c=init.i2c, width=self.DISPLAY_WIDTH, height=self.DISPLAY_HEIGHT, flip=True)
        self.width = self.DISPLAY_WIDTH
        self.height = self.DISPLAY_HEIGHT

    def clear(self):
        self.driver.clear()

    def text(self, text, w, h, f):
        self.driver.monoFB.text(text, w, h, f)

    def hline(self, x, y, w, c):
        self.driver.monoFB.hline(x, y, w, c)

    def fill_rect(self, x, y, w, h, c):
        self.driver.monoFB.fill_rect(x, y, w, h, c)

    def show(self):
        self.driver.present()