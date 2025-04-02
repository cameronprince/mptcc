"""
MicroPython Tesla Coil Controller (MPTCC)
by Cameron Prince
teslauniverse.com

hardware/other/sd_card_reader.py
Class for interacting with the SD card reader.
"""

from machine import Pin, SPI
import sdcard
import uos
from ..init import init
from ..hardware import Hardware


class SDCardReader(Hardware):
    """
    A class to interact with the SD card reader using the PCA9685 PWM driver.
    """

    def __init__(self, spi_instance, mount_point):
        """
        Constructs all the necessary attributes for the SDCardReader object.
        """
        super().__init__()
        self.mount_point = mount_point
        self.init = init

        # Prepare the SPI bus.
        if spi_instance == 2:
            self.init.init_spi_2()
            self.spi = self.init.spi_2
            self.cs = self.init.PIN_SPI_2_CS
        else:
            self.init.init_spi_1()
            self.spi = self.init.spi_1
            self.cs = self.init.PIN_SPI_1_CS

        self.init.sd_card_reader = self

        print(f"SD card reader driver loaded on SPI{spi_instance}")

    def init_sd(self):
        """
        Initializes and mounts the SD card.
        """
        try:
            sd = sdcard.SDCard(self.spi, Pin(self.cs, Pin.OUT))
            # Mount the disk.
            uos.mount(sd, self.mount_point)
        except OSError as e:
            pass

    def deinit_sd(self):
        """
        Dismounts the SD card.
        """
        try:
            uos.umount(self.mount_point)
        except Exception:
            # Ignore any errors that occur.
            pass
