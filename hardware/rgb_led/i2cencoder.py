"""
MicroPython Tesla Coil Controller (MPTCC)
by Cameron Prince
teslauniverse.com

hardware/rgb_led/rgb_led.py
Parent class for RGB LEDs.
"""

import time
from ..rgb_led.rgb_led import RGB, RGBLED
from ...lib.utils import status_color, hex_to_rgb
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
        self.encoders = self.init.encoder.encoders
        self.init.rgb_led = [RGB_I2CEncoder(encoder) for encoder in self.encoders]

class RGB_I2CEncoder(RGB):
    """
    A class for handling RGB LEDs with an I2C Encoder.
    """
    def __init__(self, encoder):
        super().__init__()
        self.init = init
        self.encoder = encoder

        if self.init.I2CENCODER_I2C_INSTANCE == 2:
            self.mutex = self.init.i2c_2_mutex
        else:
            self.mutex = self.init.i2c_1_mutex

        # Set default color and brightness values.
        self.default_color = hex_to_rgb(self.init.I2CENCODER_DEFAULT_COLOR)
        self.threshold_brightness = self.init.I2CENCODER_THRESHOLD_BRIGHTNESS
        self.full_brightness = self.init.I2CENCODER_FULL_BRIGHTNESS

    def setColor(self, r, g, b):
        """
        Sets the color of the RGB LED using the I2C Encoder.

        If the color is (0, 0, 0), the LEDs are set to the default color and threshold brightness.

        Parameters:
        ----------
        r : int
            Red value (0-255).
        g : int
            Green value (0-255).
        b : int
            Blue value (0-255).
        """
        # Check if the color is (0, 0, 0)
        if r == 0 and g == 0 and b == 0:
            # Use the default color and threshold brightness
            r, g, b = self.default_color
            dimmed_r = r * self.threshold_brightness // 255
            dimmed_g = g * self.threshold_brightness // 255
            dimmed_b = b * self.threshold_brightness // 255
            color_code = (dimmed_r << 16) | (dimmed_g << 8) | dimmed_b
        else:
            # Use the provided color
            color_code = (r << 16) | (g << 8) | b

        self.init.mutex_acquire(self.mutex, "i2cencoder:set_color")
        try:
            self.encoder.writeRGBCode(color_code)
        except OSError as e:
            print(f"I2CEncoder error: {e}")
        finally:
            self.init.mutex_release(self.mutex, "i2cencoder:set_color")

    def off(self, output=None):
        """
        Set the RGB LED to the default color and threshold brightness.
        """
        r, g, b = self.default_color
        dimmed_r = r * self.threshold_brightness // 255
        dimmed_g = g * self.threshold_brightness // 255
        dimmed_b = b * self.threshold_brightness // 255
        self.setColor(dimmed_r, dimmed_g, dimmed_b)

    def set_status(self, output, frequency, on_time, max_duty=None, max_on_time=None):
        """
        Calculates the RGB color based on frequency, on_time, and optional constraints.

        Parameters:
        ----------
        output: int
            The index of the output for which the LED should be updated.
        frequency : int
            The frequency of the signal.
        on_time : int
            The on time of the signal in microseconds.
        max_duty : int, optional
            The maximum duty cycle.
        max_on_time : int, optional
            The maximum on time.
        """
        # Calculate the color based on frequency, on_time, etc.
        color = status_color(frequency, on_time, max_duty, max_on_time)

        # Scale the color to the full brightness
        r, g, b = color
        scaled_r = r * self.full_brightness // 255
        scaled_g = g * self.full_brightness // 255
        scaled_b = b * self.full_brightness // 255

        # Set the LED color
        if self.init.RGB_LED_ASYNCIO_POLLING:
            self.init.rgb_led_color[output] = (scaled_r, scaled_g, scaled_b)
        else:
            self.setColor(scaled_r, scaled_g, scaled_b)
