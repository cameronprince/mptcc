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
Hardware Settings
"""
# I2C bus 1 pin assignments and settings.
# (used by the default SSD1306 display.)
init.PIN_I2C_1_SCL = 17
init.PIN_I2C_1_SDA = 16
init.I2C_1_INTERFACE = 0
init.I2C_1_FREQ = 400000

# I2C bus 2 pin assignments and settings.
# (used by the default PCA9685 RGB LED hardware)
init.PIN_I2C_2_SCL = 19
init.PIN_I2C_2_SDA = 18
init.I2C_2_INTERFACE = 1
init.I2C_2_FREQ = 400000

# SPI bus 1 pin assignments and settings.
# (used by SD card reader)
init.SPI_1_INTERFACE = 0
init.SPI_1_BAUD = 1000000
init.PIN_SPI_1_SCK = 2
init.PIN_SPI_1_MOSI = 3
init.PIN_SPI_1_MISO = 4
init.PIN_SPI_1_CS = 1
init.PIN_SPI_1_DC = 4
init.PIN_SPI_1_RST = 16

# SPI bus 2 pin assignments and settings.
# (optionally used by a display)
# init.SPI_2_INTERFACE = 1
# init.SPI_2_BAUD = 1000000
# init.PIN_SPI_2_SCK = 0
# init.PIN_SPI_2_MOSI = 0
# init.PIN_SPI_2_MISO = 0
# init.PIN_SPI_2_CS = 0
# init.PIN_SPI_2_DC = 0
# init.PIN_SPI_2_RST = 0

# Output pin assignments.
init.PIN_OUTPUT_1 = 22
init.PIN_OUTPUT_2 = 6
init.PIN_OUTPUT_3 = 7
init.PIN_OUTPUT_4 = 8

# Battery status ADC pin assignment and settings.
init.PIN_BATT_STATUS_ADC = 28
# Adjust for specific supply voltage used.
init.VOLTAGE_DROP_FACTOR = 5 # Default value for 5V supply.

# MIDI input pin assignment and UART settings.
init.PIN_MIDI_INPUT = 13
init.UART_INTERFACE = 0
init.UART_BAUD = 31250

# Miscellaneous definitions.
init.SD_MOUNT_POINT = "/sd"
init.CONFIG_PATH = "/mptcc/config.json"

# Frequencies listed here are filtered from the available choices for the interrupter function.
init.BANNED_INTERRUPTER_FREQUENCIES = []

# Rotary encoder pin assignments.
init.PIN_ROTARY_1_CLK = 11
init.PIN_ROTARY_1_DT = 10
init.PIN_ROTARY_1_SW = 12

init.PIN_ROTARY_2_CLK = 14
init.PIN_ROTARY_2_DT = 9
init.PIN_ROTARY_2_SW = 15

init.PIN_ROTARY_3_CLK = 26
init.PIN_ROTARY_3_DT = 27
init.PIN_ROTARY_3_SW = 0

init.PIN_ROTARY_4_CLK = 20
init.PIN_ROTARY_4_DT = 21
init.PIN_ROTARY_4_SW = 5

# Enable/disable encoder pin pull-up resistors.
# Most of the PCB-mounted encoders have pull-ups on the boards.
init.ROTARY_PULL_UP = False

"""
Display

Select one of the display options below by commenting out the default option
and removing the comment for the desired, alternate option.

The display needs to be initialized first as it needs a large block of
contiguous memory.

Edit the class for the selected hardware to define configuration.
"""
# SSD1306 0.96" 128X64 OLED LCD Display (https://amzn.to/40sf11I)
# Interface: I2C/SPI
# Requires: https://github.com/TimHanewich/MicroPython-SSD1306
# Note: This library only supports standard frame buffer commands.
# To use with SPI, include an 'spi' argument when instantiating the
# display object as: init.display = display('spi').
from mptcc.hardware.display.ssd1306 import SSD1306 as display  # Default option.

# SSD1309 2.42" 128x64 OLED LCD Display (https://amzn.to/40wQWbs)
# Interface: I2C/SPI
# Requires: https://github.com/rdagger/micropython-ssd1309
# Note: This library supports custom fonts, shapes, images, and more, beyond
# the standard frame buffer commands. This driver also works with SSD1306 displays.
# To use with SPI, include an 'spi' argument when instantiating the
# display object as: init.display = display('spi').
# from mptcc.hardware.display.ssd1309 import SSD1309 as display  # Alternate option.

# SSD1322 3.12" 256x64 OLED LCD Display (https://amzn.to/4jupi6c)
# Interface: SPI
# Requires: https://github.com/rdagger/micropython-ssd1322
# Note: This library supports custom fonts, shapes, images, and more, beyond
# the standard frame buffer commands.
# To use with SPI, include an 'spi' argument when instantiating the
# display object as: init.display = display('spi').
# from mptcc.hardware.display.ssd1322 import SSD1322 as display  # Alternate option.

init.display = display()

"""
Input Devices

Select one of the input device options below by commenting out the default option
and removing the comment for the desired, alternate option.

Edit the class for the selected hardware to define configuration.
"""
# KY-040 Rotary Encoder - https://amzn.to/42E63l1 or https://amzn.to/3CdzIqi
# Requires: https://github.com/miketeachman/micropython-rotary
from mptcc.hardware.input.ky_040 import KY040 as inputs  # Default option.

# I2CEncoder V2.1 - https://github.com/Fattoresaimon/I2CEncoderV2.1
# Requires: https://github.com/cameronprince/i2cEncoderLibV2
# from mptcc.hardware.input.i2cencoder import I2CEncoderInput as inputs  # Alternate option.

init.inputs = inputs()

"""
RGB LEDs

Select one of the RGB LED options below by commenting out the default option
and removing the comment for the desired, alternate option.

Edit the class for the selected hardware to define configuration.
"""
# PCA9685 16-channel 12-bit PWM - https://amzn.to/4jf2E1J
# Requires: https://github.com/kevinmcaleer/pca9685_for_pico
from mptcc.hardware.rgb_led.pca9685 import PCA9685 as rgb_led  # Default option.

# I2CEncoder V2.1 - https://github.com/Fattoresaimon/I2CEncoderV2.1
# Requires: https://github.com/cameronprince/i2cEncoderLibV2
# from mptcc.hardware.rgb_led.i2cencoder import I2CEncoder as rgb_led  # Alternate option.

init.rgb_driver = rgb_led()

"""
Outputs

Select one of the output options below by commenting out the default option
and removing the comment for the desired, alternate option.
"""
# GPIO pin outputs with hardware PWM.
from mptcc.hardware.output.gpio_pwm import GPIO_PWM as output # Default option.

# GPIO pin outputs with Programmable Input Output (PIO).
# from mptcc.hardware.output.gpio_pio import GPIO_PIO as output # Alternate option.

init.output = output()

"""
SD Card Reader
"""
from mptcc.hardware.sd_card_reader import SDCardReader as sd_card_reader
init.sd_card_reader = sd_card_reader()

"""
Menu Definition
"""
from mptcc.lib.menu import Menu, MenuScreen, SubMenuItem, CustomItem
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
    .add(screens.BatteryStatus('Battery Status'))
    .add(SubMenuItem('Configure')
        .add(screens.InterrupterConfig('Interrupter'))
        .add(screens.MIDIFileConfig('MIDI File'))
        .add(screens.RestoreDefaults('Restore Defaults'))
    )
)

init.menu.draw()
