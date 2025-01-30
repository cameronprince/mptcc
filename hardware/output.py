"""
MicroPython Tesla Coil Controller (MPTCC)
by Cameron Prince
teslauniverse.com

hardware/output.py
Class for handling outputs.
"""

from machine import Pin, PWM
from .hardware import Hardware
from ..lib import utils
from ..hardware.init import init

class Output(Hardware):
    """
    A class to handle the outputs for the MPTCC.

    Attributes:
    -----------
    init : object
        The initialization object containing configuration and hardware settings.
    output : list
        A list of PWM objects for each output.
    """
    def __init__(self):
        super().__init__()
        self.init = init

        self.output = [
            PWM(Pin(self.init.PIN_OUTPUT_1)),
            PWM(Pin(self.init.PIN_OUTPUT_2)),
            PWM(Pin(self.init.PIN_OUTPUT_3)),
            PWM(Pin(self.init.PIN_OUTPUT_4))
        ]

    def disable_outputs(self):
        """
        Disables all outputs by setting their duty cycle to 0 and turning off the associated LEDs.
        """
        for output in self.output:
            output.duty_u16(0)
        for led in self.init.rgb_led:
            led.off()

    def set_output(self, output, active, frequency=None, on_time=None, triggering_class=None):
        """
        Sets the output based on the provided parameters.

        Parameters:
        ----------
        output : int
            The index of the output to be set.
        active : bool
            Whether the output should be active.
        frequency : int, optional
            The frequency of the output signal.
        on_time : int, optional
            The on time of the output signal in microseconds.
        triggering_class : object, optional
            The class instance containing max_duty, min_on_time, and max_on_time attributes.

        Raises:
        -------
        ValueError
            If frequency or on_time is not provided when activating the output.
        """
        if active:
            if frequency is None or on_time is None:
                raise ValueError("Frequency and on_time must be provided when activating the output.")
            
            frequency = int(frequency)
            on_time = int(on_time)

            self.output[output].freq(frequency)
            duty_cycle = int((on_time / (1000000 / frequency)) * 65535)
            self.output[output].duty_u16(duty_cycle)

            if triggering_class:
                percent = utils.calculate_percent(frequency, on_time, triggering_class)
                self.init.rgb_led[output].status_color(percent)
            else:
                velocity = int((on_time / 65535) * 127)
                self.init.rgb_led[output].status_color(velocity, mode="velocity")
        else:
            self.output[output].duty_u16(0)
            self.init.rgb_led[output].off()
