"""
MicroPython Tesla Coil Controller (MPTCC)
by Cameron Prince
teslauniverse.com

hardware/sd_card_reader.py
Class for interacting with the SD card reader.
"""

from .hardware import Hardware
from machine import Pin, SPI
import sdcard
import uos


class SDCardReader(Hardware):
    """
    A class to interact with the SD card reader using the PCA9685 PWM driver.

    Attributes:
    -----------
    init : object
        The initialization object containing configuration and hardware settings.
    """

    def __init__(self, init):
        """
        Constructs all the necessary attributes for the SDCardReader object.
        """
        super().__init__()
        self.init = init

        # Prepare the SPI bus.
        if self.init.SD_CARD_READER_SPI_INSTANCE == 2:
            self.init.init_spi_2()
            self.spi = self.init.spi_2
            self.cs = self.init.PIN_SPI_2_CS
        else:
            self.init.init_spi_1()
            self.spi = self.init.spi_1
            self.cs = self.init.PIN_SPI_1_CS

    def init_sd(self):
        """
        Initializes and mounts the SD card.
        """
        try:
            sd = sdcard.SDCard(self.spi, Pin(self.cs, Pin.OUT))
            # Mount the disk.
            uos.mount(sd, self.init.SD_CARD_READER_MOUNT_POINT)
        except OSError as e:
            pass

    def deinit_sd(self):
        """
        Dismounts the SD card.
        """
        try:
            uos.umount(self.init.SD_MOUNT_POINT)
        except Exception:
            # Ignore any errors that occur.
            pass
