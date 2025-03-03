"""
MicroPython Tesla Coil Controller (MPTCC)
by Cameron Prince
teslauniverse.com

hardware/rgb_led/rgb_led.py
Parent class for RGB LEDs.
"""

from ...lib.utils import status_color
from ..hardware import Hardware

class RGBLED(Hardware):
    """
    Parent class for RGB LED hardware.
    """
    def __init__(self):
        super().__init__()

class RGB:
    """
    A base class for RGB LED functionality.
    """
    def off(self, output=None):
        """
        Turns off the LED by setting its color to (0, 0, 0).
        """
        color = (0, 0, 0)
        if output is not None and self.init.RGB_LED_ASYNCIO_POLLING:
            self.init.rgb_led_color[output] = (color)
        else:
            self.setColor(*color)

    def set_status(self, output, frequency, on_time, max_duty=None, max_on_time=None):
        """
        Calculates the RGB color based on frequency, on_time, and optional constraints.

        Parameters:
        ----------
        output: int
            The index of the output for which the LED should be updated.
        frequency : int
            The frequency of the signal.
        on_time : int
            The on time of the signal in microseconds.
        max_duty : int, optional
            The maximum duty cycle.
        max_on_time : int, optional
            The maximum on time.
        """
        color = status_color(frequency, on_time, max_duty, max_on_time)
        if self.init.RGB_LED_ASYNCIO_POLLING:
            self.init.rgb_led_color[output] = color
        else:
            self.setColor(*color)