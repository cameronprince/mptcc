"""
MicroPython Tesla Coil Controller (MPTCC)
by Cameron Prince
teslauniverse.com

hardware/display/ssh1122.py
Display sub-class for interfacing with SH1122 library.
"""

from machine import Pin
from .display import Display
from sh1122 import SH1122_SPI as driver
from ...hardware.init import init


class SSH1122(Display):
    """
    A class to interface with the SH1122 display driver for the
    MicroPython Tesla Coil Controller (MPTCC).
    """

    DISPLAY_WIDTH = 256
    DISPLAY_HEIGHT = 64
    DISPLAY_FONT_WIDTH = 8
    DISPLAY_FONT_HEIGHT = 8
    DISPLAY_LINE_HEIGHT = 12
    DISPLAY_HEADER_HEIGHT = 10
    DISPLAY_ITEMS_PER_PAGE = 2  # Matches two rows visible in assignment screen

    def __init__(self, config):
        """
        Constructs all the necessary attributes for the SSH1122 object.

        Parameters:
        ----------
        config : dict
            Configuration dictionary containing SPI instance and pin settings.
        """
        super().__init__()
        self.spi_instance = config.get("spi_instance", None)
        self.init = init

        if self.spi_instance is None:
            raise ValueError("SPI instance must be provided.")

        if self.spi_instance == 2:
            self.init.init_spi_2()
            self.dc = Pin(self.init.PIN_SPI_2_DC, Pin.OUT)
            self.cs = Pin(self.init.PIN_SPI_2_CS, Pin.OUT)
            self.rst = Pin(self.init.PIN_SPI_2_RST, Pin.OUT)
            self.spi = self.init.spi_2
        else:
            self.init.init_spi_1()
            self.dc = Pin(self.init.PIN_SPI_1_DC, Pin.OUT)
            self.cs = Pin(self.init.PIN_SPI_1_CS, Pin.OUT)
            self.rst = Pin(self.init.PIN_SPI_1_RST, Pin.OUT)
            self.spi = self.init.spi_1

        self.driver = driver(
            width=self.DISPLAY_WIDTH,
            height=self.DISPLAY_HEIGHT,
            spi=self.spi,
            dc=self.dc,
            res=self.rst,  # SH1122 uses 'res' for reset
            cs=self.cs
        )
        self.width = self.DISPLAY_WIDTH
        self.height = self.DISPLAY_HEIGHT
        self.font_width = self.DISPLAY_FONT_WIDTH
        self.font_height = self.DISPLAY_FONT_HEIGHT
        self.line_height = self.DISPLAY_LINE_HEIGHT
        self.header_height = self.DISPLAY_HEADER_HEIGHT

        print(f"SH1122 display driver initialized on SPI{self.spi_instance}")

    def _clear(self):
        """
        Clears the display.
        """
        self.driver.fill(0)

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
        return max(0, min(y, max_y))

    def _text(self, text, x, y, c):
        """
        Displays text on the screen.

        Parameters:
        ----------
        text : str
            The text to display.
        x : int
            The x-coordinate for the text.
        y : int
            The y-coordinate for the text.
        c : int
            The font color (0 or 1).
        """
        y = self._clamp_y(y, self.DISPLAY_FONT_HEIGHT)
        if c > 0:
            c = 15  # Maximum grayscale intensity
        self.driver.text(text, x, y, c)

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
        self.driver.fill_rect(x, y, w, 1, c)

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
        max_height = self.DISPLAY_HEIGHT - y
        h = min(h, max_height)
        if c > 0:
            c = 15
        self.driver.fill_rect(x, y, w, h, c)

    def _show(self):
        """
        Updates the display with the current frame buffer content.
        """
        self.driver.show()

    def center_text(self, text, y, c=1):
        """
        Displays centered text on the screen.

        Parameters:
        ----------
        text : str
            The text to display.
        y : int
            The y-coordinate for the text.
        c : int
            The font color (0 or 1, default: 1).
        """
        text_width = len(text) * self.DISPLAY_FONT_WIDTH
        x = max(0, (self.DISPLAY_WIDTH - text_width) // 2)
        self._text(text, x, y, c)

    def header(self, text):
        """
        Displays a header at the top of the screen.

        Parameters:
        ----------
        text : str
            The header text to display.
        """
        self._fill_rect(0, 0, self.DISPLAY_WIDTH, self.DISPLAY_HEADER_HEIGHT, 0)
        self.center_text(text, 1, 1)

    def loading_screen(self):
        """
        Displays a loading screen.
        """
        self._clear()
        self.center_text("Loading...", self.DISPLAY_HEIGHT // 2 - self.DISPLAY_FONT_HEIGHT // 2, 1)
        self._show()

    def alert_screen(self, text):
        """
        Displays an alert screen with the specified text.

        Parameters:
        ----------
        text : str
            The alert text to display.
        """
        self._clear()
        self.center_text(text, self.DISPLAY_HEIGHT // 2 - self.DISPLAY_FONT_HEIGHT // 2, 1)
        self._show()
