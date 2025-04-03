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

    def __init__(self, pin, length_ms, volume, pwm_freq):
        """
        Constructs all the necessary attributes for the GPIO_Beep object.

        Parameters:
        ----------
        pin : int
            The GPIO pin number connected to the piezo element.
        length_ms : int
            The duration of the beep in milliseconds.
        volume : int
            The volume as a percentage (0-100), mapped to PWM duty cycle or digital out at 100.
        pwm_freq : int
            The PWM operating frequency.
        """
        super().__init__()
        self.pin_number = pin
        self.length_ms = length_ms
        self.volume = volume
        if self.volume == 100:
            self.pin = Pin(self.pin_number, Pin.OUT)
        else:
            self.pin = PWM(Pin(self.pin_number))
            self.pin.freq(pwm_freq)
        init.beep = self

        print(f"Beep tone confirmation enabled (Pin: {pin}, Length: {length_ms}ms, Volume: {volume}, PWM Frequency: {pwm_freq})")

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
