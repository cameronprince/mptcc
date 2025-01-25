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
        self.last_switch_click_time = [0] * 4  # Store the last click time for each switch

        self.rotary_encoders = [
            RotaryIRQ(pin_num_clk=init.PIN_ROTARY_1_CLK, pin_num_dt=init.PIN_ROTARY_1_DT,
                      min_val=-50, max_val=50, reverse=False, range_mode=RotaryIRQ.RANGE_WRAP,
                      pull_up=init.ROTARY_PULL_UP, half_step=False),
            RotaryIRQ(pin_num_clk=init.PIN_ROTARY_2_CLK, pin_num_dt=init.PIN_ROTARY_2_DT,
                      min_val=-50, max_val=50, reverse=False, range_mode=RotaryIRQ.RANGE_WRAP,
                      pull_up=init.ROTARY_PULL_UP, half_step=False),
            RotaryIRQ(pin_num_clk=init.PIN_ROTARY_3_CLK, pin_num_dt=init.PIN_ROTARY_3_DT,
                      min_val=-50, max_val=50, reverse=False, range_mode=RotaryIRQ.RANGE_WRAP,
                      pull_up=init.ROTARY_PULL_UP, half_step=False),
            RotaryIRQ(pin_num_clk=init.PIN_ROTARY_4_CLK, pin_num_dt=init.PIN_ROTARY_4_DT,
                      min_val=-50, max_val=50, reverse=False, range_mode=RotaryIRQ.RANGE_WRAP,
                      pull_up=init.ROTARY_PULL_UP, half_step=False),
        ]
        self.last_rotations = [encoder.value() for encoder in self.rotary_encoders]

        for idx, encoder in enumerate(self.rotary_encoders):
            encoder.add_listener(self.create_listener(idx))

        self.init.switch_1 = Pin(init.PIN_ROTARY_1_SW, Pin.IN, Pin.PULL_UP)
        self.init.switch_2 = Pin(init.PIN_ROTARY_2_SW, Pin.IN, Pin.PULL_UP)
        self.init.switch_3 = Pin(init.PIN_ROTARY_3_SW, Pin.IN, Pin.PULL_UP)
        self.init.switch_4 = Pin(init.PIN_ROTARY_4_SW, Pin.IN, Pin.PULL_UP)

        self.init.switch_1.irq(lambda pin: self.switch_click(1), Pin.IRQ_FALLING)
        self.init.switch_2.irq(lambda pin: self.switch_click(2), Pin.IRQ_FALLING)
        self.init.switch_3.irq(lambda pin: self.switch_click(3), Pin.IRQ_FALLING)
        self.init.switch_4.irq(lambda pin: self.switch_click(4), Pin.IRQ_FALLING)

    def create_listener(self, idx):
        """
        Create a listener function that captures the index.
        
        Parameters:
        ----------
        idx : int
            The index of the encoder.

        Returns:
        -------
        function
            A listener function that captures the index.
        """
        def listener():
            new_value = self.rotary_encoders[idx].value()
            self.rotary_encoder_change(idx, new_value)
        return listener

    def rotary_encoder_change(self, idx, new_value):
        """
        The primary rotary encoder callback function with debugging.

        Parameters:
        ----------
        idx : int
            Index of the encoder.
        new_value : int
            The new value of the encoder.
        """
        encoder = self.rotary_encoders[idx]
        print(f'rotary_encoder_change called for encoder {idx + 1} with new value: {new_value}')
        if self.last_rotations[idx] != new_value:
            current_screen = self.init.menu.get_current_screen()
            method_name = f'rotary_{idx + 1}'
            print(f'Calling method {method_name} for current screen.')
            if isinstance(current_screen, CustomItem) and hasattr(current_screen, method_name):
                getattr(current_screen, method_name)(new_value)
            elif idx == 0:
                self.init.menu.move(-1 if self.last_rotations[idx] > new_value else 1)
            self.last_rotations[idx] = new_value
            time.sleep_ms(50)

    def switch_click(self, switch):
        """
        The primary switch callback function with debouncing.

        Parameters:
        ----------
        switch : int
            The switch number (1 to 4).
        """
        current_time = time.ticks_ms()
        if time.ticks_diff(current_time, self.last_switch_click_time[switch - 1]) > 200:
            # Call the parent class's switch_click method
            super().switch_click(switch)
            self.last_switch_click_time[switch - 1] = current_time
