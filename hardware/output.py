from .hardware import Hardware
from ..lib import utils
from machine import Pin, PWM
from .. import init

class Output(Hardware):
    def __init__(self):
        super().__init__()
        self.init = init.init

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

    def enable_output(self, output, frequency, on_time, active, max_duty=None):
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
            percent = utils.calculate_percent(frequency, on_time, max_duty)
            percent = max(1, min(100, percent))
            self.init.rgb_led[output].status_color(percent, mode="percentage")
        else:
            self.output[output].duty_u16(0)
            self.init.rgb_led[output].off()

