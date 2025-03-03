"""
MicroPython Tesla Coil Controller (MPTCC)
by Cameron Prince
teslauniverse.com

hardware/output/output.py
Parent class for output devices.
"""

from ..hardware import Hardware
from ..init import init

class Output(Hardware):
    def __init__(self):
        super().__init__()
        self.init = init

    def set_all_outputs(self, active=False, freq=None, on_time=None, max_duty=None, max_on_time=None):
        """
        Sets all outputs based on the provided parameters.

        Parameters:
        ----------
        active : bool, optional
            Whether the outputs should be active. Defaults to False.
        freq : int, optional
            The frequency of the output signal in Hz. Required if active is True.
        on_time : int, optional
            The on time of the output signal in microseconds. Required if active is True.
        max_duty : int, optional
            The maximum duty cycle allowed.
        max_on_time : int, optional
            The maximum on time allowed in microseconds.
        """
        for i in range(self.init.NUMBER_OF_COILS):
            self.set_output(i, active, freq, on_time, max_duty, max_on_time)
