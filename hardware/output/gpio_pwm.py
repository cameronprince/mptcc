"""
MicroPython Tesla Coil Controller (MPTCC)
by Cameron Prince
teslauniverse.com

hardware/output/gpio_pwm.py
Class for driving outputs with hardware PWM.
"""

from machine import Pin, PWM
from mptcc.lib.utils import status_color
from ...hardware.init import init
from ..output.output import Output

class GPIO_PWM(Output):
    """
    A class to provide hardware PWM outputs for the MPTCC.

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

    def set_output(self, output, active, frequency=None, on_time=None, max_duty=None, max_on_time=None):
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
            self.init.rgb_led[output].set_status(output, frequency, on_time, max_duty, max_on_time)
        else:
            self.output[output].duty_u16(0)
            self.init.rgb_led[output].off(output)