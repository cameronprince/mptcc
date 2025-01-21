"""
MicroPython Tesla Coil Controller (MPTCC)
by Cameron Prince
teslauniverse.com

main.py
Define and initialize the hardware, set up the menu object.
"""

from mptcc.init import init
from mptcc.lib.menu import Menu, MenuScreen, SubMenuItem, CustomItem
import mptcc.screens as screens

"""
Input Devices

Select one of the input device options below by commenting out the default option
and removing the comment for the desired alternate option.

Edit the class for the selected hardware to define configuration.
"""

# KY-040 Rotary Encoder - https://amzn.to/42E63l1 or https://amzn.to/3CdzIqi
# Requires: https://github.com/miketeachman/micropython-rotary
# --------
from mptcc.hardware.input.ky_040 import KY040 as inputs # Default option.

# I2CEncoder V2.1 - https://www.tindie.com/products/saimon/i2cencoder-v21-connect-rotary-encoder-on-i2c-bus
# Requires: https://github.com/cameronprince/i2cEncoderLibV2
# --------
# from mptcc.hardware.input.i2cencoder import I2CEncoderInput as inputs # Alternate option.

init.inputs = inputs()

"""
Display

Select one of the display options below by commenting out the default option
and removing the comment for the desired alternate option.

Edit the class for the selected hardware to define configuration.
"""
# SSD1309 2.42" 128x64 OLED LCD Display (https://amzn.to/40wQWbs)
# Requires: https://github.com/rdagger/micropython-ssd1309
# Note: This library supports custom fonts, shapes, images and more, beyond
# the standard frame buffer commands.
# --------
from mptcc.hardware.display.ssd1309 import SSD1309 as display # Default option.

# SSD1306 0.96" 128X64 OLED LCD Display (https://amzn.to/40sf11I)
# Requires: https://github.com/TimHanewich/MicroPython-SSD1306
# Note: This library only supports standard frame buffer commands.
# --------
# from mptcc.hardware.display.ssd1306 import SSD1306 as display # Alternate option.

init.display = display()

"""
RGB LEDs

Select one of the RGB LED options below by commenting out the default option
and removing the comment for the desired alternate option.

Edit the class for the selected hardware to define configuration.
"""
# PCA9685 16-channel 12-bit PWM - https://amzn.to/4jf2E1J
# Requires: https://github.com/kevinmcaleer/pca9685_for_pico
# --------
from mptcc.hardware.rgb_led.pca9685 import PCA9685 as rgb_led # Default option.

# I2CEncoder V2.1 - https://www.tindie.com/products/saimon/i2cencoder-v21-connect-rotary-encoder-on-i2c-bus
# Requires: https://github.com/cameronprince/i2cEncoderLibV2
# --------
# from mptcc.hardware.rgb_led.i2cencoder import I2CEncoderInput as rgb_leds # Alternate option.

init.rgb_driver = rgb_led()

"""
Outputs
"""
from mptcc.hardware.output import Output as output
init.output = output()

"""
SD Card Reader
"""
from mptcc.hardware.sd_card_reader import SDCardReader as sd_card_reader
init.sd_card_reader = sd_card_reader()

"""
Menu
"""
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
        .add(screens.RestoreDefaults('Restore Defaults'))
    )
)
init.menu.draw()

