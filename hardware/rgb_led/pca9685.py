"""
MicroPython Tesla Coil Controller (MPTCC)
by Cameron Prince
teslauniverse.com

hardware/rgb_led/pca9685.py
RGB LED device utilizing the PCA9685 external PWM board.
"""

import _thread
from machine import Pin
from pca9685 import PCA9685 as driver
from ..rgb_led.rgb_led import RGBLED, RGB
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

    def __init__(self):
        """
        Constructs all the necessary attributes for the PCA9685 object.
        """
        super().__init__()
        self.init = init

        # Prepare the I2C bus.
        if self.init.RGB_PCA9685_I2C_INSTANCE == 2:
            self.init.init_i2c_2()
            self.i2c = self.init.i2c_2
            self.mutex = self.init.i2c_2_mutex
        else:
            self.init.init_i2c_1()
            self.i2c = self.init.i2c_1
            self.mutex = self.init.i2c_1_mutex

        # Initialize the PCA9685 driver.
        self.driver = driver(self.i2c, address=self.init.RGB_PCA9685_ADDR)
        self.driver.freq(self.init.RGB_PCA9685_FREQ)

        # Initialize RGB LEDs.
        self.init.rgb_led = [
            RGB_PCA9685(
                self.driver,
                red_channel=init.RGB_PCA9685_LED1_RED,
                green_channel=init.RGB_PCA9685_LED1_GREEN,
                blue_channel=init.RGB_PCA9685_LED1_BLUE,
                mutex=self.mutex,
            ),
            RGB_PCA9685(
                self.driver,
                red_channel=init.RGB_PCA9685_LED2_RED,
                green_channel=init.RGB_PCA9685_LED2_GREEN,
                blue_channel=init.RGB_PCA9685_LED2_BLUE,
                mutex=self.mutex,
            ),
            RGB_PCA9685(
                self.driver,
                red_channel=init.RGB_PCA9685_LED3_RED,
                green_channel=init.RGB_PCA9685_LED3_GREEN,
                blue_channel=init.RGB_PCA9685_LED3_BLUE,
                mutex=self.mutex,
            ),
            RGB_PCA9685(
                self.driver,
                red_channel=init.RGB_PCA9685_LED4_RED,
                green_channel=init.RGB_PCA9685_LED4_GREEN,
                blue_channel=init.RGB_PCA9685_LED4_BLUE,
                mutex=self.mutex,
            ),
        ]

class RGB_PCA9685(RGB):
    """
    A class for handling RGB LEDs with a PCA9685 driver.
    """
    def __init__(self, pca, red_channel, green_channel, blue_channel, mutex):
        super().__init__()
        self.init = init
        self.pca = pca
        self.red_channel = red_channel
        self.green_channel = green_channel
        self.blue_channel = blue_channel
        self.mutex = mutex
        self.setColor(0, 0, 0)

    def setColor(self, r, g, b):
        """
        Sets the color of the RGB LED using the PCA9685 driver.

        Parameters:
        ----------
        r : int
            Red value (0-255).
        g : int
            Green value (0-255).
        b : int
            Blue value (0-255).
        """
        self.init.mutex_acquire(self.mutex, "pca9685:set_color")
        # self.mutex.acquire()
        try:
            self.pca.duty(self.red_channel, r * 16)
            self.pca.duty(self.green_channel, g * 16)
            self.pca.duty(self.blue_channel, b * 16)
        finally:
            self.init.mutex_release(self.mutex, "pca9685:set_color")
            # self.mutex.release()
