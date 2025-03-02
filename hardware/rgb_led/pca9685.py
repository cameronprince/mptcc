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

        # Dynamically initialize RGB LEDs based on NUMBER_OF_COILS.
        self.init.rgb_led = []
        for i in range(1, self.init.NUMBER_OF_COILS + 1):
            # Dynamically get the RGB channel configurations for the current coil.
            red_attr = f"RGB_PCA9685_LED{i}_RED"
            green_attr = f"RGB_PCA9685_LED{i}_GREEN"
            blue_attr = f"RGB_PCA9685_LED{i}_BLUE"

            if not hasattr(self.init, red_attr) or \
               not hasattr(self.init, green_attr) or \
               not hasattr(self.init, blue_attr):
                raise ValueError(
                    f"RGB LED configuration for PCA9685 {i} is missing. "
                    f"Please ensure {red_attr}, {green_attr}, and {blue_attr} are defined in main."
                )

            red_channel = getattr(self.init, red_attr)
            green_channel = getattr(self.init, green_attr)
            blue_channel = getattr(self.init, blue_attr)

            # Initialize the RGB_PCA9685 instance.
            self.init.rgb_led.append(RGB_PCA9685(
                self.driver,
                red_channel=red_channel,
                green_channel=green_channel,
                blue_channel=blue_channel,
                mutex=self.mutex,
            ))

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
