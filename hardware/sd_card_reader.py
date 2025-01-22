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

    def __init__(self):
        super().__init__()
        self.init = init

        # Prepare the SPI bus.
        self.init.init_spi_1()

    def init_sd(self):
        try:
            sd = sdcard.SDCard(self.init.spi_1, Pin(self.init.PIN_SPI_1_CS, Pin.OUT))
            # Mount the disk.
            uos.mount(sd, self.init.SD_MOUNT_POINT)
        except OSError as e:
            print(f"Error initializing SD card: {e}")

    def deinit_sd(self):
        """Dismounts the SD card."""
        import uos
        try:
            uos.umount(self.init.SD_MOUNT_POINT)
        except Exception:
            # Ignore any errors that occur
            pass
