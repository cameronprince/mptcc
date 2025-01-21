from pca9685 import PCA9685 as driver
from ..rgb_led.rgb_led import RGBLED
from ...lib.rgb import RGB
from ... import init
from machine import Pin
import time

class PCA9685(RGBLED):
    
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
        super().__init__()
        self.init = init.init

        # Prepare the I2C bus.
        self.init.init_i2c_2()
        self.driver = driver(self.init.i2c_2)
        self.driver.freq(self.PCA9685_FREQ)

        self.init.rgb_led = [
            RGB(self.driver, red_channel=self.PCA_LED1_RED, green_channel=self.PCA_LED1_GREEN, blue_channel=self.PCA_LED1_BLUE),
            RGB(self.driver, red_channel=self.PCA_LED2_RED, green_channel=self.PCA_LED2_GREEN, blue_channel=self.PCA_LED2_BLUE),
            RGB(self.driver, red_channel=self.PCA_LED3_RED, green_channel=self.PCA_LED3_GREEN, blue_channel=self.PCA_LED3_BLUE),
            RGB(self.driver, red_channel=self.PCA_LED4_RED, green_channel=self.PCA_LED4_GREEN, blue_channel=self.PCA_LED4_BLUE),
        ]

        # self.init.rgb_led[1].status_color(1)

