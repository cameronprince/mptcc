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
    A class to initialize and manage the hardware components and
    shared attributes for the MicroPython Tesla Coil Controller (MPTCC).
    """
    # I2C bus pin assignments and settings
    # (used by the SSD1306 display and PCA9685 PWM driver
    # for RGB LEDs).
    PIN_IC2_SCL = 19
    PIN_IC2_SDA = 18
    I2C_INTERFACE = 1
    I2C_FREQ = 400000

    # SPI bus pin assignments and settings
    # (used by SD card reader).
    PIN_SPI_SCK = 2
    PIN_SPI_MOSI = 3
    PIN_SPI_MISO = 4
    PIN_SPI_CS_DISPLAY = 5
    PIN_SPI_CS_SD = 1
    PIN_SPI_DC = 4
    PIN_SPI_RST = 16
    SPI_INTERFACE = 0
    SPI_BAUD = 1000000

    # Fiber optic transmitter pin assignments.
    PIN_XMTR_1 = 22
    PIN_XMTR_2 = 6
    PIN_XMTR_3 = 7
    PIN_XMTR_4 = 8

    # Rotary encoder pin assignments.
    PIN_ROTARY_1_CLK = 10
    PIN_ROTARY_1_DT = 11
    PIN_ROTARY_1_SW = 12

    PIN_ROTARY_2_CLK = 9
    PIN_ROTARY_2_DT = 14
    PIN_ROTARY_2_SW = 15

    PIN_ROTARY_3_CLK = 27
    PIN_ROTARY_3_DT = 26
    PIN_ROTARY_3_SW = 0

    PIN_ROTARY_4_CLK = 21
    PIN_ROTARY_4_DT = 20
    PIN_ROTARY_4_SW = 17

    # Enable/disable encoder pin pull-up resistors.
    ROTARY_PULL_UP = False

    # Battery status ADC pin assignment and settings.
    PIN_BATT_STATUS_ADC = 28
    # Adjust for specific supply voltage used.
    VOLTAGE_DROP_FACTOR = 848.5

    # RGB LED assignments (PCA9685 channels).
    PCA_LED1_RED = 0
    PCA_LED1_GREEN = 1
    PCA_LED1_BLUE = 2

    PCA_LED2_RED = 3
    PCA_LED2_GREEN = 4
    PCA_LED2_BLUE = 5

    PCA_LED3_RED = 6
    PCA_LED3_GREEN = 7
    PCA_LED3_BLUE = 8

    PCA_LED4_RED = 9
    PCA_LED4_GREEN = 10
    PCA_LED4_BLUE = 11

    # MIDI input pin assignment and UART settings.
    PIN_MIDI_INPUT = 13
    UART_INTERFACE = 0
    UART_BAUD = 31250

    # Display-related definitions.
    DISPLAY_WIDTH = 128
    DISPLAY_HEIGHT = 64
    DISPLAY_LINE_HEIGHT = 12
    DISPLAY_FONT_WIDTH = 8
    DISPLAY_FONT_HEIGHT = 8
    DISPLAY_HEADER_HEIGHT = 10
    DISPLAY_ITEMS_PER_PAGE = 4

    # Miscellaneous definitions.
    PCA9685_FREQ = 1000
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
            Init.SPI_INTERFACE,
            baudrate=Init.SPI_BAUD,
            polarity=0,
            phase=0,
            sck=Pin(Init.PIN_SPI_SCK),
            mosi=Pin(Init.PIN_SPI_MOSI),
            miso=Pin(Init.PIN_SPI_MISO)
        )

    def init_display(self):
        """Initializes the display on the SPI bus."""
        self.init_i2c()
        # For best results, use the SSD1306 driver from:
        # https://github.com/TimHanewich/MicroPython-SSD1306
        import ssd1306
        self.display = ssd1306.SSD1306_I2C(
            Init.DISPLAY_WIDTH,
            Init.DISPLAY_HEIGHT,
            self.i2c,
        )

    def init_sd(self):
        """Initializes the SD card reader on the SPI bus."""
        self.init_spi()
        import sdcard
        import uos
        try:
            sd = sdcard.SDCard(self.spi, Pin(Init.PIN_SPI_CS_SD, Pin.OUT))
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

    def init_uart(self):
        """Initializes the UART for MIDI input."""
        from machine import UART
        self.uart = UART(
            Init.UART_INTERFACE,
            baudrate=Init.UART_BAUD,
            rx=Pin(Init.PIN_MIDI_INPUT)
        )

    def init_xmtrs(self):
        """Initializes all the fiber optic transmitters."""
        from machine import PWM
        self.xmtrs = [
            PWM(Pin(Init.PIN_XMTR_1)),
            PWM(Pin(Init.PIN_XMTR_2)),
            PWM(Pin(Init.PIN_XMTR_3)),
            PWM(Pin(Init.PIN_XMTR_4))
        ]

    def init_i2c(self):
        """Initializes the I2C bus for communication with the external PWM driver which drives the RGB LEDs."""
        from machine import I2C
        self.i2c = I2C(
            Init.I2C_INTERFACE,
            scl=Pin(Init.PIN_IC2_SCL),
            sda=Pin(Init.PIN_IC2_SDA),
            freq=Init.I2C_FREQ
        )

    def init_pca(self):
        """Initializes the external PWM driver."""
        self.init_i2c()
        self.deinit_pca()
        from pca9685 import PCA9685
        self.pca = PCA9685(self.i2c)
        self.pca.freq(Init.PCA9685_FREQ)

    def deinit_pca(self):
        """Shuts down the external PWM driver."""
        from pca9685 import PCA9685
        if isinstance(self.pca, PCA9685):
            self.pca.reset()

    def init_encoders(self):
        """Prepares the array of encoder pin assignments."""
        self.encoders = [
            {'clk': Init.PIN_ROTARY_1_CLK, 'dt': Init.PIN_ROTARY_1_DT},
            {'clk': Init.PIN_ROTARY_2_CLK, 'dt': Init.PIN_ROTARY_2_DT},
            {'clk': Init.PIN_ROTARY_3_CLK, 'dt': Init.PIN_ROTARY_3_DT},
            {'clk': Init.PIN_ROTARY_4_CLK, 'dt': Init.PIN_ROTARY_4_DT}
        ]

    def init_switches(self):
        """Initializes all the encoder switches."""
        self.switch_1 = Pin(Init.PIN_ROTARY_1_SW, Pin.IN, Pin.PULL_UP)
        self.switch_2 = Pin(Init.PIN_ROTARY_2_SW, Pin.IN, Pin.PULL_UP)
        self.switch_3 = Pin(Init.PIN_ROTARY_3_SW, Pin.IN, Pin.PULL_UP)
        self.switch_4 = Pin(Init.PIN_ROTARY_4_SW, Pin.IN, Pin.PULL_UP)

    def init_leds(self):
        """Initializes all the RGB LEDs on the external PWM driver."""
        self.init_pca()
        from mptcc.lib.rgb import RGB
        self.leds = [
            RGB(self.pca, red_channel=Init.PCA_LED1_RED, green_channel=Init.PCA_LED1_GREEN, blue_channel=Init.PCA_LED1_BLUE),
            RGB(self.pca, red_channel=Init.PCA_LED2_RED, green_channel=Init.PCA_LED2_GREEN, blue_channel=Init.PCA_LED2_BLUE),
            RGB(self.pca, red_channel=Init.PCA_LED3_RED, green_channel=Init.PCA_LED3_GREEN, blue_channel=Init.PCA_LED3_BLUE),
            RGB(self.pca, red_channel=Init.PCA_LED4_RED, green_channel=Init.PCA_LED4_GREEN, blue_channel=Init.PCA_LED4_BLUE)
        ]

init = Init()