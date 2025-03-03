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

        # Initialize outputs dynamically
        self.output = []

        for i in range(1, self.init.NUMBER_OF_COILS + 1):
            # Dynamically get the output pin for the current coil
            pin_attr = f"PIN_OUTPUT_{i}"
            if not hasattr(self.init, pin_attr):
                raise ValueError(
                    f"Output pin configuration for coil {i} is missing. "
                    f"Please ensure {pin_attr} is defined in the init module."
                )
            pin = getattr(self.init, pin_attr)

            # Initialize the PWM object for the current output pin
            self.output.append(PWM(Pin(pin)))

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
