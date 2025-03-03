"""
MicroPython Tesla Coil Controller (MPTCC)
by Cameron Prince
teslauniverse.com

init.py
Carries configuration and initialized hardware between classes.
"""

import _thread
import time
from machine import Pin
from ..lib.events import events

class Init:
    """
    A class to carry configuration and initialized hardware between
    classes for the MicroPython Tesla Coil Controller (MPTCC).

    Attributes:
    -----------
    display : object
        The display object.
    i2c_1 : object
        The first I2C bus.
    i2c_2 : object
        The second I2C bus.
    menu : object
        The menu object.
    spi_1 : object
        The first SPI bus.
    spi_2 : object
        The second SPI bus.
    switch_1 : object
        The first switch.
    switch_2 : object
        The second switch.
    switch_3 : object
        The third switch.
    switch_4 : object
        The fourth switch.
    uart : object
        The UART for MIDI input.
    """

    def __init__(self):
        """
        Constructs all the necessary attributes for the Init object.
        """
        self.display = None
        self.i2c_1 = None
        self.i2c_2 = None
        self.menu = None
        self.spi_1 = None
        self.spi_2 = None
        self.switch_1 = None
        self.switch_2 = None
        self.switch_3 = None
        self.switch_4 = None
        self.uart = None
        self.events = events
        self.rgb_led_color = {}
        self.ignore_input = False

    def validate_settings(self):
        """
        Validates the NUMBER_OF_COILS variable.
        Raises an error and stops the program if the constraints are not met.
        """
        # Ensure NUMBER_OF_COILS is at least 4
        if self.NUMBER_OF_COILS < 4:
            raise ValueError("NUMBER_OF_COILS must be at least 4. The program will now exit.")

        # Check if the number of coils is greater than 4
        if self.NUMBER_OF_COILS > 4:
            if self.display.DISPLAY_WIDTH < 256:
                raise ValueError("For more than 4 coils, the display width must be at least 256 pixels. The program will now exit.")

        # Check if the number of coils is greater than 8
        if self.NUMBER_OF_COILS > 8:
            raise ValueError("The maximum number of supported coils is currently 8. The program will now exit.")

    def init_i2c_1(self):
        """
        Initializes the first I2C bus.
        """
        from machine import I2C
        if not isinstance(self.i2c_1, I2C):
            self.i2c_1 = I2C(
                self.I2C_1_INTERFACE,
                scl=Pin(self.PIN_I2C_1_SCL),
                sda=Pin(self.PIN_I2C_1_SDA),
                freq=self.I2C_1_FREQ,
                timeout=self.I2C_1_TIMEOUT,
            )
        # Add a mutex for I2C communication to the init object.
        if not hasattr(self, 'i2c_1_mutex'):
            self.i2c_1_mutex = _thread.allocate_lock()

    def init_i2c_2(self):
        """
        Initializes the second I2C bus.
        """
        from machine import I2C
        if not isinstance(self.i2c_2, I2C):
            self.i2c_2 = I2C(
                self.I2C_2_INTERFACE,
                scl=Pin(self.PIN_I2C_2_SCL),
                sda=Pin(self.PIN_I2C_2_SDA),
                freq=self.I2C_2_FREQ,
                timeout=self.I2C_2_TIMEOUT,
            )
        # Add a mutex for I2C communication to the init object.
        if not hasattr(self, 'i2c_2_mutex'):
            self.i2c_2_mutex = _thread.allocate_lock()

    def init_spi_1(self):
        """
        Initializes the first SPI bus.
        """
        from machine import SPI
        if isinstance(self.spi_1, SPI):
            self.spi_1.deinit()
        miso = None
        if self.PIN_SPI_1_MISO is not None:
            miso = Pin(self.PIN_SPI_1_MISO)
        self.spi_1 = SPI(
            self.SPI_1_INTERFACE,
            baudrate=self.SPI_1_BAUD,
            polarity=0,
            phase=0,
            sck=Pin(self.PIN_SPI_1_SCK),
            mosi=Pin(self.PIN_SPI_1_MOSI),
            miso=miso,
        )

    def init_spi_2(self):
        """
        Initializes the second SPI bus.
        """
        from machine import SPI
        if isinstance(self.spi_2, SPI):
            self.spi_2.deinit()
        miso = None
        if self.PIN_SPI_2_MISO is not None:
            miso = Pin(self.PIN_SPI_2_MISO)
        self.spi_2 = SPI(
            self.SPI_2_INTERFACE,
            baudrate=self.SPI_2_BAUD,
            polarity=0,
            phase=0,
            sck=Pin(self.PIN_SPI_2_SCK),
            mosi=Pin(self.PIN_SPI_2_MOSI),
            miso=miso,
        )

    def init_uart(self):
        """
        Initializes the UART for MIDI input.
        """
        from machine import UART
        self.uart = UART(
            self.UART_INTERFACE,
            baudrate=self.UART_BAUD,
            rx=Pin(self.PIN_MIDI_INPUT),
        )

    def mutex_acquire(self, mutex, src):
        """
        Acquires a mutex and provides a common function for debugging.
        """
        if self.MUTEX_DEBUGGING:
            print("mutex_acquire: ", src)
        mutex.acquire()

    def mutex_release(self, mutex, src):
        """
        Releases a mutex and provides a common function for debugging.
        """
        if self.MUTEX_DEBUGGING:
            print("mutex_release: ", src)
        mutex.release()

init = Init()
