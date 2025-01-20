from .hardware import Hardware
from ..lib import utils
from machine import Pin, PWM
from .. import init

class Outputs(Hardware):
    def __init__(self):
        super().__init__()

        print(dir(init))

        self.outputs = [
            PWM(Pin(init.init.PIN_OUTPUT_1)),
            PWM(Pin(init.init.PIN_OUTPUT_2)),
            PWM(Pin(init.init.PIN_OUTPUT_3)),
            PWM(Pin(init.init.PIN_OUTPUT_4))
        ]

    def disable_outputs(self):
        """
        Turns off all transmitters and LEDs.
        """
        for output in self.outputs:
            output.duty_u16(0)
        for led in init.leds:
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
            self.outputs[output].freq(frequency)
            duty_cycle = int((on_time / (1000000 / frequency)) * 65535)
            self.outputs[output].duty_u16(duty_cycle)
            if max_duty is not None:
                percent = calculate_percent(frequency, on_time, max_duty)
                init.leds[output].status_color(max(1, min(100, percent)), mode="percentage")
            else:
                velocity = int((on_time / 65535) * 127)
                init.leds[output].status_color(velocity, mode="velocity")
        else:
            init.outputs[output].duty_u16(0)
            init.leds[output].off()

