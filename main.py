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
from machine import Pin
from rotary_irq_rp2 import RotaryIRQ
import time

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

def switch_click(pin):
    """
    Callback for switch clicks.
    Either passes the click off to a corresponding method in a CustomItem
    class (screen) or provides interaction with the menu.

    Parameters:
    ----------
    pin : machine.Pin
        The pin object that triggered the interrupt.
    """
    if pin.value() == 0:
        current_screen = init.menu.get_current_screen()
        if isinstance(current_screen, CustomItem):
            for i, encoder in enumerate(init.encoders):
                if pin == eval(f"init.switch_{i + 1}"):
                    method_name = f"switch_{i + 1}"
                    if hasattr(current_screen, method_name):
                        getattr(current_screen, method_name)()
                    break
        else:
            if pin == init.switch_1:
                init.menu.click()
            elif pin == init.switch_2:
                parent_screen = init.menu.current_screen.parent
                if parent_screen:
                    init.menu.set_screen(parent_screen)
                    init.menu.draw()

# Set up interrupts for the switches.
init.switch_1.irq(switch_click, Pin.IRQ_FALLING)
init.switch_2.irq(switch_click, Pin.IRQ_FALLING)
init.switch_3.irq(switch_click, Pin.IRQ_FALLING)
init.switch_4.irq(switch_click, Pin.IRQ_FALLING)

# Set up rotary encoders.
rotary_encoders = [
    RotaryIRQ(pin_num_clk=init.encoders[0]['clk'], pin_num_dt=init.encoders[0]['dt'],
              min_val=0, max_val=10, reverse=False, range_mode=RotaryIRQ.RANGE_UNBOUNDED,
              pull_up=True, half_step=False),
    RotaryIRQ(pin_num_clk=init.encoders[1]['clk'], pin_num_dt=init.encoders[1]['dt'],
              min_val=0, max_val=10, reverse=False, range_mode=RotaryIRQ.RANGE_UNBOUNDED,
              pull_up=True, half_step=False),
    RotaryIRQ(pin_num_clk=init.encoders[2]['clk'], pin_num_dt=init.encoders[2]['dt'],
              min_val=0, max_val=10, reverse=False, range_mode=RotaryIRQ.RANGE_UNBOUNDED,
              pull_up=True, half_step=False),
    RotaryIRQ(pin_num_clk=init.encoders[3]['clk'], pin_num_dt=init.encoders[3]['dt'],
              min_val=0, max_val=10, reverse=False, range_mode=RotaryIRQ.RANGE_UNBOUNDED,
              pull_up=True, half_step=False),
]

last_rotations = [encoder.value() for encoder in rotary_encoders]

def rotary_encoder_change():
    """
    Callback for encoder rotation.
    Either passes the rotation off to a corresponding method in a CustomItem
    class (screen) or provides interaction with the menu.
    """
    for idx, encoder in enumerate(rotary_encoders):
        new_value = encoder.value()
        if last_rotations[idx] != new_value:
            current_screen = init.menu.get_current_screen()
            method_name = f'rotary_{idx + 1}'
            if isinstance(current_screen, CustomItem) and hasattr(current_screen, method_name):
                getattr(current_screen, method_name)(new_value)
            elif idx == 0:
                init.menu.move(-1 if last_rotations[idx] > new_value else 1)
            last_rotations[idx] = new_value

# Define the listeners which fire the callback.
for encoder in rotary_encoders:
    encoder.add_listener(rotary_encoder_change)