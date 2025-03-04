"""
MicroPython Tesla Coil Controller (MPTCC)
by Cameron Prince
teslauniverse.com

lib/duppa.py
Utility library for interfacing with hardware from DuPPa.net.
"""

import struct

class DuPPa:
    def __init__(self, i2c, address, constants):
        """
        Initialize the DuPPa hardware.

        Args:
            i2c: I2C bus object.
            address: I2C address of the device.
            constants: Dictionary of constants and register definitions.
        """
        self.i2c = i2c
        self.address = address
        self.constants = constants

    def begin(self, config):
        """
        Initialize the encoder with the given configuration.
        """
        self.writeEncoder8(self.constants["REG_GCONF"], config & 0xFF)
        self.writeEncoder8(self.constants["REG_GCONF2"], (config >> 8) & 0xFF)

    def reset(self):
        """
        Reset the encoder.
        """
        self.writeEncoder8(self.constants["REG_GCONF"], 0x80)

    def writeEncoder8(self, reg, value):
        """
        Write an 8-bit value to the specified register.
        """
        self.i2c.writeto_mem(self.address, reg, bytes([value]))

    def readEncoder8(self, reg):
        """
        Read an 8-bit value from the specified register.
        """
        data = self.i2c.readfrom_mem(self.address, reg, 1)
        return struct.unpack(">B", data)[0]

    def writeEncoder32(self, reg, value):
        """
        Write a 32-bit value to the specified register.
        """
        data = struct.pack('>I', value)
        self.i2c.writeto_mem(self.address, reg, data)

    def readEncoder32(self, reg):
        """
        Read a 32-bit value from the specified register.
        """
        data = self.i2c.readfrom_mem(self.address, reg, 4)
        return struct.unpack(">I", data)[0]

    def writeCounter(self, value):
        """
        Write the counter value.
        """
        self.writeEncoder32(self.constants["REG_CVALB4"], value)

    def writeMax(self, value):
        """
        Write the maximum value.
        """
        self.writeEncoder32(self.constants["REG_CMAXB4"], value)

    def writeMin(self, value):
        """
        Write the minimum value.
        """
        self.writeEncoder32(self.constants["REG_CMINB4"], value)

    def writeStep(self, value):
        """
        Write the step value.
        """
        self.writeEncoder32(self.constants["REG_ISTEPB4"], value)

    def writeAntibouncingPeriod(self, value):
        """
        Write the antibouncing period.
        """
        self.writeEncoder8(self.constants["REG_ANTBOUNC"], value)

    def writeGammaRLED(self, value):
        """
        Write the gamma value for the red LED.
        """
        self.writeEncoder8(self.constants["REG_GAMRLED"], value)

    def writeGammaGLED(self, value):
        """
        Write the gamma value for the green LED.
        """
        self.writeEncoder8(self.constants["REG_GAMGLED"], value)

    def writeGammaBLED(self, value):
        """
        Write the gamma value for the blue LED.
        """
        self.writeEncoder8(self.constants["REG_GAMBLED"], value)

    def writeRGBCode(self, rgb):
        """
        Write a 24-bit RGB color code to the encoder's RGB LED registers.
        """
        # Extract the red, green, and blue components from the 24-bit RGB value
        red = (rgb >> 16) & 0xFF
        green = (rgb >> 8) & 0xFF
        blue = rgb & 0xFF

        # Write the RGB values to their respective registers
        self.writeEncoder8(self.constants["REG_RLED"], red)
        self.writeEncoder8(self.constants["REG_GLED"], green)
        self.writeEncoder8(self.constants["REG_BLED"], blue)

    def readStatus(self):
        """
        Read the status register.
        """
        return self.readEncoder8(self.constants["REG_ESTATUS"])
