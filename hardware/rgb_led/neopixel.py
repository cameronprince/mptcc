"""
MicroPython Tesla Coil Controller (MPTCC)
by Cameron Prince
teslauniverse.com

hardware/rgb_led/neopixel.py
RGB LED device utilizing the WS2812/NeoPixel.
"""

from machine import Pin
from neopixel import NeoPixel as NeoPixelDriver
from ...lib.utils import status_color, hex_to_rgb
from ..rgb_led.rgb_led import RGBLED, RGB
from ...hardware.init import init


class NeoPixel(RGBLED):
    """
    A class to control RGB LED devices using the WS2812/Neopixel.

    Attributes:
    -----------
    init : object
        The initialization object containing configuration and hardware settings.
    """
    def __init__(self, pin, segments, reverse, default_color, threshold_brightness, full_brightness):
        super().__init__()
        self.init = init
        self.instances = []

        # Validate that the number of segments is sufficient.
        if segments < self.init.NUMBER_OF_COILS:
            raise ValueError(
                f"Number of NeoPixel segments ({segments}) "
                f"is less than the number of coils ({self.init.NUMBER_OF_COILS}). "
                "Increase segments or decrease NUMBER_OF_COILS."
            )

        # Initialize the NeoPixel object.
        self.np = NeoPixelDriver(Pin(pin), segments)

        # Generate a unique key for this instance.
        instance_key = len(self.init.rgb_led_instances["neopixel"])

        for i in range(self.init.NUMBER_OF_COILS):
            led_instance = RGB_NeoPixel(
                driver=self.np,
                led_index=i,
                reverse=reverse,
                num_segments=segments,
                default_color=hex_to_rgb(default_color),
                threshold_brightness=threshold_brightness,
                full_brightness=full_brightness
            )
            self.instances.append(led_instance)

        # Print initialization details.
        print(f"NeoPixel RGB LED driver {instance_key} initialized on GPIO {pin} with {segments} segments")
        print(f"- Reverse mode: {reverse}")
        print(f"- Default color: {default_color}")
        print(f"- Threshold brightness: {threshold_brightness}")
        print(f"- Full brightness: {full_brightness}")
        print(f"- Asyncio polling: {self.init.RGB_LED_ASYNCIO_POLLING}")


class RGB_NeoPixel(RGB):
    """
    A class for handling RGB LEDs with a NeoPixel driver.
    """
    def __init__(self, driver, led_index, reverse, num_segments, default_color, threshold_brightness, full_brightness):
        super().__init__()
        self.driver = driver
        self.led_index = led_index
        self.reverse = reverse
        self.num_segments = num_segments
        self.default_color = default_color
        self.threshold_brightness = threshold_brightness
        self.full_brightness = full_brightness
        self.init = init
        self.off()

    def set_color(self, r, g, b):
        """
        Sets the color of the RGB LED using the NeoPixel driver.

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
        # Check if the color is (0, 0, 0).
        if r == 0 and g == 0 and b == 0:
            # Use the default color and threshold brightness.
            r, g, b = self.default_color
            dimmed_r = r * self.threshold_brightness // 255
            dimmed_g = g * self.threshold_brightness // 255
            dimmed_b = b * self.threshold_brightness // 255
        else:
            # Use the provided color.
            dimmed_r, dimmed_g, dimmed_b = r, g, b

        # Calculate the actual LED index based on reverse mode.
        if self.reverse:
            actual_index = self.num_segments - 1 - self.led_index
        else:
            actual_index = self.led_index

        # Set the color and update the NeoPixel strip.
        self.driver[actual_index] = (dimmed_r, dimmed_g, dimmed_b)
        self.driver.write()
