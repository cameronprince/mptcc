"""
MicroPython Tesla Coil Controller (MPTCC)
by Cameron Prince
teslauniverse.com

hardware/rgb_led/neopixel.py
RGB LED device utilizing the WS2812/NeoPixel.
"""

from machine import Pin
from neopixel import NeoPixel as NeoPixelDriver
from ...lib.utils import status_color, hex_to_rgb, scale_rgb
from ..rgb_led.rgb_led import RGBLED, RGB
from ...hardware.init import init


class GPIO_NeoPixel(RGBLED):
    """
    A class to control RGB LED devices using the WS2812/Neopixel.

    Attributes:
    -----------
    init : object
        The initialization object containing configuration and hardware settings.
    """
    def __init__(self, config):
        super().__init__()

        pin = config.get("pin", None)
        segments = config.get("segments", 0)

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
            led_instance = RGB_NeoPixel(driver=self.np, led_index=i, config=config)
            self.instances.append(led_instance)

        # Print initialization details.
        print(f"NeoPixel RGB LED driver {instance_key} initialized on GPIO {pin} with {segments} segments")
        print(f"- Reverse mode: {config.get('reverse', False)}")
        print(f"- Default color: {config.get('default_color', '#000000')}")
        print(f"- Threshold brightness: {config.get('threshold_brightness', 0)}")
        print(f"- Full brightness: {config.get('full_brightness', 0)}")


class RGB_NeoPixel(RGB):
    """
    A class for handling RGB LEDs with a NeoPixel driver.
    """
    def __init__(self, driver, led_index, config):
        super().__init__()
        self.driver = driver
        self.led_index = led_index

        self.reverse = config.get("reverse", False)
        self.segments = config.get("segments", 0)
        self.default_color = hex_to_rgb(config.get("default_color", "#000000"))
        self.threshold_brightness = config.get("threshold_brightness", 0)
        self.full_brightness = config.get("full_brightness", 0)

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
            r, g, b = scale_rgb(*self.default_color, self.threshold_brightness)

        # Calculate the actual LED index based on reverse mode.
        if self.reverse:
            actual_index = self.segments - 1 - self.led_index
        else:
            actual_index = self.led_index

        # Set the color and update the NeoPixel strip.
        self.driver[actual_index] = (r, g, b)
        self.driver.write()
