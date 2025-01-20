"""
MicroPython Tesla Coil Controller (MPTCC)
by Cameron Prince
teslauniverse.com

main.py
The primary purpose of this file is to define the menu object
and set up the interrupts and callbacks for the inputs.
The modules in the screens subdirectory provide the functionality.
"""

from mptcc.init import init
from mptcc.lib.menu import Menu, MenuScreen, SubMenuItem, CustomItem
import mptcc.screens as screens

from mptcc.hardware.input import ky_040
inputs = ky_040.KY040(init)

# Define and display the menu.
init.menu = Menu(
    init.display,
    init.DISPLAY_ITEMS_PER_PAGE,
    init.DISPLAY_LINE_HEIGHT,
    init.DISPLAY_FONT_WIDTH,
    init.DISPLAY_FONT_HEIGHT
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

