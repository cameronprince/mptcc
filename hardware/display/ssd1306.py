"""
MicroPython Tesla Coil Controller (MPTCC)
by Cameron Prince
teslauniverse.com

hardware/display/ssd1306.py
Display sub-class for interfacing with SSD1306 library.
"""
from .display import Display
from ssd1306 import SSD1306_I2C as driver
from ...hardware.init import init

class SSD1306(Display):

    DISPLAY_WIDTH = 128
    DISPLAY_HEIGHT = 64
    DISPLAY_LINE_HEIGHT = 12
    DISPLAY_FONT_WIDTH = 8
    DISPLAY_FONT_HEIGHT = 8
    DISPLAY_HEADER_HEIGHT = 10
    DISPLAY_ITEMS_PER_PAGE = 4

    def __init__(self):
        super().__init__()
        self.init = init
        self.driver = driver(self.DISPLAY_WIDTH, self.DISPLAY_HEIGHT, i2c=self.init.i2c_1)
        self.width = self.DISPLAY_WIDTH
        self.height = self.DISPLAY_HEIGHT

    def clear(self):
        self.driver.fill(0)

    def text(self, text, w, h, f):
        self.driver.text(text, w, h, f)

    def hline(self, x, y, w, c):
        self.driver.hline(x, y, w, c)

    def fill_rect(self, x, y, w, h, c):
        self.driver.fill_rect(x, y, w, h, c)

    def show(self):
        self.driver.show()