"""
MicroPython Tesla Coil Controller (MPTCC)
by Cameron Prince
teslauniverse.com

hardware/rgb_led/gpio_rgbled.py
RGB LED device utilizing GPIO pins.
"""

from machine import Pin, PWM
from ...lib.utils import status_color, scale_rgb
from ..rgb_led.rgb_led import RGBLED, RGB
from ...hardware.init import init


class GPIO_RGBLED(RGBLED):
    """
    A class to control common-cathode RGB LED devices using GPIO pins with PWM.
    """
    def __init__(self, config):
        super().__init__()
        self.init = init
        self.pins = config.get("pins", [])

        self.instances = []

        # Generate a unique key for this instance.
        instance_key = len(self.init.rgb_led_instances["gpio"])

        # Initialize the LEDs based on the pins configuration.
        self.instances = []
        for pins in self.pins:
            led = RGB_GPIO_RGBLED(pins)
            self.instances.append(led)

        print(f"GPIO RGB LED driver {instance_key} initialized with {len(self.instances)} instances")
        for i, led in enumerate(self.instances):
            print(f"- LED {i}: Red=GPIO{led.pins[0] if led.pins[0] is not None else 'None'}, "
                  f"Green=GPIO{led.pins[1] if led.pins[1] is not None else 'None'}, "
                  f"Blue=GPIO{led.pins[2] if led.pins[2] is not None else 'None'}")

class RGB_GPIO_RGBLED(RGB):
    """
    A class for handling a single common-cathode RGB LED with GPIO pins and PWM control.
    """
    def __init__(self, pins):
        super().__init__()
        self.init = init
        self.pins = pins

        # Initialize PWM for each pin (if not None).
        self.pwm = []
        for pin in self.pins:
            if pin is not None:
                pwm = PWM(Pin(pin, Pin.OUT))
                pwm.freq(1000)  # 1kHz PWM frequency.
                pwm.duty_u16(0)  # Off state (active-high, common-cathode).
                self.pwm.append(pwm)
            else:
                self.pwm.append(None)

        self.off()

    def set_color(self, r, g, b):
        """
        Sets the color of the common-cathode RGB LED using PWM on GPIO pins.

        Uses raw RGB values (0-255). Skips channels where the pin is None.

        Parameters:
        ----------
        r : int
            Red value (0-255).
        g : int
            Green value (0-255).
        b : int
            Blue value (0-255).
        """
        # Convert 0-255 to 0-65535 for PWM (u16).
        colors = [r, g, b]
        for i, (color, pwm) in enumerate(zip(colors, self.pwm)):
            if pwm is not None:
                # Map 0-255 to 0-65535.
                duty = int((color / 255) * 65535)
                pwm.duty_u16(duty)

    def off(self):
        """
        Turns off the LED by setting all PWM channels to 0 (common-cathode).
        """
        for pwm in self.pwm:
            if pwm is not None:
                pwm.duty_u16(0)
