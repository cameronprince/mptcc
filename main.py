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

init.inputs = inputs(init)


"""
Display

Select one of the display options below by commenting out the default option.

Edit the class for the selected hardware to define configuration options.
"""
# SSD1309 2.42" 128x64 OLED LCD Display (https://amzn.to/40DiImt)
# Requires: https://github.com/rdagger/micropython-ssd1309/blob/master/ssd1309.py
from mptcc.hardware.display.ssd1309 import SSD1309 as display

init.display = display(init)

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
