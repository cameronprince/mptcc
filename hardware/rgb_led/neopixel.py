"""
MicroPython Tesla Coil Controller (MPTCC)
by Cameron Prince
teslauniverse.com

hardware/rgb_led/neopixel.py
RGB LED device utilizing the WS2812/NeoPixel.
"""

from machine import Pin
from neopixel import NeoPixel as NeoPixelDriver
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
    def __init__(self):
        super().__init__()
        self.init = init

        # Validate that the number of segments is sufficient.
        if self.init.RGB_NEOPIXEL_SEGMENTS < self.init.NUMBER_OF_COILS:
            raise ValueError(
                f"Number of NeoPixel segments ({self.init.RGB_NEOPIXEL_SEGMENTS}) "
                f"is less than the number of coils ({self.init.NUMBER_OF_COILS}). "
                "Increase RGB_NEOPIXEL_SEGMENTS or decrease NUMBER_OF_COILS."
            )

        # Initialize the NeoPixel object.
        self.np = NeoPixelDriver(Pin(self.init.RGB_NEOPIXEL_PIN), self.init.RGB_NEOPIXEL_SEGMENTS)

        # Print initialization details.
        print(f"NeoPixel RGB LED driver initialized on GPIO {self.init.RGB_NEOPIXEL_PIN} with {self.init.RGB_NEOPIXEL_SEGMENTS} segments")
        print(f"- Asyncio polling: {self.init.RGB_LED_ASYNCIO_POLLING}")
        print(f"- Reverse mode: {self.init.RGB_NEOPIXEL_REVERSE}")

        # Dynamically initialize RGB LEDs based on NUMBER_OF_COILS.
        self.init.rgb_led = [
            RGB_NeoPixel(
                driver=self.np,
                led_index=i,
                reverse=self.init.RGB_NEOPIXEL_REVERSE,
                num_segments=self.init.RGB_NEOPIXEL_SEGMENTS,
            )
            for i in range(self.init.NUMBER_OF_COILS)
        ]


class RGB_NeoPixel(RGB):
    """
    A class for handling RGB LEDs with a NeoPixel driver.
    """
    def __init__(self, driver, led_index, reverse, num_segments):
        super().__init__()
        self.driver = driver
        self.led_index = led_index
        self.reverse = reverse
        self.num_segments = num_segments
        self.init = init
        self.setColor(0, 0, 0)  # Initialize LED to off

    def setColor(self, r, g, b):
        """
        Sets the color of the RGB LED using the NeoPixel driver.
        If reverse mode is enabled, the LED index is reversed.
        """
        # Calculate the actual LED index based on reverse mode
        if self.reverse:
            actual_index = self.num_segments - 1 - self.led_index
        else:
            actual_index = self.led_index

        # Set the color and update the NeoPixel strip
        self.driver[actual_index] = (r, g, b)
        self.driver.write()
