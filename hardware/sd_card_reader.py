"""
MicroPython Tesla Coil Controller (MPTCC)
by Cameron Prince
teslauniverse.com

hardware/sd_card_reader.py
Class for interacting with the SD card reader.
"""

from ..hardware.init import init
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

    def __init__(self):
        """
        Constructs all the necessary attributes for the SDCardReader object.
        """
        super().__init__()
        self.init = init

        # Prepare the SPI bus.
        self.init.init_spi_1()

    def init_sd(self):
        """
        Initializes and mounts the SD card.
        """
        try:
            sd = sdcard.SDCard(self.init.spi_1, Pin(self.init.PIN_SPI_1_CS, Pin.OUT))
            # Mount the disk.
            uos.mount(sd, self.init.SD_MOUNT_POINT)
        except OSError as e:
            print(f"Error initializing SD card: {e}")

    def deinit_sd(self):
        """
        Dismounts the SD card.
        """
        try:
            uos.umount(self.init.SD_MOUNT_POINT)
        except Exception:
            # Ignore any errors that occur
            pass
