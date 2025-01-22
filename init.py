"""
MicroPython Tesla Coil Controller (MPTCC)
by Cameron Prince
teslauniverse.com

init.py
Shared configuration and hardware initialization.
"""

from machine import Pin

class Init:

    # I2C bus 1 pin assignments and settings.
    # (used by the default PCA9685 RGB LED hardware)
    PIN_I2C_1_SCL = 17
    PIN_I2C_1_SDA = 16
    I2C_1_INTERFACE = 0
    I2C_1_FREQ = 400000

    # I2C bus 2 pin assignments and settings.
    # (used by the default PCA9685 RGB LED hardware)
    PIN_I2C_2_SCL = 19
    PIN_I2C_2_SDA = 18
    I2C_2_INTERFACE = 1
    I2C_2_FREQ = 400000

    # SPI bus pin assignments and settings.
    # (used by SD card reader).
    PIN_SPI_SCK = 2
    PIN_SPI_MOSI = 3
    PIN_SPI_MISO = 4
    PIN_SPI_CS = 1
    PIN_SPI_DC = 4
    PIN_SPI_RST = 16
    SPI_INTERFACE = 0
    SPI_BAUD = 1000000

    # Output pin assignments.
    PIN_OUTPUT_1 = 22
    PIN_OUTPUT_2 = 6
    PIN_OUTPUT_3 = 7
    PIN_OUTPUT_4 = 8

    # Battery status ADC pin assignment and settings.
    PIN_BATT_STATUS_ADC = 28
    # Adjust for specific supply voltage used.
    VOLTAGE_DROP_FACTOR = 848.5

    # MIDI input pin assignment and UART settings.
    PIN_MIDI_INPUT = 13
    UART_INTERFACE = 0
    UART_BAUD = 31250

    # Miscellaneous definitions.
    SD_MOUNT_POINT = "/sd"
    CONFIG_PATH = "/mptcc/config.json"

    # In my set up, these frequencies cause the display to go haywire. I'm not sure if it's
    # a hardware issue, a display driver issue, or what exactly. Will try a different display
    # to confirm.
    BANNED_INTERRUPTER_FREQUENCIES = [
        139, 339, 239, 289, 389, 390, 391, 392, 393, 394, 395,
        396, 397, 398, 399, 439, 489, 539, 639, 739, 839, 939
    ]

    def __init__(self):
        """Initializes the hardware and sets up shared attributes."""

        # Attributes for sharing among screens.
        self.spi = None
        self.uart = None
        self.i2c_1 = None
        self.i2c_2 = None
        self.menu = None
        self.display = None

    """
    Bus and port handling.
    """
    def init_i2c_1(self):
        """Initializes the first I2C bus."""
        from machine import I2C
        if not isinstance(self.i2c_1, I2C):
            self.i2c_1 = I2C(
                self.I2C_1_INTERFACE,
                scl=Pin(self.PIN_I2C_1_SCL),
                sda=Pin(self.PIN_I2C_1_SDA),
                freq=self.I2C_1_FREQ
            )

    def init_i2c_2(self):
        """Initializes the second I2C bus."""
        from machine import I2C
        if not isinstance(self.i2c_2, I2C):
            self.i2c_2 = I2C(
                self.I2C_2_INTERFACE,
                scl=Pin(self.PIN_I2C_2_SCL),
                sda=Pin(self.PIN_I2C_2_SDA),
                freq=self.I2C_2_FREQ
            )

    def init_spi(self):
        """Initializes the SPI bus."""
        from machine import SPI
        if isinstance(self.spi, SPI):
            self.spi.deinit()
        self.spi = SPI(
            self.SPI_INTERFACE,
            baudrate=self.SPI_BAUD,
            polarity=0,
            phase=0,
            sck=Pin(self.PIN_SPI_SCK),
            mosi=Pin(self.PIN_SPI_MOSI),
            miso=Pin(self.PIN_SPI_MISO)
        )

    def init_uart(self):
        """Initializes the UART for MIDI input."""
        from machine import UART
        self.uart = UART(
            self.UART_INTERFACE,
            baudrate=self.UART_BAUD,
            rx=Pin(self.PIN_MIDI_INPUT)
        )

init = Init()

