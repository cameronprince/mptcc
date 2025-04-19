"""
MicroPython Tesla Coil Controller (MPTCC)
by Cameron Prince
teslauniverse.com

hardware/display/ssd1322.py
Display sub-class for interfacing with SSD1322 library.
"""

from machine import Pin
from .display import Display
from ssd1322 import Display as driver
from ...hardware.init import init

class SSD1322(Display):
    """
    A class to interface with the SSD1322 display driver for the 
    MicroPython Tesla Coil Controller (MPTCC).
    """

    DISPLAY_WIDTH = 256
    DISPLAY_HEIGHT = 64
    DISPLAY_FONT_HEIGHT = 8
    # DISPLAY_LINE_HEIGHT = 12
    # DISPLAY_FONT_WIDTH = 8
    # DISPLAY_HEADER_HEIGHT = 10
    # DISPLAY_ITEMS_PER_PAGE = 4

    def __init__(self, config):
        """
        Constructs all the necessary attributes for the SSD1322 object.
        """
        super().__init__()
        self.spi_instance = config.get("spi_instance", None)
        self.init = init

        if self.spi_instance is None:
            raise ValueError("SPI instance must be provided.")

        if self.spi_instance == 2:
            init.init_spi_2()
            self.dc = Pin(self.init.PIN_SPI_2_DC, Pin.OUT)
            self.cs = Pin(self.init.PIN_SPI_2_CS, Pin.OUT)
            self.rst = Pin(self.init.PIN_SPI_2_RST, Pin.OUT)
            self.spi = self.init.spi_2
        else:
            init.init_spi_1()
            self.dc = Pin(self.init.PIN_SPI_1_DC, Pin.OUT)
            self.cs = Pin(self.init.PIN_SPI_1_CS, Pin.OUT)
            self.rst = Pin(self.init.PIN_SPI_1_RST, Pin.OUT)
            self.spi = self.init.spi_1

        self.driver = driver(self.spi, dc=self.dc, cs=self.cs, rst=self.rst)
        self.width = self.DISPLAY_WIDTH
        self.height = self.DISPLAY_HEIGHT

        print(f"SSD1322 display driver initialized on SPI{self.spi_instance}")

    def _clear(self):
        """
        Clears the display.
        """
        self.driver.clear()

    def _clamp_y(self, y, height=0):
        """
        Clamps the y-coordinate to ensure the object fits within the display bounds.

        Parameters:
        ----------
        y : int
            The y-coordinate to clamp.
        height : int
            The height of the object being drawn (default: 0).

        Returns:
        -------
        int
            The clamped y-coordinate.
        """
        max_y = self.DISPLAY_HEIGHT - height - 1  # Subtract 1 to ensure the object fits
        clamped_y = max(0, min(y, max_y))
        return clamped_y

    def _text(self, text, w, h, c):
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
        c : int
            The font color (0 or 1).
        """
        h = self._clamp_y(h, self.DISPLAY_FONT_HEIGHT)
        if c > 0:
            c = 15
        self.driver.draw_text8x8(w, h, text, c)

    def _hline(self, x, y, w, c):
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
        y = self._clamp_y(y)
        if c > 0:
            c = 15
        self.driver.draw_hline(x, y, w, c)

    def _fill_rect(self, x, y, w, h, c):
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
        y = self._clamp_y(y, h)
        # Ensure the rectangle does not exceed the display height.
        max_height = self.DISPLAY_HEIGHT - y
        h = min(h, max_height)

        if c > 0:
            c = 15
        self.driver.fill_rectangle(x, y, w, h, c)

    def _show(self):
        """
        Updates the display with the current frame buffer content.
        """
        self.driver.present()
