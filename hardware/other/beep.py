"""
MicroPython Tesla Coil Controller (MPTCC)
by Cameron Prince
teslauniverse.com

hardware/other/beep.py
Provides beep tone confirmation for inputs.
"""

import time
from machine import Pin, PWM
from ..init import init


class GPIO_Beep():
    """
    A class to interact with a piezo element connected to a GPIO pin.
    """

    def __init__(self, config):
        """
        Constructs all the necessary attributes for the GPIO_Beep object.
        """
        super().__init__()

        self.pin_number = config.get("pin", None)
        self.length_ms = config.get("length_ms", 0)
        self.volume = config.get("volume", 0)
        self.pwm_freq = config.get("pwm_freq", 0)

        if self.volume == 100:
            self.pin = Pin(self.pin_number, Pin.OUT)
        else:
            self.pin = PWM(Pin(self.pin_number))
            self.pin.freq(self.pwm_freq)
        init.beep = self

        print(f"Beep tone confirmation enabled (Pin: {self.pin_number}, Length: {self.length_ms}ms, Volume: {self.volume}, PWM Frequency: {self.pwm_freq})")

    def on(self):
        """
        Trigger a blocking beep for the specified duration.
        Uses digital output if volume = 100, PWM otherwise.
        """
        if self.volume == 100:
            # Use digital output.
            self.pin.on()
            time.sleep_ms(self.length_ms)
            self.pin.off()
        else:
            # Use PWM output.
            duty = int((self.volume / 100) * 65535)
            self.pin.duty_u16(duty)
            time.sleep_ms(self.length_ms)
            self.pin.duty_u16(0)
