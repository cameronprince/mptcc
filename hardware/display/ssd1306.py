"""
MicroPython Tesla Coil Controller (MPTCC)
by Cameron Prince
teslauniverse.com

hardware/display/ssd1306.py
Display sub-class for interfacing with SSD1306 library.
"""
from .display import Display
from ssd1306 import SSD1306_I2C as driver
from ... import init

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

        self.init = init.init
        self.driver = driver(
            Init.DISPLAY_WIDTH,
            Init.DISPLAY_HEIGHT,
            self.init.i2c_1,
        )


