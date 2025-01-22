"""
MicroPython Tesla Coil Controller (MPTCC)
by Cameron Prince
teslauniverse.com

hardware/input/input.py
Parent class for input devices.
"""
from ..hardware import Hardware

class Input(Hardware):
    def __init__(self):
        super().__init__()
