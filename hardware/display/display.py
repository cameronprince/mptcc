"""
MicroPython Tesla Coil Controller (MPTCC)
by Cameron Prince
teslauniverse.com

hardware/display/display.py
Parent class for displays.
"""

from ..hardware import Hardware

class Display(Hardware):
    def __init__(self):
        super().__init__()
