"""
MicroPython Tesla Coil Controller (MPTCC)
by Cameron Prince
teslauniverse.com

hardware/output/gpio_pwm.py
Class for driving outputs with hardware PWM.
"""

from machine import Pin, PWM
from ...lib import utils
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

            # The triggering class is passed for any screen which allows
            # variable signal constraints. The constraints are then used to
            # determine the output percentage level of the current signal.
            if max_duty and max_on_time:
                percent = utils.calculate_percent(frequency, on_time, max_duty, max_on_time)
                self.init.rgb_led[output].status_color(percent)
            else:
                # MIDI signal constraints are fixed at 0-127 by the standard.
                percent = utils.calculate_midi_percent(frequency, on_time)
                # print('CH: ', output, ' %:', percent)
                self.init.rgb_led[output].status_color(percent)
        else:
            self.output[output].duty_u16(0)
            self.init.rgb_led[output].off()