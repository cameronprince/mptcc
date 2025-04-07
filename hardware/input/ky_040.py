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


class KY040(Input):
    def __init__(self, pins, pull_up=False):
        """
        Initialize the KY-040 rotary encoder driver.

        Args:
            pins (list): A list of lists, where each inner list contains the CLK, DT, and SW pin numbers.
            pull_up (bool): Whether to enable pull-up resistors for the encoder pins.
        """
        super().__init__()

        self.pins = pins
        self.pull_up = pull_up
        self.last_switch_click_time = [0] * len(pins)

        # Initialize rotary encoders and switches.
        self.instances = []
        self.last_rotations = []
        self.encoder_interrupt = None
        self.switch_interrupt = None

        for i, (clk_pin, dt_pin, sw_pin) in enumerate(pins):
            # Initialize rotary encoder.
            encoder = RotaryIRQ(
                pin_num_clk=clk_pin,
                pin_num_dt=dt_pin,
                min_val=0,
                max_val=100,
                reverse=False,
                range_mode=RotaryIRQ.RANGE_WRAP,
                pull_up=self.pull_up,
                half_step=False,
            )
            self.instances.append(encoder)
            self.last_rotations.append(encoder.value())

            # Add listener for rotary encoder.
            encoder.add_listener(self.create_listener(i))

            # Initialize switch if SW pin is provided.
            if sw_pin is not None:
                switch_pin = Pin(sw_pin, Pin.IN, Pin.PULL_UP if self.pull_up else Pin.IN)
                switch_pin.irq(self.create_switch_callback(i), Pin.IRQ_FALLING)

        instance_key = len(self.init.input_instances["encoder"]["ky_040"])

        # Print initialization details.
        print(f"KY-040 driver {instance_key} initialized with {len(self.pins)} encoders (pull_up={self.pull_up}):")
        for i, (clk_pin, dt_pin, sw_pin) in enumerate(self.pins):
            print(f"- Encoder {i + 1}: CLK={clk_pin}, DT={dt_pin}, SW={sw_pin}")

        # Start the asyncio task to process interrupts.
        asyncio.create_task(self.encoder_interrupt_handler())
        asyncio.create_task(self.switch_interrupt_handler())

    def create_listener(self, idx):
        """
        Create a listener callback for the rotary encoder.

        Args:
            idx (int): The index of the encoder.

        Returns:
            function: The listener callback.
        """
        def listener():
            # Set the encoder_interrupt to the index of the encoder that triggered the interrupt.
            self.encoder_interrupt = idx
        return listener

    def create_switch_callback(self, idx):
        """
        Create a switch callback for the rotary encoder switch.

        Args:
            idx (int): The index of the encoder.

        Returns:
            function: The switch callback.
        """
        def callback(pin):
            current_time = time.ticks_ms()
            if time.ticks_diff(current_time, self.last_switch_click_time[idx]) > 300:
                self.last_switch_click_time[idx] = current_time
                self.switch_interrupt = idx
        return callback

    async def encoder_interrupt_handler(self):
        """
        Asyncio task to process rotary encoder changes.
        """
        while True:
            if self.encoder_interrupt is not None:
                idx = self.encoder_interrupt
                self.encoder_interrupt = None

                encoder = self.instances[idx]
                new_value = encoder.value()

                if new_value is None:
                    continue

                if self.last_rotations[idx] != new_value:
                    if self.last_rotations[idx] == 0 and new_value == 100:
                        direction = -1
                    elif self.last_rotations[idx] == 100 and new_value == 0:
                        direction = 1
                    else:
                        direction = 1 if new_value > self.last_rotations[idx] else -1

                    self.last_rotations[idx] = new_value
                    super().encoder_change(idx, direction)

            await asyncio.sleep(0.01)

    async def switch_interrupt_handler(self):
        """
        Asyncio task to process switch clicks.
        """
        while True:
            if self.switch_interrupt is not None:
                idx = self.switch_interrupt
                self.switch_interrupt = None
                super().switch_click(idx + 1)
            await asyncio.sleep(0.01)
