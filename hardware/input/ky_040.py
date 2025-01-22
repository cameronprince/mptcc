"""
MicroPython Tesla Coil Controller (MPTCC)
by Cameron Prince
teslauniverse.com

hardware/input/ky_040.py
Input module for standard KY-040 rotary encoders.
"""

import time
from machine import Pin
from rotary_irq_rp2 import RotaryIRQ
from ...hardware.init import init
from ..input.input import Input
from ...lib.menu import CustomItem

class KY040(Input):
    """
    A class to handle input from standard KY-040 rotary encoders for the 
    MicroPython Tesla Coil Controller (MPTCC).

    Attributes:
    -----------
    init : object
        The initialization object containing configuration and hardware settings.
    rotary_encoders : list
        List of RotaryIRQ objects for the rotary encoders.
    last_rotations : list
        List of the last rotation values for each encoder.
    """

    def __init__(self):
        """
        Constructs all the necessary attributes for the KY040 object.
        """
        super().__init__()

        self.init = init

        # Define rotary interrupts.
        self.rotary_encoders = [
            RotaryIRQ(pin_num_clk=init.PIN_ROTARY_1_CLK, pin_num_dt=init.PIN_ROTARY_1_DT,
                      min_val=0, max_val=10, reverse=False, range_mode=RotaryIRQ.RANGE_UNBOUNDED,
                      pull_up=init.ROTARY_PULL_UP, half_step=False),
            RotaryIRQ(pin_num_clk=init.PIN_ROTARY_2_CLK, pin_num_dt=init.PIN_ROTARY_2_DT,
                      min_val=0, max_val=10, reverse=False, range_mode=RotaryIRQ.RANGE_UNBOUNDED,
                      pull_up=init.ROTARY_PULL_UP, half_step=False),
            RotaryIRQ(pin_num_clk=init.PIN_ROTARY_3_CLK, pin_num_dt=init.PIN_ROTARY_3_DT,
                      min_val=0, max_val=10, reverse=False, range_mode=RotaryIRQ.RANGE_UNBOUNDED,
                      pull_up=init.ROTARY_PULL_UP, half_step=False),
            RotaryIRQ(pin_num_clk=init.PIN_ROTARY_4_CLK, pin_num_dt=init.PIN_ROTARY_4_DT,
                      min_val=0, max_val=10, reverse=False, range_mode=RotaryIRQ.RANGE_UNBOUNDED,
                      pull_up=init.ROTARY_PULL_UP, half_step=False),
        ]
        self.last_rotations = [encoder.value() for encoder in self.rotary_encoders]

        # Add the listeners which file the rotary_encoder_change callback.
        for encoder in self.rotary_encoders:
            encoder.add_listener(self.rotary_encoder_change)

        # Define the switches.
        # Note: These definitions go to init so that switches may be accessed
        # directly for screens such as "Restore Defaults" where two switches
        # trigger an action.
        self.init.switch_1 = Pin(init.PIN_ROTARY_1_SW, Pin.IN, Pin.PULL_UP)
        self.init.switch_2 = Pin(init.PIN_ROTARY_2_SW, Pin.IN, Pin.PULL_UP)
        self.init.switch_3 = Pin(init.PIN_ROTARY_3_SW, Pin.IN, Pin.PULL_UP)
        self.init.switch_4 = Pin(init.PIN_ROTARY_4_SW, Pin.IN, Pin.PULL_UP)

        # Set up the switch interrupts.
        self.init.switch_1.irq(self.switch_click, Pin.IRQ_FALLING)
        self.init.switch_2.irq(self.switch_click, Pin.IRQ_FALLING)
        self.init.switch_3.irq(self.switch_click, Pin.IRQ_FALLING)
        self.init.switch_4.irq(self.switch_click, Pin.IRQ_FALLING)

    def switch_click(self, pin):
        """
        The primary switch callback function.

        Parameters:
        ----------
        pin : machine.Pin
            The pin object for the switch.
        """
        time.sleep_ms(50)
        if pin.value() == 0:
            current_screen = self.init.menu.get_current_screen()
            if isinstance(current_screen, CustomItem):
                switch_dict = {
                    self.init.switch_1: 'switch_1',
                    self.init.switch_2: 'switch_2',
                    self.init.switch_3: 'switch_3',
                    self.init.switch_4: 'switch_4'
                }
                if pin in switch_dict:
                    method_name = switch_dict[pin]
                    if hasattr(current_screen, method_name):
                        getattr(current_screen, method_name)()
            else:
                if pin == self.init.switch_1:
                    self.init.menu.click()
                elif pin == self.init.switch_2:
                    parent_screen = self.init.menu.current_screen.parent
                    if parent_screen:
                        self.init.menu.set_screen(parent_screen)
                        self.init.menu.draw()

    def rotary_encoder_change(self):
        """
        The primary rotary encoder callback function.
        """
        for idx, encoder in enumerate(self.rotary_encoders):
            new_value = encoder.value()
            if self.last_rotations[idx] != new_value:
                current_screen = self.init.menu.get_current_screen()
                method_name = f'rotary_{idx + 1}'
                if isinstance(current_screen, CustomItem) and hasattr(current_screen, method_name):
                    getattr(current_screen, method_name)(new_value)
                elif idx == 0:
                    self.init.menu.move(-1 if self.last_rotations[idx] > new_value else 1)
                self.last_rotations[idx] = new_value
                time.sleep_ms(50)
