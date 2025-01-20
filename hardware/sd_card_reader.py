from .hardware import Hardware
from machine import SPI
import sdcard
import uos

class SDCardReader(Hardware):

    PIN_SPI_SCK = 2
    PIN_SPI_MOSI = 3
    PIN_SPI_MISO = 4
    PIN_SPI_CS_DISPLAY = 5
    PIN_SPI_CS_SD = 1
    PIN_SPI_DC = 4
    PIN_SPI_RST = 16
    SPI_INTERFACE = 0
    SPI_BAUD = 1000000

    def __init__(self):
        super().__init__()

        # Initializes the dedicated SPI bus.
        if isinstance(self.spi, SPI):
            self.spi.deinit()
        self.spi = SPI(
            SPI_INTERFACE,
            baudrate=SPI_BAUD,
            polarity=0,
            phase=0,
            sck=Pin(PIN_SPI_SCK),
            mosi=Pin(PIN_SPI_MOSI),
            miso=Pin(PIN_SPI_MISO)
        )

    def init_sd(self):
        try:
            sd = sdcard.SDCard(self.spi, Pin(PIN_SPI_CS_SD, Pin.OUT))
            # Mount the disk.
            uos.mount(sd, Init.SD_MOUNT_POINT)
        except OSError as e:
            print(f"Error initializing SD card: {e}")

    def deinit_sd(self):
        """Dismounts the SD card."""
        import uos
        try:
            uos.umount(Init.SD_MOUNT_POINT)
        except Exception:
            # Ignore any errors that occur
            pass