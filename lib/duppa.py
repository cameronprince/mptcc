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
        Reset the device, supporting ISSI3746, IS31FL3745, and encoders.
        """
        if "ISSI3746_RESET_REG" in self.constants:
            self.writeEncoder8(self.constants["ISSI3746_RESET_REG"], 0xAE)  # ISSI3746 reset
        elif "IS31FL3745_RESET_REG" in self.constants:
            self.select_page(self.constants["IS31FL3745_PAGE2"])
            self.writeEncoder8(self.constants["IS31FL3745_RESET_REG"], 0x00)  # IS31FL3745 reset
        elif "REG_GCONF" in self.constants:
            self.writeEncoder8(self.constants["REG_GCONF"], self.constants["RESET"])  # Encoder reset
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
        red = (rgb >> 16) & 0xFF
        green = (rgb >> 8) & 0xFF
        blue = rgb & 0xFF
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

    def writeEncoder16(self, reg, value):
        """
        Write a 16-bit value to the specified register.
        """
        data = struct.pack('<H', value)  # Little-endian, 16-bit unsigned int
        self.i2c.writeto_mem(self.address, reg, data)

    def readEncoder16(self, reg):
        """
        Read a 16-bit value from the specified register.
        """
        data = self.i2c.readfrom_mem(self.address, reg, 2)
        return int.from_bytes(data, 'little')

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
        Set the scaling for all LEDs (ISSI3746-specific, 72 channels).
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

    def set_rgb_batch(self, buffer):
        """
        Set the RGB color for all LEDs in a batch update (ISSI3746-specific).
        """
        self.select_bank(self.constants["ISSI3746_PAGE0"])
        self.i2c.writeto_mem(self.address, 0x01, buffer)

    # New methods for IS31FL3745 support (RGBLEDRing)
    def select_page(self, page):
        """
        Select the active page for IS31FL3745 LED controller.
        """
        self.writeEncoder8(self.constants["IS31FL3745_UNLOCK_REGISTER"], self.constants["IS31FL3745_UNLOCK_CODE"])
        self.writeEncoder8(self.constants["IS31FL3745_PAGE_REGISTER"], page)

    def set_scaling_all_is31fl3745(self, scal, num_channels):
        """
        Set scaling for all LEDs on IS31FL3745 (variable channel count).
        """
        self.select_page(self.constants["IS31FL3745_PAGE1"])
        for i in range(num_channels):
            self.writeEncoder8(i, scal)

    def set_rgb_batch_is31fl3745(self, buffer):
        """
        Set the RGB color for all LEDs in a batch update on IS31FL3745.
        """
        self.select_page(self.constants["IS31FL3745_PAGE0"])
        self.i2c.writeto_mem(self.address, 0x00, buffer)

    def configuration_is31fl3745(self, conf):
        """
        Configure the IS31FL3745 LED controller.
        """
        self.select_page(self.constants["IS31FL3745_PAGE2"])
        self.writeEncoder8(self.constants["IS31FL3745_CONFIG_REG"], conf)

    def global_current_is31fl3745(self, curr):
        """
        Set the global current for the IS31FL3745 LED controller.
        """
        self.select_page(self.constants["IS31FL3745_PAGE2"])
        self.writeEncoder8(self.constants["IS31FL3745_GLOBAL_CURRENT"], curr)
    