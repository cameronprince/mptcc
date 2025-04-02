"""
MicroPython Tesla Coil Controller (MPTCC)
by Cameron Prince
teslauniverse.com

hardware/output/gpio_pwm.py
Class for driving outputs with hardware PWM.
"""

from machine import Pin, PWM
from ...hardware.init import init
from ..output.output import Output
from ...lib.utils import calculate_duty_cycle


class Output_GPIO_PWM(Output):
    """
    A class to wrap a single PWM object and provide output control.
    """
    def __init__(self, pin):
        """
        Initialize the Output_GPIO_PWM instance.

        Parameters:
        ----------
        pin : int
            The GPIO pin number for the PWM output.
        """
        self.pin = pin
        self.pwm = PWM(Pin(pin)) if pin is not None else None

    def set_output(self, active=False, freq=None, on_time=None):
        """
        Sets the output based on the provided parameters.

        Parameters:
        ----------
        active : bool, optional
            Whether the output should be active.
        freq : int, optional
            The frequency of the output signal.
        on_time : int, optional
            The on time of the output signal in microseconds.
        """
        if self.pwm is None:
            return  # Skip if the pin is not configured.

        if active:
            freq = int(freq)
            on_time = int(on_time)

            self.pwm.freq(freq)
            duty_cycle = calculate_duty_cycle(on_time, freq)
            self.pwm.duty_u16(duty_cycle)
        else:
            self.pwm.duty_u16(0)


class GPIO_PWM():
    def __init__(self, pins):
        """
        Initialize the GPIO_PWM driver.

        Parameters:
        ----------
        pins : list of int
            A list of GPIO pin numbers for PWM outputs.
        """
        super().__init__()
        self.init = init

        # Initialize Output_GPIO_PWM instances for the provided pins.
        self.instances = [Output_GPIO_PWM(pin) for pin in pins]

        # Assign this instance to the next available key.
        instance_key = len(self.init.output_instances['gpio_pwm'])

        # Print initialization details.
        print(f"GPIO PWM output {instance_key} initialized")
        for i, pin in enumerate(pins):
            if pin is not None:
                print(f"- Output {i}: GPIO {pin}")
