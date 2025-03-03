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
from ...lib.utils import calculate_percent, status_color
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

    def __init__(self):
        """
        Constructs all the necessary attributes for the RGBLEDRingSmall object.
        """
        super().__init__()
        self.init = init

        # Validate that the number of RGB LED Ring Small addresses matches NUMBER_OF_COILS
        if len(self.init.RGB_LED_RING_SMALL_ADDRESSES) != self.init.NUMBER_OF_COILS:
            raise ValueError(
                f"The number of RGB LED Ring Small addresses ({len(self.init.RGB_LED_RING_SMALL_ADDRESSES)}) "
                f"must match NUMBER_OF_COILS ({self.init.NUMBER_OF_COILS}). The program will now exit."
            )

        # Prepare the I2C bus.
        if self.init.RGB_LED_RING_SMALL_I2C_INSTANCE == 2:
            self.init.init_i2c_2()
            self.i2c = self.init.i2c_2
            self.mutex = self.init.i2c_2_mutex
        else:
            self.init.init_i2c_1()
            self.i2c = self.init.i2c_1
            self.mutex = self.init.i2c_1_mutex

        # Dynamically initialize RGB LED Ring Small devices based on NUMBER_OF_COILS
        self.init.rgb_led = [
            RGB_RGBLEDRingSmall(self.i2c, address, self.mutex)
            for address in self.init.RGB_LED_RING_SMALL_ADDRESSES
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
        self.init = init
        self.num_leds = 24
        self.threshold_brightness = self.init.RGB_LED_RING_SMALL_THRESHOLD_BRIGHTNESS
        self.full_brightness = self.init.RGB_LED_RING_SMALL_FULL_BRIGHTNESS
        self.default_color = self._get_default_color()
        self.step_delay = self.init.RGB_LED_RING_SMALL_DELAY_BETWEEN_STEPS
        self.vu_colors = self._generate_vu_colors()
        self.led_indexes = self._generate_led_indexes()
        self.led_ring = None
        self._initialize_led_ring()

    def _get_default_color(self):
        """
        Get the default color or handle the "vu_meter" case.

        Returns:
        -------
        tuple
            The default color as an RGB tuple or None if "vu_meter" is set.
        """
        if self.init.RGB_LED_RING_SMALL_DEFAULT_COLOR == "vu_meter":
            return None
        else:
            return self._hex_to_rgb(self.init.RGB_LED_RING_SMALL_DEFAULT_COLOR)

    def _hex_to_rgb(self, hex_color):
        """
        Convert a hex color code to an RGB tuple.

        Parameters:
        ----------
        hex_color : str
            The hex color code (e.g., "#326400").

        Returns:
        -------
        tuple
            The RGB color as a tuple (R, G, B).
        """
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

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

        # Generate smooth color transitions.
        vu_meter_colors = []
        for i in range(len(vu_colors) - 1):
            steps = self.num_leds // (len(vu_colors) - 1)
            gradient = self._get_color_gradient(vu_colors[i], vu_colors[i + 1], steps)
            vu_meter_colors.extend(gradient)

        # Ensure the list has exactly 24 colors.
        if len(vu_meter_colors) < self.num_leds:
            vu_meter_colors.extend([vu_colors[-1]] * (self.num_leds - len(vu_meter_colors)))

        # Reverse the order of LEDs to go in the correct direction from green to red.
        vu_meter_colors.reverse()

        # Shift starting LED by the configured rotation.
        rotation_leds = int((self.init.RGB_LED_RING_SMALL_ROTATION / 360) * self.num_leds)
        vu_meter_colors = vu_meter_colors[-rotation_leds:] + vu_meter_colors[:-rotation_leds]

        # Apply the additional shift by one position.
        vu_meter_colors = vu_meter_colors[-1:] + vu_meter_colors[:-1]

        return vu_meter_colors

    def _generate_led_indexes(self):
        """
        Generate the LED indexes to account for the configured rotation.
        """
        led_indexes = list(range(self.num_leds))
        rotation_leds = int((self.init.RGB_LED_RING_SMALL_ROTATION / 360) * self.num_leds)
        skewed_indexes = led_indexes[-rotation_leds:] + led_indexes[:-rotation_leds]
        skewed_indexes.reverse()
        skewed_indexes = skewed_indexes[-1:] + skewed_indexes[:-1]
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
        self.init.mutex_acquire(self.mutex, "rgb_led_ring_small:_initialize_led_ring")
        try:
            self.led_ring = LEDRingSmall(self.i2c, self.address)
            self.led_ring.reset()
            time.sleep(0.01)
            self.led_ring.configuration(0x01)  # Normal operation
            self.led_ring.pwm_frequency_enable(1)
            self.led_ring.spread_spectrum(0b0010110)
            self.led_ring.global_current(0xFF)
            self.led_ring.set_scaling_all(0xFF)
            self.led_ring.pwm_mode()
        finally:
            self.init.mutex_release(self.mutex, "rgb_led_ring_small:_initialize_led_ring")
            self.off()

    def _set_rgb(self, led_n, color, brightness, no_delay=False):
        """
        Set the color and brightness of a specific LED with mutex and a small delay.

        Parameters:
        ----------
        led_n : int
            The LED index (0-23).
        color : tuple
            The RGB color (R, G, B).
        brightness : int
            The brightness level (0-255).
        """
        self.init.mutex_acquire(self.mutex, "rgb_led_ring_small:_set_rgb")
        try:
            if led_n < self.num_leds:
                dimmed_color = (
                    color[0] * brightness // 0xFF,
                    color[1] * brightness // 0xFF,
                    color[2] * brightness // 0xFF
                )
                color_code = (dimmed_color[0] << 16) | (dimmed_color[1] << 8) | dimmed_color[2]
                self.led_ring.set_rgb(led_n, color_code)
                if not no_delay and self.step_delay > 0:
                    time.sleep(self.step_delay)
        finally:
            self.init.mutex_release(self.mutex, "rgb_led_ring_small:_set_rgb")

    def off(self, output=None):
        """
        Set all LEDs to the threshold brightness (default off state).
        """
        for i in self.led_indexes:
            if self.default_color is None:
                color = self.vu_colors[i]
            else:
                color = self.default_color
            self._set_rgb(i, color, self.threshold_brightness, no_delay=True)

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
        if self.init.RGB_LED_RING_SMALL_MODE == "status":
            color = status_color(frequency, on_time, max_duty, max_on_time)
            self._set_all_leds(color, self.full_brightness)
        else:
            # Use the updated calculate_percent function to handle both cases.
            value = calculate_percent(frequency, on_time, max_duty, max_on_time)

            # Calculate the number of LEDs to brighten.
            num_bright_leds = int(self.num_leds * value / 100)

            # Brighten the first `num_bright_leds` LEDs.
            for i in range(num_bright_leds):
                index = self.led_indexes[i]
                self._set_rgb(index, self.vu_colors[index], self.full_brightness)
            for i in range(num_bright_leds, self.num_leds):
                index = self.led_indexes[i]
                if self.default_color is None:
                    self._set_rgb(index, self.vu_colors[index], self.threshold_brightness)
                else:
                    self._set_rgb(index, self.default_color, self.threshold_brightness)

    def _set_all_leds(self, color, brightness):
        """
        Set all LEDs to the same color and brightness.

        Parameters:
        ----------
        color : tuple
            The RGB color (R, G, B).
        brightness : int
            The brightness level (0-255).
        """
        for i in self.led_indexes:
            self._set_rgb(i, color, brightness, no_delay=True)
