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
    DISPLAY_LINE_HEIGHT = 12
    DISPLAY_FONT_WIDTH = 8
    DISPLAY_FONT_HEIGHT = 8
    DISPLAY_HEADER_HEIGHT = 10
    DISPLAY_ITEMS_PER_PAGE = 4
    interface = None

    def __init__(self):
        """
        Constructs all the necessary attributes for the SSD1322 object.
        """
        self.interface == 'spi'
        super().__init__()
        self.init = init

        init.init_spi_2()

        dc = Pin(self.init.PIN_SPI_2_DC, Pin.OUT)
        cs = Pin(self.init.PIN_SPI_2_CS, Pin.OUT)
        res = Pin(self.init.PIN_SPI_2_RST, Pin.OUT)

        self.driver = driver(self.init.spi_2, dc=dc, cs=cs, rst=res)
        self.width = self.DISPLAY_WIDTH
        self.height = self.DISPLAY_HEIGHT

        # Debugging: Print initialization details
        # print(f"SSD1322 initialized: width={self.width}, height={self.height}")

    def clear(self):
        """
        Clears the display.
        """
        # print("clear: Clearing display")
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
        # if clamped_y != y:
        #     print(f"_clamp_y: Clamped y={y} to {clamped_y} (height={height})")
        return clamped_y

    def text(self, text, w, h, c):
        """
        Displays text on the screen, ensuring the text fits within the display bounds.
        """
        h = self._clamp_y(h, self.DISPLAY_FONT_HEIGHT)
        if c > 0:
            c = 15
        # print(f"text: text='{text}', x={w}, y={h}, color={c}")
        self.driver.draw_text8x8(w, h, text, c)

    def hline(self, x, y, w, c):
        """
        Draws a horizontal line on the screen, ensuring the line fits within the display bounds.
        """
        y = self._clamp_y(y)
        if c > 0:
            c = 15
        # print(f"hline: x={x}, y={y}, width={w}, color={c}")
        self.driver.draw_hline(x, y, w, c)

    def fill_rect(self, x, y, w, h, c):
        """
        Draws a filled rectangle on the screen, ensuring the rectangle fits within the display bounds.
        """
        y = self._clamp_y(y, h)
        # Ensure the rectangle does not exceed the display height
        max_height = self.DISPLAY_HEIGHT - y
        h = min(h, max_height)
        
        # Debugging: Print the clamped values
        # print(f"fill_rect: x={x}, y={y}, width={w}, height={h}, color={c}")
        
        if c > 0:
            c = 15
        self.driver.fill_rectangle(x, y, w, h, c)

    def show(self):
        """
        Updates the display with the current frame buffer content.
        """
        # print("show: Updating display")
        self.driver.present()
