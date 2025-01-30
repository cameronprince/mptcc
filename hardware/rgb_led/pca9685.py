"""
MicroPython Tesla Coil Controller (MPTCC)
by Cameron Prince
teslauniverse.com

hardware/rgb_led/pca9685.py
RGB LED device utilizing the PCA9685 external PWM board.
"""

import time
from machine import Pin
from pca9685 import PCA9685 as driver
from ..rgb_led.rgb_led import RGBLED, RGB_PCA9685
from ...hardware.init import init

class PCA9685(RGBLED):
    """
    A class to control RGB LED devices using the PCA9685 external PWM board.

    Attributes:
    -----------
    init : object
        The initialization object containing configuration and hardware settings.
    driver : PCA9685
        The PCA9685 PWM driver instance.
    """

    # RGB LED to PCA9685 channel assignments.
    PCA_LED1_RED = 0
    PCA_LED1_GREEN = 1
    PCA_LED1_BLUE = 2

    PCA_LED2_RED = 3
    PCA_LED2_GREEN = 4
    PCA_LED2_BLUE = 5

    PCA_LED3_RED = 6
    PCA_LED3_GREEN = 7
    PCA_LED3_BLUE = 8

    PCA_LED4_RED = 9
    PCA_LED4_GREEN = 10
    PCA_LED4_BLUE = 11

    # Miscellaneous settings.
    PCA9685_FREQ = 1000

    def __init__(self):
        """
        Constructs all the necessary attributes for the PCA9685 object.
        """
        super().__init__()
        self.init = init

        # Prepare the I2C bus.
        self.init.init_i2c_2()
        self.driver = driver(self.init.i2c_2)
        self.driver.freq(self.PCA9685_FREQ)

        self.init.rgb_led = [
            RGB_PCA9685(self.driver, red_channel=self.PCA_LED1_RED, green_channel=self.PCA_LED1_GREEN, blue_channel=self.PCA_LED1_BLUE),
            RGB_PCA9685(self.driver, red_channel=self.PCA_LED2_RED, green_channel=self.PCA_LED2_GREEN, blue_channel=self.PCA_LED2_BLUE),
            RGB_PCA9685(self.driver, red_channel=self.PCA_LED3_RED, green_channel=self.PCA_LED3_GREEN, blue_channel=self.PCA_LED3_BLUE),
            RGB_PCA9685(self.driver, red_channel=self.PCA_LED4_RED, green_channel=self.PCA_LED4_GREEN, blue_channel=self.PCA_LED4_BLUE),
        ]
