"""
MicroPython Tesla Coil Controller (MPTCC)
by Cameron Prince
teslauniverse.com

hardware/rgb_led/gpio.py
RGB LED device utilizing standard GPIO pins.
"""

from machine import Pin, PWM
from ...lib.utils import hex_to_rgb
from ..rgb_led.rgb_led import RGBLED, RGB
from ...hardware.init import init


class GPIO_RGBLED(RGBLED):
    """
    A class to control RGB LED devices using standard GPIO pins.

    Attributes:
    -----------
    init : object
        The initialization object containing configuration and hardware settings.
    """
    def __init__(self, pins):
        super().__init__()
        self.init = init
        self.instances = []

        # Validate that the number of pin sets is sufficient.
        if len(pins) < self.init.NUMBER_OF_COILS:
            raise ValueError(
                f"Number of GPIO pin sets ({len(pins)}) "
                f"is less than the number of coils ({self.init.NUMBER_OF_COILS}). "
                "Increase pin sets or decrease NUMBER_OF_COILS."
            )

        # Generate a unique key for this instance.
        instance_key = len(self.init.rgb_led_instances["gpio"])

        for i in range(self.init.NUMBER_OF_COILS):
            led_instance = RGB_GPIO_RGBLED(pins=pins[i])
            self.instances.append(led_instance)

        # Print initialization details.
        print(f"GPIO RGB LED driver {instance_key} initialized with {len(pins)} pin sets")


class RGB_GPIO_RGBLED(RGB):
    """
    A class for handling RGB LEDs with a GPIO driver.
    """
    def __init__(self, pins):
        super().__init__()
        self.init = init

        # Initialize GPIO pins for R, G, B
        self.pin_r = PWM(Pin(pins[0])) if pins[0] is not None else None
        self.pin_g = PWM(Pin(pins[1])) if pins[1] is not None else None
        self.pin_b = PWM(Pin(pins[2])) if pins[2] is not None else None

        # Initialize PWM frequency (e.g., 1000 Hz)
        self._pwm_freq = 1000
        if self.pin_r:
            self.pin_r.freq(self._pwm_freq)
        if self.pin_g:
            self.pin_g.freq(self._pwm_freq)
        if self.pin_b:
            self.pin_b.freq(self._pwm_freq)

        # Turn off the LED initially
        self.off()

    def set_color(self, r, g, b):
        """
        Sets the color of the RGB LED using the GPIO pins.

        Parameters:
        ----------
        r : int
            Red value (0-255).
        g : int
            Green value (0-255).
        b : int
            Blue value (0-255).
        """
        # Set the color using PWM on the GPIO pins.
        self._set_pin_value(self.pin_r, r)
        self._set_pin_value(self.pin_g, g)
        self._set_pin_value(self.pin_b, b)

    def _set_pin_value(self, pin, value):
        """
        Sets the value of a GPIO pin using PWM.

        Parameters:
        ----------
        pin : machine.PWM
            The PWM object for the GPIO pin.
        value : int
            The value to set (0-255).
        """
        if pin is not None:
            # Scale the value to 0-65535 (PWM duty cycle range)
            pin.duty_u16(int(value * 257))  # 257 = 65535 / 255
