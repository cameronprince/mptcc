"""
MicroPython Tesla Coil Controller (MPTCC)
by Cameron Prince
teslauniverse.com

init.py
Constants, shared attributes and initialization code.
"""

from machine import Pin

class Init:
    """
    A class to initialize and manage the hardware components and shared attributes
    for the MicroPython Tesla Coil Controller (MPTCC).

    Attributes:
    -----------
    Various hardware and configuration attributes necessary for the operation of the MPTCC.
    """

    def __init__(self):
        """Initializes the hardware and sets up shared attributes."""
        # I2C bus pin assignments and settings
        # (used by the PCA9685 PWM driver for RGB LEDs).
        self.PIN_IC2_SCL = 19
        self.PIN_IC2_SDA = 18
        self.I2C_INTERFACE = 1
        self.I2C_FREQ = 400000

        # SPI bus pin assignments and settings
        # (used by SSD1306 display and SD card reader).
        self.PIN_SPI_SCK = 2
        self.PIN_SPI_MOSI = 3
        self.PIN_SPI_MISO = 4
        self.PIN_SPI_CS_DISPLAY = 5
        self.PIN_SPI_CS_SD = 1
        self.PIN_SPI_DC = 4
        self.PIN_SPI_RST = 16
        self.SPI_INTERFACE = 0
        self.SPI_BAUD = 1000000

        # Fiber optic transmitter pin assignments.
        self.PIN_XMTR_1 = 22
        self.PIN_XMTR_2 = 6
        self.PIN_XMTR_3 = 7
        self.PIN_XMTR_4 = 8

        # Rotary encoder pin assignments.
        self.PIN_ROTARY_1_CLK = 10
        self.PIN_ROTARY_1_DT = 11
        self.PIN_ROTARY_1_SW = 12

        self.PIN_ROTARY_2_CLK = 9
        self.PIN_ROTARY_2_DT = 14
        self.PIN_ROTARY_2_SW = 15

        self.PIN_ROTARY_3_CLK = 27
        self.PIN_ROTARY_3_DT = 26
        self.PIN_ROTARY_3_SW = 0

        self.PIN_ROTARY_4_CLK = 21
        self.PIN_ROTARY_4_DT = 20
        self.PIN_ROTARY_4_SW = 17

        # Battery status ADC pin assignment and settings.
        self.PIN_BATT_STATUS_ADC = 28
        # Adjust for specific supply voltage used.
        self.VOLTAGE_DROP_FACTOR = 848.5

        # RGB LED assignments (PCA9685 channels).
        self.PCA_LED1_RED = 9
        self.PCA_LED1_GREEN = 10
        self.PCA_LED1_BLUE = 11

        self.PCA_LED2_RED = 6
        self.PCA_LED2_GREEN = 7
        self.PCA_LED2_BLUE = 8

        self.PCA_LED3_RED = 3
        self.PCA_LED3_GREEN = 4
        self.PCA_LED3_BLUE = 5

        self.PCA_LED4_RED = 0
        self.PCA_LED4_GREEN = 1
        self.PCA_LED4_BLUE = 2

        # MIDI input pin assignment and UART settings.
        self.PIN_MIDI_INPUT = 13
        self.UART_INTERFACE = 0
        self.UART_BAUD = 31250

        # Display-related definitions.
        self.DISPLAY_WIDTH = 128
        self.DISPLAY_HEIGHT = 64
        self.DISPLAY_LINE_HEIGHT = 12
        self.DISPLAY_FONT_WIDTH = 8
        self.DISPLAY_FONT_HEIGHT = 8
        self.DISPLAY_HEADER_HEIGHT = 10
        self.DISPLAY_ITEMS_PER_PAGE = 4

        # Miscellaneous definitions.
        self.PCA9685_FREQ = 1000
        self.SD_MOUNT_POINT = "/sd"
        self.CONFIG_PATH = "/mptcc/config.json"
        # In my set up, these frequencies cause the display to go haywire. I'm not sure if it's
        # a hardware issue, a display driver issue, or what exactly. Will try a different display
        # to confirm.
        self.BANNED_INTERRUPTER_FREQUENCIES = [
            139, 339, 239, 289, 389, 390, 391, 392, 393, 394, 395,
            396, 397, 398, 399, 439, 489, 539, 639, 739, 839, 939
        ]

        # Attributes for sharing among screens.
        self.spi = None
        self.display = None
        self.uart = None
        self.i2c = None
        self.xmtrs = None
        self.pca = None
        self.encoders = None
        self.switch_1 = None
        self.switch_2 = None
        self.switch_3 = None
        self.switch_4 = None
        self.leds = None
        self.rotary_instances = None
        self.menu = None

        # Initialize the hardware.
        self.init_display()
        self.init_xmtrs()
        self.init_encoders()
        self.init_switches()
        self.init_leds()

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

    def init_display(self):
        """Initializes the display on the SPI bus."""
        self.init_spi()
        # For best results, use the SSD1306 driver from:
        # https://github.com/TimHanewich/MicroPython-SSD1306
        import ssd1306
        self.display = ssd1306.SSD1306_SPI(
            self.DISPLAY_WIDTH,
            self.DISPLAY_HEIGHT,
            self.spi,
            Pin(self.PIN_SPI_DC),
            Pin(self.PIN_SPI_RST),
            Pin(self.PIN_SPI_CS_DISPLAY)
        )

    def init_sd(self):
        """Initializes the SD card reader on the SPI bus."""
        self.init_spi()
        import sdcard
        import uos
        try:
            sd = sdcard.SDCard(self.spi, Pin(self.PIN_SPI_CS_SD, Pin.OUT))
            # Mount the disk.
            uos.mount(sd, self.SD_MOUNT_POINT)
        except OSError as e:
            print(f"Error initializing SD card: {e}")

    def deinit_sd(self):
        """Dismounts the SD card."""
        import uos
        try:
            uos.umount(self.SD_MOUNT_POINT)
        except Exception:
            # Ignore any errors that occur
            pass

    def init_uart(self):
        """Initializes the UART for MIDI input."""
        # self.deinit_uart()
        from machine import UART
        self.uart = UART(
            self.UART_INTERFACE,
            baudrate=self.UART_BAUD,
            rx=Pin(self.PIN_MIDI_INPUT)
        )

    def deinit_uart(self):
        """Shuts down the UART for MIDI input."""
        from machine import UART
        if isinstance(self.uart, UART):
            self.uart.deinit()

    def init_xmtrs(self):
        """Initializes all the fiber optic transmitters."""
        from machine import PWM
        self.xmtrs = [
            PWM(Pin(self.PIN_XMTR_1)),
            PWM(Pin(self.PIN_XMTR_2)),
            PWM(Pin(self.PIN_XMTR_3)),
            PWM(Pin(self.PIN_XMTR_4))
        ]

    def init_i2c(self):
        """Initializes the I2C bus for communication with the external PWM driver which drives the RGB LEDs."""
        self.deinit_i2c()
        from machine import I2C
        self.i2c = I2C(
            self.I2C_INTERFACE,
            scl=Pin(self.PIN_IC2_SCL),
            sda=Pin(self.PIN_IC2_SDA),
            freq=self.I2C_FREQ
        )

    def deinit_i2c(self):
        """Shuts down the I2C bus."""
        from machine import I2C
        if isinstance(self.i2c, I2C):
            self.i2c.deinit()

    def init_pca(self):
        """Initializes the external PWM driver."""
        self.init_i2c()
        self.deinit_pca()
        from pca9685 import PCA9685
        self.pca = PCA9685(self.i2c)
        self.pca.freq(self.PCA9685_FREQ)

    def deinit_pca(self):
        """Shuts down the external PWM driver."""
        from pca9685 import PCA9685
        if isinstance(self.pca, PCA9685):
            self.pca.reset()

    def init_encoders(self):
        """Prepares the array of encoder pin assignments."""
        self.encoders = [
            {'clk': self.PIN_ROTARY_1_CLK, 'dt': self.PIN_ROTARY_1_DT},
            {'clk': self.PIN_ROTARY_2_CLK, 'dt': self.PIN_ROTARY_2_DT},
            {'clk': self.PIN_ROTARY_3_CLK, 'dt': self.PIN_ROTARY_3_DT},
            {'clk': self.PIN_ROTARY_4_CLK, 'dt': self.PIN_ROTARY_4_DT}
        ]

    def init_switches(self):
        """Initializes all the encoder switches."""
        self.switch_1 = Pin(self.PIN_ROTARY_1_SW, Pin.IN, Pin.PULL_UP)
        self.switch_2 = Pin(self.PIN_ROTARY_2_SW, Pin.IN, Pin.PULL_UP)
        self.switch_3 = Pin(self.PIN_ROTARY_3_SW, Pin.IN, Pin.PULL_UP)
        self.switch_4 = Pin(self.PIN_ROTARY_4_SW, Pin.IN, Pin.PULL_UP)

    def init_leds(self):
        """Initializes all the RGB LEDs on the external PWM driver."""
        self.init_pca()
        from mptcc.rgb import RGB
        self.leds = [
            RGB(self.pca, red_channel=self.PCA_LED1_RED, green_channel=self.PCA_LED1_GREEN, blue_channel=self.PCA_LED1_BLUE),
            RGB(self.pca, red_channel=self.PCA_LED2_RED, green_channel=self.PCA_LED2_GREEN, blue_channel=self.PCA_LED2_BLUE),
            RGB(self.pca, red_channel=self.PCA_LED3_RED, green_channel=self.PCA_LED3_GREEN, blue_channel=self.PCA_LED3_BLUE),
            RGB(self.pca, red_channel=self.PCA_LED4_RED, green_channel=self.PCA_LED4_GREEN, blue_channel=self.PCA_LED4_BLUE)
        ]

init = Init()