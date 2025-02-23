"""
MicroPython Tesla Coil Controller (MPTCC)
by Cameron Prince
teslauniverse.com

hardware/rgb_led/rgb_led.py
Parent class for RGB LEDs.
"""

import time
from ..hardware import Hardware
from ...lib import utils

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

    def status_color(self, frequency, on_time, max_duty, max_on_time):
        """
        Sets the color of the LED based on a value and mode.
        """
        try:
            if max_duty and max_on_time:
                value = utils.calculate_percent(frequency, on_time, max_duty, max_on_time)
            else:
                # MIDI signal constraints are fixed at 0-127 by the standard.
                value = utils.calculate_midi_percent(frequency, on_time)
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
        except OSError as e:
            print(f"Error updating RGB LED: {e}")
            # Optionally, log the error or take other corrective actions
