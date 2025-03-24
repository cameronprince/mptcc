"""
MicroPython Tesla Coil Controller (MPTCC)
by Cameron Prince
teslauniverse.com

hardware/output/output.py
Parent class for output devices.
"""

from ..hardware import Hardware


class Output(Hardware):
    def __init__(self):
        super().__init__()
