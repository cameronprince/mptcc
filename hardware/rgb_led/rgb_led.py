"""
MicroPython Tesla Coil Controller (MPTCC)
by Cameron Prince
teslauniverse.com

hardware/rgb_led/rgb_led.py
Parent class for RGB LEDs.
"""

from ..hardware import Hardware

class RGBLED(Hardware):
    """
    Parent class for RGB LEDs.
    """
    def __init__(self):
        super().__init__()

class RGB:
    """
    A base class for RGB LED functionality.
    """
    def map(self, x, in_min, in_max, out_min, out_max):
        """
        Converts a value from one range to another.

        Parameters:
        ----------
        x : int
            The value to be converted.
        in_min : int
            The minimum value of the input range.
        in_max : int
            The maximum value of the input range.
        out_min : int
            The minimum value of the output range.
        out_max : int
            The maximum value of the output range.

        Returns:
        -------
        int
            The converted value in the output range.
        """
        return (x - in_min) * (out_max - out_min) // (in_max - in_min) + out_min

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
        if x < out_min:
            return out_min
        elif x > out_max:
            return out_max
        else:
            return x

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

    def status_color(self, value):
        """
        Sets the color of the LED based on a percentage value.

        Parameters:
        ----------
        value : int
            The percentage value (1-100).
        """
        if value <= 50:
            red = self.map(value, 1, 50, 0, 255)
            green = 255
            blue = 0
        else:
            red = 255
            green = self.map(value, 50, 100, 255, 0)
            blue = 0

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
        r_mapped = self.map(r, 0, 255, 0, 4095)
        g_mapped = self.map(g, 0, 255, 0, 4095)
        b_mapped = self.map(b, 0, 255, 0, 4095)
        self.pca.duty(self.red_channel, r_mapped)
        self.pca.duty(self.green_channel, g_mapped)
        self.pca.duty(self.blue_channel, b_mapped)
