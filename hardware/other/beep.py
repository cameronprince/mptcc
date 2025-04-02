"""
MicroPython Tesla Coil Controller (MPTCC)
by Cameron Prince
teslauniverse.com

hardware/other/beep.py
Provides beep tone confirmation for inputs.
"""

import time
from machine import Pin
from ..init import init
from ..hardware import Hardware


class GPIO_Beep(Hardware):
    """
    A class to interact with a piezo element connected to a GPIO pin.
    """

    def __init__(self, pin, length_ms):
        """
        Constructs all the necessary attributes for the GPIO_Beep object.

        Parameters:
        ----------
        pin : int
            The GPIO pin number connected to the piezo element.
        length_ms : int
            The duration of the beep in milliseconds.
        """
        super().__init__()
        self.pin = Pin(pin, Pin.OUT)
        self.length_ms = length_ms
        init.beep = self

        print(f"Beep tone confirmation enabled (Pin: {pin})")

    def on(self):
        """
        Trigger a blocking beep for the specified duration.
        """
        self.pin.on()
        time.sleep_ms(self.length_ms)
        self.pin.off()
    