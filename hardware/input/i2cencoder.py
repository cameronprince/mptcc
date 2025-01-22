"""
MicroPython Tesla Coil Controller (MPTCC)
by Cameron Prince
teslauniverse.com

hardware/input/i2cencoder.py
Input module for I2CEncoder V2.1.
"""

from ..input.input import Input
from ... import init

class I2CEncoder(Input):
    def __init__(self):
        super().__init__()

