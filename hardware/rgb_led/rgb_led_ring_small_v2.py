"""
MicroPython Tesla Coil Controller (MPTCC)
by Cameron Prince
teslauniverse.com

hardware/rgb_led/rgb_led_ring_small.py
RGB LED Ring Small driver.
"""

import time
import _thread
from RGBLEDRingSmall import RGBLEDRingSmall as LEDRingSmall
from ..rgb_led.rgb_led import RGB, RGBLED
from ...hardware.init import init

class RGBLEDRingSmall(RGBLED):
    """
    A class to control the RGB LED Ring Small device.

    Attributes:
    -----------
    init : object
        The initialization object containing configuration and hardware settings.
    """

    # I2C addresses for the four RGB LED Ring Small devices
    RGB_LED_RING_SMALL_ADDRESSES = [0x68, 0x6C, 0x62, 0x61]

    def __init__(self):
        """
        Constructs all the necessary attributes for the RGBLEDRingSmall object.
        """
        super().__init__()
        self.init = init

        # Add a mutex for I2C communication to the init object.
        if not hasattr(self.init, 'i2cencoder_mutex'):
            self.init.i2cencoder_mutex = _thread.allocate_lock()

        # Initialize the four RGB LED Ring Small devices
        self.init.rgb_led = [
            RGB_RGBLEDRingSmall(self.init.i2c_1, address, self.init.i2cencoder_mutex)
            for address in self.RGB_LED_RING_SMALL_ADDRESSES
        ]

class RGB_RGBLEDRingSmall(RGB):
    """
    A class for handling the RGB LED Ring Small device.
    """
    def __init__(self, i2c, address, mutex):
        super().__init__()
        self.i2c = i2c
        self.address = address
        self.mutex = mutex
        self.num_leds = 24
        self.threshold_brightness = 0x03  # Adjusted to a slightly higher brightness (0x05 out of 0xFF)
        self.full_brightness = 0x20  # Further reduced full brightness to a lower value
        self.vu_colors = self._generate_vu_colors()
        self.led_indexes = self._generate_led_indexes()
        self.led_ring = None
        self._initialize_led_ring()

    def _generate_vu_colors(self):
        """
        Generate the VU meter colors for the LED ring.
        """
        vu_colors = [
            (0, 255, 0),   # Green
            (85, 255, 0),  # Yellow-green
            (170, 255, 0), # Yellow
            (255, 170, 0), # Yellow-orange
            (255, 85, 0),  # Orange
            (255, 0, 0)    # Red
        ]

        # Generate smooth color transitions
        vu_meter_colors = []
        for i in range(len(vu_colors) - 1):
            steps = self.num_leds // (len(vu_colors) - 1)
            gradient = self._get_color_gradient(vu_colors[i], vu_colors[i + 1], steps)
            vu_meter_colors.extend(gradient)

        # Ensure the list has exactly 24 colors
        if len(vu_meter_colors) < self.num_leds:
            vu_meter_colors.extend([vu_colors[-1]] * (self.num_leds - len(vu_meter_colors)))

        # Reverse the order of LEDs to go in the correct direction from green to red
        vu_meter_colors.reverse()

        # Shift starting LED by 180 degrees (13 LEDs) to make L13 the starting green LED
        vu_meter_colors = vu_meter_colors[-13:] + vu_meter_colors[:-13]

        return vu_meter_colors

    def _generate_led_indexes(self):
        """
        Generate the LED indexes to account for 180-degree mounting difference.
        """
        led_indexes = list(range(self.num_leds))
        skewed_indexes = led_indexes[-12:] + led_indexes[:-12]  # Skew by 12
        skewed_indexes.reverse()  # Reverse the order
        skewed_indexes = skewed_indexes[-1:] + skewed_indexes[:-1]  # Back up by one
        return skewed_indexes

    def _get_color_gradient(self, color1, color2, steps):
        """
        Generate a color gradient between two colors.

        Parameters:
        ----------
        color1 : tuple
            The starting color (R, G, B).
        color2 : tuple
            The ending color (R, G, B).
        steps : int
            The number of steps in the gradient.

        Returns:
        -------
        list
            A list of colors representing the gradient.
        """
        gradient = []
        for i in range(steps):
            ratio = i / float(steps)
            red = int(color1[0] * (1 - ratio) + color2[0] * ratio)
            green = int(color1[1] * (1 - ratio) + color2[1] * ratio)
            blue = int(color1[2] * (1 - ratio) + color2[2] * ratio)
            gradient.append((red, green, blue))
        return gradient

    def _initialize_led_ring(self):
        """
        Initialize the LED ring with default settings.
        """
        self.mutex.acquire()
        try:
            # Initialize the LEDRingSmall instance
            self.led_ring = LEDRingSmall(self.i2c, self.address)
            self.led_ring.reset()
            time.sleep(0.02)
            self.led_ring.configuration(0x01)  # Normal operation
            self.led_ring.pwm_frequency_enable(1)
            self.led_ring.spread_spectrum(0b0010110)
            self.led_ring.global_current(0xFF)
            self.led_ring.set_scaling_all(0xFF)
            self.led_ring.pwm_mode()
        finally:
            self.mutex.release()
            # Set all LEDs to the default off state (threshold brightness)
            self._set_all_to_threshold_brightness()

    def _set_rgb(self, led_n, color, brightness):
        """
        Set the color and brightness of a specific LED with mutex.

        Parameters:
        ----------
        led_n : int
            The LED index (0-23).
        color : tuple
            The RGB color (R, G, B).
        brightness : int
            The brightness level (0-255).
        """
        self.mutex.acquire()
        try:
            if led_n < self.num_leds:
                dimmed_color = (
                    color[0] * brightness // 0xFF,
                    color[1] * brightness // 0xFF,
                    color[2] * brightness // 0xFF
                )
                color_code = (dimmed_color[0] << 16) | (dimmed_color[1] << 8) | dimmed_color[2]
                self.led_ring.set_rgb(led_n, color_code)
        finally:
            self.mutex.release()

    def _set_all_to_threshold_brightness(self):
        """
        Set all LEDs to the threshold brightness (default off state) with mutex.
        """
        dark_blue = (0, 0, 139)  # Dark blue color
        for i in self.led_indexes:
            self._set_rgb(i, dark_blue, self.threshold_brightness)

    def status_color(self, value, mode="percent"):
        """
        Set the status color based on a percentage value.

        Parameters:
        ----------
        value : int
            The percentage value (0-100).
        mode : str
            The mode to interpret the value ("percent" or "velocity").
        """
        # Convert velocity to percentage if in velocity mode
        if mode == "velocity":
            value = int(value * 100 / 127)

        # Ensure value is between 0 and 100
        value = max(0, min(100, value))

        # Calculate the number of LEDs to brighten
        num_bright_leds = int(self.num_leds * value / 100)

        # Brighten the first `num_bright_leds` LEDs
        for i in range(num_bright_leds):
            index = self.led_indexes[i]
            self._set_rgb(index, self.vu_colors[index], self.full_brightness)  # Further reduced full brightness
        for i in range(num_bright_leds, self.num_leds):
            index = self.led_indexes[i]
            dark_blue = (0, 0, 139)  # Dark blue color
            self._set_rgb(index, dark_blue, self.threshold_brightness)  # Threshold brightness

    def off(self):
        """
        Set all LEDs to the threshold brightness (default off state).
        """
        dark_blue = (0, 0, 139)  # Dark blue color
        for i in self.led_indexes:
            self._set_rgb(i, dark_blue, self.threshold_brightness)
