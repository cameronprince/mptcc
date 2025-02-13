"""
MicroPython Tesla Coil Controller (MPTCC)
by Cameron Prince
teslauniverse.com

hardware/rgb_led/i2cencoder.py
I2CEncoder V2.1 RGB LED device.
"""

import time
from ..rgb_led.rgb_led import RGB, RGBLED
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

class RGB_I2CEncoder(RGB):
    """
    A class for handling RGB LEDs with an I2C Encoder.
    """
    def __init__(self, encoder):
        super().__init__()
        self.init = init
        self.encoder = encoder

    def setColor(self, r, g, b):
        """
        Sets the color of the RGB LED using the I2C Encoder.

        Parameters:
        ----------
        r : int
            Red value (0-255).
        g : int
            Green value (0-255).
        b : int
            Blue value (0-255).
        """
        color_code = (r << 16) | (g << 8) | b

        self.init.i2c_mutex.acquire()
        try:
            self.encoder.writeRGBCode(color_code)
        finally:
            self.init.i2c_mutex.release()
