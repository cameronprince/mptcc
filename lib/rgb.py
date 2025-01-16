"""
MicroPython Tesla Coil Controller (MPTCC)
by Cameron Prince

rgb.py
Provides functions for controlling RGB LED colors.
Based in part on https://github.com/alex27riva/picoRGB
"""

class RGB:
    """
    A class to represent and control RGB LED colors using the PCA9685 PWM driver.

    Attributes:
    -----------
    pca : PCA9685
        The PCA9685 PWM driver instance.
    red_channel : int
        The PWM channel for the red LED.
    green_channel : int
        The PWM channel for the green LED.
    blue_channel : int
        The PWM channel for the blue LED.
    red_val : int
        The intensity value for the red LED (default is 0).
    green_val : int
        The intensity value for the green LED (default is 0).
    blue_val : int
        The intensity value for the blue LED (default is 0).
    """

    def __init__(self, pca, red_channel, green_channel, blue_channel, red_val=0, green_val=0, blue_val=0):
        """
        Constructs all the necessary attributes for the RGB object and sets the initial color.

        Parameters:
        ----------
        pca : PCA9685
            The PCA9685 PWM driver instance.
        red_channel : int
            The PWM channel for the red LED.
        green_channel : int
            The PWM channel for the green LED.
        blue_channel : int
            The PWM channel for the blue LED.
        red_val : int
            The initial intensity value for the red LED (default is 0).
        green_val : int
            The initial intensity value for the green LED (default is 0).
        blue_val : int
            The initial intensity value for the blue LED (default is 0).
        """
        self.pca = pca
        self.red_channel = red_channel
        self.green_channel = green_channel
        self.blue_channel = blue_channel
        self.red_val = red_val
        self.green_val = green_val
        self.blue_val = blue_val
        self.setColor(red_val, green_val, blue_val)

    def map(self, x, in_min, in_max, out_min, out_max):
        """
        Handles value conversion from one range to another.

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

    def setColor(self, r, g, b):
        """
        Sets the color of the LED by updating the PWM values for the red, green, and blue channels.

        Parameters:
        ----------
        r : int
            The intensity value for the red LED (0-255).
        g : int
            The intensity value for the green LED (0-255).
        b : int
            The intensity value for the blue LED (0-255).
        """
        self.red_val = r
        self.green_val = g
        self.blue_val = b
        r = self.map(r, 0, 255, 0, 4095)
        g = self.map(g, 0, 255, 0, 4095)
        b = self.map(b, 0, 255, 0, 4095)
        self.pca.duty(self.red_channel, r)
        self.pca.duty(self.green_channel, g)
        self.pca.duty(self.blue_channel, b)

    def status_color(self, value, mode="percentage"):
        """
        Sets the color of the LED based on a value.

        Parameters:
        ----------
        value : int
            The value to determine the color (0-100 for percentage mode, 0-127 for velocity mode).
        mode : str
            The mode to interpret the value ("percentage" or "velocity").
        """
        if mode == "percentage":
            if value <= 50:
                red = self.map(value, 0, 50, 0, 255)
                green = 255
                blue = 0
            else:
                red = 255
                green = self.map(100 - value, 0, 50, 0, 255)
                blue = 0
        elif mode == "velocity":
            red = self.map(value, 0, 127, 0, 255)
            green = self.map(127 - value, 0, 127, 0, 255)
            blue = 0
        self.setColor(red, green, blue)