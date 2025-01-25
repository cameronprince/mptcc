"""
MicroPython Tesla Coil Controller (MPTCC)
by Cameron Prince
teslauniverse.com

hardware/rgb_led/pca9685.py
RGB LED device utilizing the PCA9685 external PWM board.
"""

import time
from ..rgb_led.rgb_led import RGBLED
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

        self.init.rgb_led = [
            # RGB(self.driver, red_channel=self.PCA_LED1_RED, green_channel=self.PCA_LED1_GREEN, blue_channel=self.PCA_LED1_BLUE),
            # RGB(self.driver, red_channel=self.PCA_LED2_RED, green_channel=self.PCA_LED2_GREEN, blue_channel=self.PCA_LED2_BLUE),
            # RGB(self.driver, red_channel=self.PCA_LED3_RED, green_channel=self.PCA_LED3_GREEN, blue_channel=self.PCA_LED3_BLUE),
            # RGB(self.driver, red_channel=self.PCA_LED4_RED, green_channel=self.PCA_LED4_GREEN, blue_channel=self.PCA_LED4_BLUE),
        ]
