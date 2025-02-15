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
        Disables all outputs by setting their duty cycle to 0 and turning off the associated LEDs.
        """
        for i in range(4):
            self.set_output(i, active, freq, on_time, max_duty, max_on_time)
