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

    def reset(self):
        """
        Reset the device.
        """
        if "ISSI3746_RESET_REG" in self.constants:
            # Reset the RGB LED ring
            self.writeEncoder8(self.constants["ISSI3746_RESET_REG"], 0xAE)
        elif "REG_GCONF" in self.constants:
            # Reset the encoder
            self.writeEncoder8(self.constants["REG_GCONF"], self.constants["RESET"])
        else:
            raise KeyError("No valid reset constant found in CONSTANTS dictionary.")

    def writeInterruptConfig(self, interrupt):
        """
        Write the interrupt configuration.
        """
        self.writeEncoder8(self.constants["REG_INTCONF"], interrupt)

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

    def updateStatus(self):
        """
        Update the status of the encoder.
        """
        self.stat = self.readEncoder8(self.constants["REG_ESTATUS"])
        return self.stat != 0

    def readStatusRaw(self):
        """
        Read the raw status of the encoder.
        """
        return self.stat

    def readCounter32(self):
        """
        Read the 32-bit counter value.
        """
        return self.readEncoder32(self.constants["REG_CVALB4"])

    def readMax(self):
        """
        Read the maximum value.
        """
        return self.readEncoder32(self.constants["REG_CMAXB4"])

    def readMin(self):
        """
        Read the minimum value.
        """
        return self.readEncoder32(self.constants["REG_CMINB4"])

    def readStep(self):
        """
        Read the step value.
        """
        return self.readEncoder32(self.constants["REG_ISTEPB4"])

    def writeDoublePushPeriod(self, value):
        """
        Write the double push period.
        """
        self.writeEncoder8(self.constants["REG_DPPERIOD"], value)

    def writeEncoder8(self, reg, value):
        """
        Write an 8-bit value to the specified register.
        """
        self.i2c.writeto_mem(self.address, reg, bytes([value]))

    def readEncoder8(self, reg):
        """
        Read an 8-bit value from the specified register.
        """
        return self.i2c.readfrom_mem(self.address, reg, 1)[0]

    def writeEncoder32(self, reg, value):
        """
        Write a 32-bit value to the specified register.
        """
        data = struct.pack('>i', value)
        self.i2c.writeto_mem(self.address, reg, data)

    def readEncoder32(self, reg):
        """
        Read a 32-bit value from the specified register.
        """
        data = self.i2c.readfrom_mem(self.address, reg, 4)
        return struct.unpack('>i', data)[0]

    def select_bank(self, bank):
        """
        Select the bank for the ISSI3746 LED controller.
        """
        self.writeEncoder8(self.constants["ISSI3746_COMMANDREGISTER_LOCK"], self.constants["ISSI3746_ULOCK_CODE"])
        self.writeEncoder8(self.constants["ISSI3746_COMMANDREGISTER"], bank)

    def pwm_mode(self):
        """
        Set the ISSI3746 LED controller to PWM mode.
        """
        self.select_bank(self.constants["ISSI3746_PAGE0"])

    def configuration(self, conf):
        """
        Configure the ISSI3746 LED controller.
        """
        self.select_bank(self.constants["ISSI3746_PAGE1"])
        self.writeEncoder8(self.constants["ISSI3746_CONFIGURATION"], conf)

    def set_scaling_all(self, scal):
        """
        Set the scaling for all LEDs.
        """
        self.select_bank(self.constants["ISSI3746_PAGE1"])
        for i in range(1, 73):
            self.writeEncoder8(i, scal)

    def global_current(self, curr):
        """
        Set the global current for the ISSI3746 LED controller.
        """
        self.select_bank(self.constants["ISSI3746_PAGE1"])
        self.writeEncoder8(self.constants["ISSI3746_GLOBALCURRENT"], curr)

    def spread_spectrum(self, spread):
        """
        Set the spread spectrum configuration for the ISSI3746 LED controller.
        """
        self.select_bank(self.constants["ISSI3746_PAGE1"])
        self.writeEncoder8(self.constants["ISSI3746_SPREADSPECTRUM"], spread)

    def pwm_frequency_enable(self, enable):
        """
        Enable or disable PWM frequency for the ISSI3746 LED controller.
        """
        self.select_bank(self.constants["ISSI3746_PAGE1"])
        self.writeEncoder8(self.constants["ISSI3746_PWM_FREQUENCY_ENABLE"], enable)

    def set_rgb(self, led_n, color):
        """
        Set the RGB color for a specific LED.

        Args:
            led_n: The LED index (0-23).
            color: The 24-bit RGB color code.
        """
        if led_n < len(self.constants["ISSI_LED_MAP"][0]):
            self.writeEncoder8(self.constants["ISSI_LED_MAP"][0][led_n], (color >> 16) & 0xFF)
            self.writeEncoder8(self.constants["ISSI_LED_MAP"][1][led_n], (color >> 8) & 0xFF)
            self.writeEncoder8(self.constants["ISSI_LED_MAP"][2][led_n], color & 0xFF)
