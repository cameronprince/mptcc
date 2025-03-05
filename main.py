"""
MicroPython Tesla Coil Controller (MPTCC)
by Cameron Prince
teslauniverse.com

main.py
Defines and initializes the hardware and menu.
"""

# Prepare the init object to store configuration and initialized hardware.
from mptcc.hardware.init import init


"""
General Settings
"""
# The number of coils the controller is to support. An equal number of encoders,
# RGB LEDs and outputs is expected. When going beyond four coils, a wider display
# is required. Valid values are currently 4-8.
init.NUMBER_OF_COILS = 4

# Asyncio RGB LED updates are available in cases where both threads update
# I2C devices on the same bus. This setting causes LED colors to be stored
# instead of calling the hardware directly. Then an asynchronous function
# detects the values being updated and triggers the hardware update. This is
# because both threads can't reliably communicate with the same bus at the
# same time. This setting is most needed with I2CEncoders where the integrated
# RGB LED shares the same interface with the encoder. Without this setting
# enabled, operating encoders during output/playback can cause freezes.
# This feature should work on any RGB LED hardware, but keep in mind it does
# have latency. RGB LEDs should have a dedicated bus instead, if possible.
# Default is False as the default RGB LEDs are on a dedicated bus.
init.RGB_LED_ASYNCIO_POLLING = False

# Enable mutex debugging. When enabled, print statements are issued each time
# a mutex is acquired or released.
init.MUTEX_DEBUGGING = False


"""
Interface Settings

Defaults to two I2C interfaces the first dedicated to the SSD1306 display and
the second dedicated to the PCA9685 RGB LED driver, along with a single SPI
interface dedicated to the SD card reader. The SD card is read incrementally
during MIDI playback. It must have a dedicated bus.
"""
# I2C bus 1 pin assignments and settings.
init.PIN_I2C_1_SCL = 17
init.PIN_I2C_1_SDA = 16
init.I2C_1_INTERFACE = 0
init.I2C_1_FREQ = 400000
init.I2C_1_TIMEOUT = 50000

# I2C bus 2 pin assignments and settings.
init.PIN_I2C_2_SCL = 19
init.PIN_I2C_2_SDA = 18
init.I2C_2_INTERFACE = 1
init.I2C_2_FREQ = 400000
init.I2C_2_TIMEOUT = 50000

# SPI bus 1 pin assignments and settings.
init.SPI_1_INTERFACE = 0
init.SPI_1_BAUD = 1000000
init.PIN_SPI_1_SCK = 2
init.PIN_SPI_1_MOSI = 3
init.PIN_SPI_1_MISO = 4
init.PIN_SPI_1_CS = 5
init.PIN_SPI_1_DC = None
init.PIN_SPI_1_RST = None

# SPI bus 2 pin assignments and settings.
# init.SPI_2_INTERFACE = 1
# init.SPI_2_BAUD = 10000000
# init.PIN_SPI_2_SCK = 10
# init.PIN_SPI_2_MOSI = 11
# init.PIN_SPI_2_MISO = None
# init.PIN_SPI_2_CS = 13
# init.PIN_SPI_2_DC = 12
# init.PIN_SPI_2_RST = 14


"""
Display

Select one of the display options below by commenting out the default
option and removing the comment for the desired, alternate option.

The display needs to be initialized first as it needs a large block of
contiguous memory.
"""

# Shared display settings.
# init.DISPLAY_INTERFACE = "I2C_1" # Either I2C_1, I2C_2, SPI_1 or SPI_2.
init.DISPLAY_INTERFACE = "I2C_1"
init.DISPLAY_I2C_ADDR = 0x3C     # Required for I2C displays.

# SSD1306 0.96" 128X64 OLED LCD Display (https://amzn.to/40sf11I)
# Interface: I2C/SPI
# Requires: https://github.com/TimHanewich/MicroPython-SSD1306
# Note: This library only supports standard frame buffer commands.
from mptcc.hardware.display.ssd1306 import SSD1306 as display  # Default option.

# SSD1309 2.42" 128x64 OLED LCD Display (https://amzn.to/40wQWbs)
# Interface: I2C/SPI
# Requires: https://github.com/rdagger/micropython-ssd1309
# Note: This library supports custom fonts, shapes, images, and more, beyond
# the standard frame buffer commands. This driver also works with SSD1306 displays.
# from mptcc.hardware.display.ssd1309 import SSD1309 as display  # Alternate option.

# SSD1322 3.12" 256x64 OLED LCD Display (https://amzn.to/4jupi6c)
# Interface: SPI
# Requires: https://github.com/rdagger/micropython-ssd1322
# Note: This library supports custom fonts, shapes, images, and more, beyond
# the standard frame buffer commands.
# from mptcc.hardware.display.ssd1322 import SSD1322 as display  # Alternate option.

init.display = display()


"""
Input Devices

Select one of the input device options below by commenting out the default option
and removing the comment for the desired, alternate option.

Defaults to generic KY-040 quadrature encoders with switches. This is the most
reliable input method, but consumes twelve GPIO pins.
"""

# KY-040 Rotary Encoder - https://amzn.to/42E63l1 or https://amzn.to/3CdzIqi
# Requires: https://github.com/miketeachman/micropython-rotary

# Rotary encoder pin assignments.
init.PIN_ROTARY_1_CLK = 14
init.PIN_ROTARY_1_DT = 13
init.PIN_ROTARY_1_SW = 15

init.PIN_ROTARY_2_CLK = 10
init.PIN_ROTARY_2_DT = 9
init.PIN_ROTARY_2_SW = 11

init.PIN_ROTARY_3_CLK = 21
init.PIN_ROTARY_3_DT = 22
init.PIN_ROTARY_3_SW = 20

init.PIN_ROTARY_4_CLK = 27
init.PIN_ROTARY_4_DT = 0
init.PIN_ROTARY_4_SW = 26

# Enable/disable encoder pin pull-up resistors.
# Most of the PCB-mounted encoders have pull-ups on the boards.
init.ROTARY_PULL_UP = False

from mptcc.hardware.input.ky_040 import KY040 as inputs  # Default option.

# I2CEncoder V2.1 - https://www.duppa.net/shop/i2cencoder-v2-1-with-soldered-accessory
# Requires: https://github.com/cameronprince/i2cEncoderLibV2

init.I2CENCODER_I2C_INSTANCE = 1
init.I2CENCODER_TYPE = 'RGB' # STANDARD or RGB
init.I2CENCODER_ADDRESSES = [0x50, 0x30, 0x60, 0x44] # 80, 48, 96, 68
init.I2CENCODER_INTERRUPT_PIN = 0

# from mptcc.hardware.input.i2cencoder import I2CEncoder as inputs  # Alternate option.

# I2CEncoderMini V1.2 - https://www.duppa.net/shop/i2cencoder-mini-with-soldered-accessory
# Requires: https://github.com/cameronprince/I2CEncoderMini

init.I2CENCODER_MINI_I2C_INSTANCE = 1
init.I2CENCODER_MINI_ADDRESSES = [0x21, 0x22, 0x23, 0x24]
init.I2CENCODER_MINI_INTERRUPT_PIN = 20

# from mptcc.hardware.input.i2cencoder_mini import I2CEncoderMini as inputs  # Alternate option.

init.inputs = inputs()


"""
RGB LEDs

Select one of the RGB LED options below by commenting out the default option
and removing the comment for the desired, alternate option.

Default is the PCA9685 external PWM. It provides a low-cost method of interfacing
RGB LEDs with the I2C bus, saving at least six GPIO pins. It also negates the
need for current limiting resistors for the LEDs.
"""

# PCA9685 16-channel 12-bit PWM - https://amzn.to/4jf2E1J
# Requires: https://github.com/kevinmcaleer/pca9685_for_pico

init.RGB_PCA9685_I2C_INSTANCE = 2
init.RGB_PCA9685_ADDR = 0x40
init.RGB_PCA9685_FREQ = 1000

init.RGB_PCA9685_LED1_RED = 0
init.RGB_PCA9685_LED1_GREEN = 1
init.RGB_PCA9685_LED1_BLUE = 2

init.RGB_PCA9685_LED2_RED = 3
init.RGB_PCA9685_LED2_GREEN = 4
init.RGB_PCA9685_LED2_BLUE = 5

init.RGB_PCA9685_LED3_RED = 6
init.RGB_PCA9685_LED3_GREEN = 7
init.RGB_PCA9685_LED3_BLUE = 8

init.RGB_PCA9685_LED4_RED = 9
init.RGB_PCA9685_LED4_GREEN = 10
init.RGB_PCA9685_LED4_BLUE = 11

from mptcc.hardware.rgb_led.pca9685 import PCA9685 as rgb_led  # Default option.

# I2CEncoder V2.1 - https://www.duppa.net/shop/i2cencoder-v2-1-with-soldered-accessory
# Requires: https://github.com/cameronprince/i2cEncoderLibV2
# from mptcc.hardware.rgb_led.i2cencoder import I2CEncoder as rgb_led  # Alternate option.

# RGB LED Ring Small - https://www.duppa.net/shop/rgb-led-ring-small/
# Requires: https://github.com/cameronprince/RGB_LED_Ring_Small

init.RGB_LED_RING_SMALL_I2C_INSTANCE = 2
init.RGB_LED_RING_SMALL_ADDRESSES = [0x68, 0x6C, 0x62, 0x61]
# init.RGB_LED_RING_SMALL_DEFAULT_COLOR = "#000000"
init.RGB_LED_RING_SMALL_DEFAULT_COLOR = "#326400"
# init.RGB_LED_RING_SMALL_DEFAULT_COLOR = "vu_meter"
init.RGB_LED_RING_SMALL_THRESHOLD_BRIGHTNESS = 16
init.RGB_LED_RING_SMALL_FULL_BRIGHTNESS = 32
init.RGB_LED_RING_SMALL_ROTATION = 180
init.RGB_LED_RING_SMALL_DELAY_BETWEEN_STEPS = 0.005
init.RGB_LED_RING_SMALL_MODE = "vu_meter" # Either "status" or "vu_meter"

# from mptcc.hardware.rgb_led.rgb_led_ring_small import RGBLEDRingSmall as rgb_led  # Alternate option.

# Serial Wombat 18AB - https://amzn.to/4ih0i0X
# Requires: https://github.com/BroadwellConsultingInc/SerialWombat/tree/main/SerialWombat18A_18B

# init.RGB_WOMBAT_18AB_I2C_INSTANCE = 2
# init.RGB_WOMBAT_18AB_INIT_DELAY = 0.2
# init.RGB_WOMBAT_18AB_ADDR = 0x6B

# init.RGB_WOMBAT_18AB_LED1_RED = 12
# init.RGB_WOMBAT_18AB_LED1_GREEN = 11
# init.RGB_WOMBAT_18AB_LED1_BLUE = 10

# init.RGB_WOMBAT_18AB_LED2_RED = 15
# init.RGB_WOMBAT_18AB_LED2_GREEN = 14
# init.RGB_WOMBAT_18AB_LED2_BLUE = 13

# init.RGB_WOMBAT_18AB_LED3_RED = 0
# init.RGB_WOMBAT_18AB_LED3_GREEN = 5
# init.RGB_WOMBAT_18AB_LED3_BLUE = 6

# init.RGB_WOMBAT_18AB_LED4_RED = 7
# init.RGB_WOMBAT_18AB_LED4_GREEN = 8 
# init.RGB_WOMBAT_18AB_LED4_BLUE = 9

# from mptcc.hardware.rgb_led.wombat_18ab import Wombat_18AB as rgb_led # Alternate option.

init.rgb_driver = rgb_led()


"""
Outputs

Select one of the output options below by commenting out the default option
and removing the comment for the desired, alternate option.

Default is the hardware PWM, for now. More testing is required.
"""

# Output pin assignments.
init.PIN_OUTPUT_1 = 1
init.PIN_OUTPUT_2 = 8
init.PIN_OUTPUT_3 = 7
init.PIN_OUTPUT_4 = 6

# GPIO pin outputs with hardware PWM.
from mptcc.hardware.output.gpio_pwm import GPIO_PWM as output # Default option.

# GPIO pin outputs with Programmable Input Output (PIO).
# from mptcc.hardware.output.gpio_pio import GPIO_PIO as output # Alternate option.

# GPIO pin outputs with software PWM (bit banging).
# from mptcc.hardware.output.gpio_bitbang import GPIO_BitBang as output # Alternate option.

# GPIO pin outputs with timers.
# from mptcc.hardware.output.gpio_timer import GPIO_Timer as output # Alternate option.

# PCA9685 16-channel 12-bit PWM - https://amzn.to/4jf2E1J
# Requires: https://github.com/kevinmcaleer/pca9685_for_pico

# init.OUTPUT_PCA9685_I2C_INSTANCE = 1
# init.OUTPUT_PCA9685_INIT_DELAY = 0.2
# init.OUTPUT_PCA9685_1_ADDR = 0x50
# init.OUTPUT_PCA9685_1_CHAN = 0
# init.OUTPUT_PCA9685_2_ADDR = 0x48
# init.OUTPUT_PCA9685_2_CHAN = 0
# init.OUTPUT_PCA9685_3_ADDR = 0x44
# init.OUTPUT_PCA9685_3_CHAN = 0
# init.OUTPUT_PCA9685_4_ADDR = 0x42
# init.OUTPUT_PCA9685_4_CHAN = 0

# from mptcc.hardware.output.pca9685 import PCA9685 as output # Alternate option.

# Serial Wombat 18AB - https://amzn.to/4ih0i0X
# Requires: https://github.com/BroadwellConsultingInc/SerialWombat/tree/main/SerialWombat18A_18B

# init.OUTPUT_WOMBAT_18AB_I2C_INSTANCE = 2
# init.OUTPUT_WOMBAT_18AB_INIT_DELAY = 0.2
# init.OUTPUT_WOMBAT_18AB_ADDR = 0x6B
# init.OUTPUT_WOMBAT_18AB_1_PIN = 16
# init.OUTPUT_WOMBAT_18AB_2_PIN = 17
# init.OUTPUT_WOMBAT_18AB_3_PIN = 18
# init.OUTPUT_WOMBAT_18AB_4_PIN = 19

# from mptcc.hardware.output.wombat_18ab import Wombat_18AB as output # Alternate option.

init.output = output()


"""
SD Card Reader
"""
init.SD_CARD_READER_SPI_INSTANCE = 1
init.SD_CARD_READER_MOUNT_POINT = "/sd"

from mptcc.hardware.sd_card_reader import SDCardReader as sd_card_reader
init.sd_card_reader = sd_card_reader()


"""
Battery Status
"""
init.PIN_BATT_STATUS_ADC = 28
init.VOLTAGE_DROP_FACTOR = 848.5 # Adjust for your supply voltage.


"""
MIDI Input
"""
init.PIN_MIDI_INPUT = 1
init.UART_INTERFACE = 0
init.UART_BAUD = 31250


"""
User Configuration
"""
init.CONFIG_PATH = "/mptcc/config.json"


"""
Settings Validation
"""
init.validate_settings()


"""
Menu Definition
"""
from mptcc.lib.menu import Menu, MenuScreen, SubMenuItem, Screen
import mptcc.screens as screens

# Define and display the menu.
init.menu = Menu(
    init.display,
    init.display.DISPLAY_ITEMS_PER_PAGE,
    init.display.DISPLAY_LINE_HEIGHT,
    init.display.DISPLAY_FONT_WIDTH,
    init.display.DISPLAY_FONT_HEIGHT
)

init.menu.set_screen(MenuScreen('MicroPython TCC')
    .add(screens.Interrupter('Interrupter'))
    .add(screens.MIDIFile('MIDI File'))
    .add(screens.MIDIInput('MIDI Input'))
    .add(screens.ARSG('ARSG Emulator'))
    .add(screens.BatteryStatus('Battery Status'))
    .add(SubMenuItem('Configure')
        .add(screens.InterrupterConfig('Interrupter Config'))
        .add(screens.MIDIFileConfig('MIDI File Config'))
        .add(screens.ARSGConfig('ARSG Config'))
        .add(screens.RestoreDefaults('Restore Defaults'))
    )
)

init.menu.draw()

"""
Asyncio Loop

This starts the loop for handling asynchronous tasks, such as; long file/track
name scrolling, input monitoring and RGB LED updates.
"""
import mptcc.lib.asyncio
init.asyncio_loop.start_loop()
