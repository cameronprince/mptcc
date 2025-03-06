"""
MicroPython Tesla Coil Controller (MPTCC)
by Cameron Prince
teslauniverse.com

hardware/input/switch.py
Generic switch input driver.
"""

import time
from machine import Pin
from ...hardware.init import init
from ..input.input import Input
from ...lib.menu import Screen

class Switch(Input):
    def __init__(self):
        super().__init__()

        self.init = init
        self.last_switch_click_time = [0] * self.init.NUMBER_OF_COILS

        # Dynamically populate rotary_pins based on NUMBER_OF_COILS.
        pins = []
        for i in range(1, self.init.NUMBER_OF_COILS + 1):
            clk_pin_attr = f"PIN_ROTARY_{i}_CLK"
            dt_pin_attr = f"PIN_ROTARY_{i}_DT"
            sw_pin_attr = f"PIN_ROTARY_{i}_SW"

            if not hasattr(self.init, clk_pin_attr) or \
               not hasattr(self.init, dt_pin_attr) or \
               not hasattr(self.init, sw_pin_attr):
                raise ValueError(
                    f"Rotary encoder configuration for KY-040 input {i} is missing. "
                    f"Please ensure {clk_pin_attr}, {dt_pin_attr}, and {sw_pin_attr} are defined in main."
                )

            pins.append((
                getattr(self.init, clk_pin_attr),
                getattr(self.init, dt_pin_attr),
                getattr(self.init, sw_pin_attr),
            ))

        # Initialize rotary encoders and switches dynamically.
        self.encoders = []
        self.last_rotations = []
        self.active_interrupt = None

        for i in range(self.init.NUMBER_OF_COILS):
            clk_pin = pins[i][0]
            dt_pin = pins[i][1]
            sw_pin = pins[i][2]

            # Initialize rotary encoder.
            encoder = RotaryIRQ(
                pin_num_clk=clk_pin,
                pin_num_dt=dt_pin,
                min_val=0,
                max_val=100,
                reverse=False,
                range_mode=RotaryIRQ.RANGE_WRAP,
                pull_up=init.ROTARY_PULL_UP,
                half_step=False,
            )
            self.encoders.append(encoder)
            self.last_rotations.append(encoder.value())

            # Add listener for rotary encoder.
            encoder.add_listener(self.create_listener(i))

            if self.init.integrated_switches:
                # Initialize switch.
                # Conditionally enable pull-up based on init.ROTARY_PULL_UP.
                if init.ROTARY_PULL_UP:
                    switch_pin = Pin(sw_pin, Pin.IN, Pin.PULL_UP)
                else:
                    switch_pin = Pin(sw_pin, Pin.IN)

                # Attach interrupt to the switch pin.
                def create_switch_callback(idx):
                    return lambda pin: self.switch_click(idx + 1)

                switch_pin.irq(create_switch_callback(i), Pin.IRQ_FALLING)
                setattr(self.init, f"switch_{i + 1}", switch_pin)

            print(f"Generic switch {i + 1} initialized: pin={sw_pin}, pull_up={init.SWITCH_PULL_UP}")

    def switch_click(self, switch):
        current_time = time.ticks_ms()
        if time.ticks_diff(current_time, self.last_switch_click_time[switch - 1]) > 500:
            self.last_switch_click_time[switch - 1] = current_time
            super().switch_click(switch)
