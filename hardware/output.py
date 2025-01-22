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
    A class to handle outputs for the MicroPython Tesla Coil Controller (MPTCC).

    Attributes:
    -----------
    init : object
        The initialization object containing configuration and hardware settings.
    output : list
        List of PWM objects for the output channels.
    """

    def __init__(self):
        """
        Constructs all the necessary attributes for the Output object.
        """
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
        Turns off all transmitters and LEDs.
        """
        for output in self.output:
            output.duty_u16(0)
        for led in self.init.rgb_led:
            led.off()

    def set_output(self, output, frequency, on_time, active, max_duty=None):
        """
        Controls the output of a transmitter and updates its corresponding LED.

        Parameters:
        ----------
        output: int
            The output channel to control. A value of 0-3 is expected.
        frequency : int
            The frequency of the signal.
        on_time : int
            The on time of the signal in microseconds.
        active : bool
            If True, the transmitter is active.
        max_duty : float, optional
            The maximum duty cycle as a percentage. If None, the mode is assumed to be "velocity".
        """

        frequency = int(frequency)
        on_time = int(on_time)

        if active:
            self.output[output].freq(frequency)
            duty_cycle = int((on_time / (1000000 / frequency)) * 65535)
            self.output[output].duty_u16(duty_cycle)
            if max_duty is not None:
                percent = utils.calculate_percent(frequency, on_time, max_duty)
                self.init.rgb_led[output].status_color(
                    max(1, min(100, percent)), mode="percentage")
            else:
                velocity = int((on_time / 65535) * 127)
                self.init.rgb_led[output].status_color(
                    velocity, mode="velocity")
        else:
            self.output[output].duty_u16(0)
            self.init.rgb_led[output].off()
