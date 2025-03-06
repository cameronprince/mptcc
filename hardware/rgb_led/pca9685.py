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

        # Print initialization details.
        print(f"PCA9685 RGB LED driver initialized on I2C_{self.init.RGB_PCA9685_I2C_INSTANCE} at address: 0x{self.init.RGB_PCA9685_ADDR:02X}")
        for i in range(self.init.NUMBER_OF_COILS):
            red_channel = getattr(self.init, f"RGB_PCA9685_LED{i + 1}_RED")
            green_channel = getattr(self.init, f"RGB_PCA9685_LED{i + 1}_GREEN")
            blue_channel = getattr(self.init, f"RGB_PCA9685_LED{i + 1}_BLUE")
            print(f"- LED {i + 1}: R={red_channel}, G={green_channel}, B={blue_channel}")
        print(f"- Asyncio polling: {self.init.RGB_LED_ASYNCIO_POLLING}")

        # Dynamically initialize RGB LEDs based on NUMBER_OF_COILS.
        self.init.rgb_led = [
            RGB_PCA9685(
                self.driver,
                red_channel=getattr(self.init, f"RGB_PCA9685_LED{i + 1}_RED"),
                green_channel=getattr(self.init, f"RGB_PCA9685_LED{i + 1}_GREEN"),
                blue_channel=getattr(self.init, f"RGB_PCA9685_LED{i + 1}_BLUE"),
                mutex=self.mutex,
            )
            for i in range(self.init.NUMBER_OF_COILS)
        ]


class RGB_PCA9685(RGB):
    """
    A class for handling RGB LEDs with a PCA9685 driver.
    """
    def __init__(self, driver, red_channel, green_channel, blue_channel, mutex):
        super().__init__()
        self.driver = driver
        self.red_channel = red_channel
        self.green_channel = green_channel
        self.blue_channel = blue_channel
        self.mutex = mutex
        self.init = init
        self.setColor(0, 0, 0)

    def setColor(self, r, g, b):
        """
        Sets the color of the RGB LED using the PCA9685 driver.
        If any channel (red, green, or blue) is None, it will be skipped.
        """
        self.init.mutex_acquire(self.mutex, "pca9685:set_color")
        try:
            if self.red_channel is not None:  # Skip if red channel is None
                self.driver.duty(self.red_channel, r * 16)
            if self.green_channel is not None:  # Skip if green channel is None
                self.driver.duty(self.green_channel, g * 16)
            if self.blue_channel is not None:  # Skip if blue channel is None
                self.driver.duty(self.blue_channel, b * 16)
        finally:
            self.init.mutex_release(self.mutex, "pca9685:set_color")
