"""
MicroPython Tesla Coil Controller (MPTCC)
by Cameron Prince
teslauniverse.com

hardware/rgb_led/rgb_led.py
Parent class for RGB LEDs.
"""

import math
from ..hardware import Hardware

class RGBLED(Hardware):
    """
    Parent class for RGB LEDs.
    """
    def __init__(self):
        super().__init__()

import math

class RGB:
    """
    A base class for RGB LED functionality.
    """

    def make_color(self, value):
        """
        Return RGB color from scalar value.

        Parameters:
        ----------
        value : float
            Scalar value between 0 and 1

        Returns:
        -------
        tuple
            RGB values.
        """
        # value must be between [0, 510].
        value = max(0, min(1, value)) * 510

        if value < 255:
            red_value = int((value / 255) ** 2 * 255)
            green_value = 255
        else:
            green_value = 256 - int((value - 255) ** 2 / 255)
            red_value = 255

        return red_value, green_value, 0

    def constrain(self, x, out_min, out_max):
        """
        Constrains a value to be within a specified range.

        Parameters:
        ----------
        x : int
            The value to be constrained.
        out_min : int
            The minimum value of the range.
        out_max : int
            The maximum value of the range.

        Returns:
        -------
        int
            The constrained value.
        """
        return max(out_min, min(x, out_max))

    def show(self):
        """
        Displays the current LED status by printing the channel numbers and their respective values.
        """
        print("LED channels ({}, {}, {}), Current values ({}, {}, {})".format(
            self.red_channel, self.green_channel, self.blue_channel,
            self.red_val, self.green_val, self.blue_val))

    def off(self):
        """
        Turns off the LED by setting its color to (0, 0, 0).
        """
        self.setColor(0, 0, 0)

    def status_color(self, value, mode="percent"):
        """
        Sets the color of the LED based on a value and mode.

        Parameters:
        ----------
        value : int
            The value to determine the color (1-100 for percent, 0-127 for velocity).
        mode : str
            The mode to interpret the value ("percent" or "velocity").
        """
        # Convert velocity to percentage if in velocity mode
        if mode == "velocity":
            value = int(value * 100 / 127)

        # Ensure value is between 1 and 100.
        value = self.constrain(value, 1, 100)

        # Map value to a range of 0 to 1.
        normalized_value = value / 100.0

        # Get color based on the normalized value.
        red, green, blue = self.make_color(normalized_value)

        red = self.constrain(red, 0, 255)
        green = self.constrain(green, 0, 255)
        blue = self.constrain(blue, 0, 255)

        self.setColor(red, green, blue)

class RGB_I2CEncoder(RGB):
    """
    A class for handling RGB LEDs with an I2C Encoder.
    """
    def __init__(self, encoder):
        super().__init__()
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
        self.encoder.writeRGBCode(color_code)

class RGB_PCA9685(RGB):
    """
    A class for handling RGB LEDs with a PCA9685 driver.
    """
    def __init__(self, pca, red_channel, green_channel, blue_channel):
        super().__init__()
        self.pca = pca
        self.red_channel = red_channel
        self.green_channel = green_channel
        self.blue_channel = blue_channel
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
        self.pca.duty(self.red_channel, r * 16)
        self.pca.duty(self.green_channel, g * 16)
        self.pca.duty(self.blue_channel, b * 16)