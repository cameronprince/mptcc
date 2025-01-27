"""
MicroPython Tesla Coil Controller (MPTCC)
by Cameron Prince
teslauniverse.com

hardware/rgb_led/i2cencoder.py
I2CEncoder V2.1 RGB LED device.
"""

import time
from ..rgb_led.rgb_led import RGBLED, RGB_I2CEncoder
from ...lib.rgb import RGB
from ...hardware.init import init

class I2CEncoder(RGBLED):
    """
    A class to control I2CEncoder V2.1 RGB LEDs.

    Attributes:
    -----------
    init : object
        The initialization object containing configuration and hardware settings.
    """

    def __init__(self):
        """
        Constructs all the necessary attributes for the I2CEncoder object.
        """
        super().__init__()
        self.init = init
        self.encoders = self.init.inputs.encoders
        self.init.rgb_led = [RGB_I2CEncoder(encoder) for encoder in self.encoders]