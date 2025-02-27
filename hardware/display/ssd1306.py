"""
MicroPython Tesla Coil Controller (MPTCC)
by Cameron Prince
teslauniverse.com

hardware/display/ssd1306.py
Display sub-class for interfacing with SSD1306 library.
"""

from .display import Display
from ...hardware.init import init
from machine import Pin

class SSD1306(Display):
    """
    A class to interface with the SSD1306 display driver for the 
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
        The SSD1306 display driver instance.
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
        Constructs all the necessary attributes for the SSD1306 object.
        """
        super().__init__()
        self.init = init

        if self.init.DISPLAY_INTERFACE == "i2c_2":
            self.init.init_i2c_2()
            from ssd1306 import SSD1306_I2C as driver
            self.driver = driver(
                self.DISPLAY_WIDTH,
                self.DISPLAY_HEIGHT,
                i2c=self.init.i2c_2,
                addr=self.init.DISPLAY_I2C_ADDR,
            )
            self.mutex = self.init.i2c_2_mutex
        elif self.init.DISPLAY_INTERFACE == "spi_1":
            self.init.init_spi_1()
            from ssd1306 import SSD1306_SPI as driver
            self.driver = driver(
                self.DISPLAY_WIDTH,
                self.DISPLAY_HEIGHT,
                spi = self.init.spi_1,
                dc = Pin(self.init.PIN_SPI_1_DC),
                res = Pin(self.init.PIN_SPI_1_RST),
                cs = Pin(self.init.PIN_SPI_1_CS),
            )
        elif self.init.DISPLAY_INTERFACE == "spi_2":
            self.init.init_spi_2()
            from ssd1306 import SSD1306_SPI as driver
            self.driver = driver(
                self.DISPLAY_WIDTH,
                self.DISPLAY_HEIGHT,
                spi = self.init.spi_2,
                dc = Pin(self.init.PIN_SPI_2_DC),
                res = Pin(self.init.PIN_SPI_2_RST),
                cs = Pin(self.init.PIN_SPI_2_CS),
            )
        else:
            self.init.init_i2c_1()
            from ssd1306 import SSD1306_I2C as driver
            self.driver = driver(
                self.DISPLAY_WIDTH,
                self.DISPLAY_HEIGHT,
                i2c=self.init.i2c_1,
                addr=self.init.DISPLAY_I2C_ADDR,
            )
            self.mutex = self.init.i2c_1_mutex

        self.width = self.DISPLAY_WIDTH
        self.height = self.DISPLAY_HEIGHT

    def clear(self):
        """
        Clears the display.
        """
        self.driver.fill(0)

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
        self.driver.text(text, w, h, f)

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
        self.driver.hline(x, y, w, c)

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
        self.driver.fill_rect(x, y, w, h, c)

    def show(self):
        """
        Updates the display with the current frame buffer content.
        """
        self.driver.show()
