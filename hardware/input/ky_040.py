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
    def __init__(self):
        super().__init__()

        self.init = init
        self.last_switch_click_time = [0] * 4

        self.rotary_encoders = [
            RotaryIRQ(pin_num_clk=init.PIN_ROTARY_1_CLK, pin_num_dt=init.PIN_ROTARY_1_DT,
                      min_val=0, max_val=100, reverse=False, range_mode=RotaryIRQ.RANGE_WRAP,
                      pull_up=init.ROTARY_PULL_UP, half_step=False),
            RotaryIRQ(pin_num_clk=init.PIN_ROTARY_2_CLK, pin_num_dt=init.PIN_ROTARY_2_DT,
                      min_val=0, max_val=100, reverse=False, range_mode=RotaryIRQ.RANGE_WRAP,
                      pull_up=init.ROTARY_PULL_UP, half_step=False),
            RotaryIRQ(pin_num_clk=init.PIN_ROTARY_3_CLK, pin_num_dt=init.PIN_ROTARY_3_DT,
                      min_val=0, max_val=100, reverse=False, range_mode=RotaryIRQ.RANGE_WRAP,
                      pull_up=init.ROTARY_PULL_UP, half_step=False),
            RotaryIRQ(pin_num_clk=init.PIN_ROTARY_4_CLK, pin_num_dt=init.PIN_ROTARY_4_DT,
                      min_val=0, max_val=100, reverse=False, range_mode=RotaryIRQ.RANGE_WRAP,
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
        def listener():
            new_value = self.rotary_encoders[idx].value()

        if direction is None:
            if new_value is None:
                return
            if self.last_rotations[idx] != new_value:
                # Handle wrap-around cases.
                if self.last_rotations[idx] == 0 and new_value == 100:
                    direction = -1
                elif self.last_rotations[idx] == 100 and new_value == 0:
                    direction = 1
                else:
                    direction = 1 if new_value > self.last_rotations[idx] else -1
            else:
                return


        if new_value is not None:
            self.last_rotations[idx] = new_value



            self.rotary_encoder_change(idx, new_value)
        return listener

    def switch_click(self, switch):
        current_time = time.ticks_ms()
        if time.ticks_diff(current_time, self.last_switch_click_time[switch - 1]) > 1000:
            self.last_switch_click_time[switch - 1] = current_time
            super().switch_click(switch)