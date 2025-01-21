from ..rgb_led.rgb_led import RGBLED
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


    def init_pca(self):
        """Initializes the external PWM driver."""
        self.init_i2c()
        self.deinit_pca()
        from pca9685 import PCA9685
        self.pca = PCA9685(self.i2c)
        self.pca.freq(Init.PCA9685_FREQ)

    def deinit_pca(self):
        """Shuts down the external PWM driver."""
        from pca9685 import PCA9685
        if isinstance(self.pca, PCA9685):
            self.pca.reset()

    def init_leds(self):
        """Initializes all the RGB LEDs on the external PWM driver."""
        self.init_pca()
        from mptcc.lib.rgb import RGB
        self.leds = [
            RGB(self.pca, red_channel=Init.PCA_LED1_RED, green_channel=Init.PCA_LED1_GREEN, blue_channel=Init.PCA_LED1_BLUE),
            RGB(self.pca, red_channel=Init.PCA_LED2_RED, green_channel=Init.PCA_LED2_GREEN, blue_channel=Init.PCA_LED2_BLUE),
            RGB(self.pca, red_channel=Init.PCA_LED3_RED, green_channel=Init.PCA_LED3_GREEN, blue_channel=Init.PCA_LED3_BLUE),
            RGB(self.pca, red_channel=Init.PCA_LED4_RED, green_channel=Init.PCA_LED4_GREEN, blue_channel=Init.PCA_LED4_BLUE)
        ]

