"""
MicroPython Tesla Coil Controller (MPTCC)
by Cameron Prince
teslauniverse.com

hardware/display/ssd1309.py
Display sub-class for interfacing with SSD1309 library.
"""

from .display import Display
from ssd1309 import Display as driver
from ... import init

class SSD1309(Display):
    """
    A class to interface with the SSD1309 display driver for the 
    MicroPython Tesla Coil Controller (MPTCC).

    Attributes:
    -----------
    DISPLAY_WIDTH : int
        The width of the display.
    DISPLAY_HEIGHT : int
        The height of the display.
    DISPLAY_LINE_HEIGHT : int
        The height of a line in the display.
    DISPLAY_FONT_WIDTH : int
        The width of a character in the display font.
    DISPLAY_FONT_HEIGHT : int
        The height of a character in the display font.
    DISPLAY_HEADER_HEIGHT : int
        The height of the header in the display.
    DISPLAY_ITEMS_PER_PAGE : int
        The number of items displayed per page.
    driver : driver
        The SSD1309 display driver instance.
    """

    DISPLAY_WIDTH = 128
    DISPLAY_HEIGHT = 64
    DISPLAY_LINE_HEIGHT = 12
    DISPLAY_FONT_WIDTH = 8
    DISPLAY_FONT_HEIGHT = 8
    DISPLAY_HEADER_HEIGHT = 10
    DISPLAY_ITEMS_PER_PAGE = 4

    def __init__(self):
        """
        Constructs all the necessary attributes for the SSD1309 object.
        """
        super().__init__()

        self.driver = driver(i2c=init.init.i2c_1, width=self.DISPLAY_WIDTH, height=self.DISPLAY_HEIGHT, flip=True)
        self.width = self.DISPLAY_WIDTH
        self.height = self.DISPLAY_HEIGHT

    def clear(self):
        """
        Clears the display.
        """
        self.driver.clear()

    def text(self, text, w, h, f):
        """
        Displays text on the screen.

        Parameters:
        ----------
        text : str
            The text to display.
        w : int
            The x-coordinate for the text.
        h : int
            The y-coordinate for the text.
        f : int
            The font color (0 or 1).
        """
        self.driver.monoFB.text(text, w, h, f)

    def hline(self, x, y, w, c):
        """
        Draws a horizontal line on the screen.

        Parameters:
        ----------
        x : int
            The x-coordinate of the start of the line.
        y : int
            The y-coordinate of the start of the line.
        w : int
            The width of the line.
        c : int
            The color of the line (0 or 1).
        """
        self.driver.monoFB.hline(x, y, w, c)

    def fill_rect(self, x, y, w, h, c):
        """
        Draws a filled rectangle on the screen.

        Parameters:
        ----------
        x : int
            The x-coordinate of the top-left corner of the rectangle.
        y : int
            The y-coordinate of the top-left corner of the rectangle.
        w : int
            The width of the rectangle.
        h : int
            The height of the rectangle.
        c : int
            The color of the rectangle (0 or 1).
        """
        self.driver.monoFB.fill_rect(x, y, w, h, c)

    def show(self):
        """
        Updates the display with the current frame buffer content.
        """
        self.driver.present()
