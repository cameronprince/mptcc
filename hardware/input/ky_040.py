"""
MicroPython Tesla Coil Controller (MPTCC)
by Cameron Prince
teslauniverse.com

hardware/input/ky_040.py
Input module for standard KY-040 rotary encoders.
"""

import time
from machine import Pin
import uasyncio as asyncio
from rotary_irq_rp2 import RotaryIRQ
from ...hardware.init import init
from ..input.input import Input
from ...lib.menu import Screen

class KY040(Input):
    def __init__(self):
        super().__init__()

        self.init = init
        self.last_switch_click_time = [0] * self.init.NUMBER_OF_COILS

        # Dynamically populate rotary_pins based on NUMBER_OF_COILS.
        rotary_pins = []
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

            rotary_pins.append((
                getattr(self.init, clk_pin_attr),
                getattr(self.init, dt_pin_attr),
                getattr(self.init, sw_pin_attr),
            ))

        # Initialize rotary encoders and switches dynamically.
        self.rotary_encoders = []
        self.last_rotations = []
        self.active_interrupt = None  # Use None to indicate no active interrupt

        for i in range(self.init.NUMBER_OF_COILS):
            clk_pin = rotary_pins[i][0]
            dt_pin = rotary_pins[i][1]
            sw_pin = rotary_pins[i][2]

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
            self.rotary_encoders.append(encoder)
            self.last_rotations.append(encoder.value())

            # Add listener for rotary encoder.
            encoder.add_listener(self.create_listener(i))

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
            print(f"KY-040 rotary encoder {i + 1} initialized: CLK={clk_pin}, DT={dt_pin}, SW={sw_pin}, pull_up={init.ROTARY_PULL_UP}")

        # Start the asyncio task to process interrupts.
        asyncio.create_task(self.process_interrupt())

    def create_listener(self, idx):
        def listener():
            # Set the active_interrupt to the index of the encoder that triggered the interrupt
            self.active_interrupt = idx
        return listener

    async def process_interrupt(self):
        """
        Asyncio task to process rotary encoder changes.
        This method processes the encoder change indicated by self.active_interrupt.
        """
        while True:
            if self.active_interrupt is not None:
                idx = self.active_interrupt  # Get the index of the encoder that triggered the interrupt
                self.active_interrupt = None  # Reset the active interrupt

                encoder = self.rotary_encoders[idx]
                new_value = encoder.value()

                if new_value is None:
                    continue  # Skip if the value is invalid

                if self.last_rotations[idx] != new_value:
                    # Determine the direction of rotation
                    if self.last_rotations[idx] == 0 and new_value == 100:
                        direction = -1  # Wrapped around from 0 to 100 (counter-clockwise)
                    elif self.last_rotations[idx] == 100 and new_value == 0:
                        direction = 1  # Wrapped around from 100 to 0 (clockwise)
                    else:
                        direction = 1 if new_value > self.last_rotations[idx] else -1

                    # Update the last rotation value
                    self.last_rotations[idx] = new_value

                    # Call the rotary encoder change handler
                    super().rotary_encoder_change(idx, direction)

            # Sleep briefly to avoid busy-waiting
            await asyncio.sleep(0.01)

    def switch_click(self, switch):
        current_time = time.ticks_ms()
        if time.ticks_diff(current_time, self.last_switch_click_time[switch - 1]) > 500:
            self.last_switch_click_time[switch - 1] = current_time
            super().switch_click(switch)
