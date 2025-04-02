"""
MicroPython Tesla Coil Controller (MPTCC)
by Cameron Prince
teslauniverse.com

hardware/rgb_led/rgb_led.py
Parent class for RGB LEDs.
"""

from ...lib.utils import status_color
from ..hardware import Hardware


class RGBLED(Hardware):
    """
    Parent class for RGB LED hardware.
    """
    def __init__(self):
        super().__init__()

class RGB:
    """
    A base class for RGB LED functionality.
    """
    def off(self, output=None):
        """
        Turns off the LED by setting its color to (0, 0, 0).
        """
        color = (0, 0, 0)
        if output is not None and self.init.RGB_LED_ASYNCIO_POLLING:
            self.init.rgb_led_color[output] = color
        else:
            self.set_color(*color)

    def set_status(self, output, freq, on_time, max_duty=None, max_on_time=None):
        """
        Calculates the RGB color based on frequency, on_time, and optional constraints.
        Optionally scales the color to the full brightness if the child class supports it.

        Parameters:
        ----------
        output: int
            The index of the output for which the LED should be updated.
        freq : int
            The frequency of the signal.
        on_time : int
            The on time of the signal in microseconds.
        max_duty : int, optional
            The maximum duty cycle.
        max_on_time : int, optional
            The maximum on time.
        """
        # Calculate the color based on frequency, on_time, etc.
        color = status_color(freq, on_time, max_duty, max_on_time)

        # Scale the color to the full brightness if the child class has a custom full_brightness.
        if hasattr(self, 'full_brightness') and self.full_brightness != 255:
            r, g, b = color
            scaled_r = r * self.full_brightness // 255
            scaled_g = g * self.full_brightness // 255
            scaled_b = b * self.full_brightness // 255
            color = (scaled_r, scaled_g, scaled_b)

        # Set the LED color.
        if self.init.RGB_LED_ASYNCIO_POLLING:
            self.init.rgb_led_color[output] = color
        else:
            self.set_color(*color)

    def get_color_gradient(self, color1, color2, steps):
        """
        Generate a color gradient between two colors.
        """
        gradient = []
        for i in range(steps):
            ratio = i / float(steps)
            red = int(color1[0] * (1 - ratio) + color2[0] * ratio)
            green = int(color1[1] * (1 - ratio) + color2[1] * ratio)
            blue = int(color1[2] * (1 - ratio) + color2[2] * ratio)
            gradient.append((red, green, blue))
        return gradient

    def generate_vu_colors(self, num_leds):
        """
        Generate the VU meter colors for an LED array.
        """
        # Define the base VU meter colors.
        vu_colors = [
            (0, 255, 0),    # Green.
            (85, 255, 0),   # Yellow-green.
            (170, 255, 0),  # Yellow.
            (255, 170, 0),  # Yellow-orange.
            (255, 85, 0),   # Orange.
            (255, 0, 0)     # Red.
        ]

        vu_meter_colors = []
        for i in range(len(vu_colors) - 1):
            steps = num_leds // (len(vu_colors) - 1)
            gradient = self.get_color_gradient(vu_colors[i], vu_colors[i + 1], steps)
            vu_meter_colors.extend(gradient)

        # Ensure the list has exactly num_leds colors.
        if len(vu_meter_colors) < num_leds:
            vu_meter_colors.extend([vu_colors[-1]] * (num_leds - len(vu_meter_colors)))

        return vu_meter_colors
