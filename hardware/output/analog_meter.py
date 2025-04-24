"""
MicroPython Tesla Coil Controller (MPTCC)
by Cameron Prince
teslauniverse.com

hardware/output/analog_meter.py
Class for driving analog meters for output level monitoring.
"""

from machine import Pin, PWM
from ...hardware.init import init
from ..output.output import Output
from ...lib.utils import calculate_percent


class Analog_Meter():
    def __init__(self, config):
        """Initialize the Analog_Meter driver."""
        super().__init__()
        self.init = init
        self.pins = config.get("pins", [])

        # Initialize Output_GPIO_PWM instances for the provided pins.
        self.instances = [Analog_Meter_PWM(pin, config) for pin in self.pins]

        # Assign this instance to the next available key.
        instance_key = len(self.init.output_instances['analog_meter'])

        # Print initialization details.
        print(f"Analog meter {instance_key} initialized")
        for i, pin in enumerate(self.pins):
            if pin is not None:
                print(f"- {i}: GPIO {pin}")


class Analog_Meter_PWM(Output):
    """
    A class to wrap a single PWM object and provide analog meter control.
    """
    def __init__(self, pin, config):
        self.pin = pin
        self.pwm = PWM(Pin(pin)) if pin is not None else None
        if self.pwm:
            self.pwm.freq(config.get("pwm_freq", 1000))
        self.sensitivity = config.get("sensitivity", 1)

    def set_output(self, active=False, freq=None, on_time=None, max_duty=None, max_on_time=None):
        if not self.pwm:
            return
        if active:
            # Use calculate_percent() to get the percentage
            percent = calculate_percent(freq, on_time, max_duty, max_on_time)
            # Apply sensitivity and clamp to 0-100%
            effective_percent = min(percent * self.sensitivity, 100)
            # Convert to PWM duty cycle (0-65535)
            duty_cycle = int((effective_percent / 100) * 65535)
            self.pwm.duty_u16(duty_cycle)
        else:
            self.pwm.duty_u16(0)  # Turn off if not active
