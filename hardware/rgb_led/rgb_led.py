"""
MicroPython Tesla Coil Controller (MPTCC)
by Cameron Prince
teslauniverse.com

hardware/rgb_led/rgb_led.py
Parent class for RGB LEDs.
"""
from ..hardware import Hardware

class RGBLED(Hardware):
    def __init__(self):
        super().__init__()
