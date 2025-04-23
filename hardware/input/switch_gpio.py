"""
MicroPython Tesla Coil Controller (MPTCC)
by Cameron Prince
teslauniverse.com

hardware/input/switch_gpio.py
GPIO switch input driver.
"""

import time
from machine import Pin
import uasyncio as asyncio
from ...hardware.init import init
from ..input.input import Input
from ...lib.menu import Screen


class Switch_GPIO(Input):
    def __init__(self, config):
        """Initialize the GPIO switch driver."""
        super().__init__()

        self.pins = config.get("pins", [])
        self.pull_up = config.get("pull_up", False)
        self.last_switch_click_time = [0] * len(self.pins)  # Track last click time for debouncing.
        self.debounce_delay = 150  # Debounce delay in milliseconds.
        self.switch_interrupt = None  # Track which switch triggered an interrupt.
        self.instances = []

        # Initialize GPIO pins for switches.
        self.switch_pins = []
        for i, pin in enumerate(self.pins):
            switch_pin = Pin(pin, Pin.IN, Pin.PULL_UP if self.pull_up else Pin.PULL_DOWN)
            switch_pin.irq(handler=self.create_switch_callback(i), trigger=Pin.IRQ_FALLING)
            self.instances.append(switch_pin)

        # Print initialization details.
        print(f"GPIO switch driver initialized with {len(self.pins)} switches (pull_up={self.pull_up}):")
        for i, pin in enumerate(self.pins):
            print(f"- Switch {i + 1}: GPIO={pin}")

        # Start the asyncio task to process switch interrupts.
        asyncio.create_task(self.switch_interrupt_handler())

    def create_switch_callback(self, idx):
        """
        Create a switch callback for the GPIO switch.

        Args:
            idx (int): The index of the switch.

        Returns:
            function: The switch callback.
        """
        def callback(pin):
            current_time = time.ticks_ms()
            if time.ticks_diff(current_time, self.last_switch_click_time[idx]) > self.debounce_delay:
                self.last_switch_click_time[idx] = current_time
                self.switch_interrupt = idx
        return callback

    async def switch_interrupt_handler(self):
        """
        Asyncio task to process switch clicks.
        """
        while True:
            if self.switch_interrupt is not None:
                idx = self.switch_interrupt
                self.switch_interrupt = None
                self._handle_switch_click(idx + 1)  # Switch indices are 1-based.
            await asyncio.sleep(0.01)

    def _handle_switch_click(self, switch):
        """
        Handle a switch click event.

        Args:
            switch (int): The index of the switch (1-based).
        """
        if switch <= 4:
            # Switches 1-4: Call the parent class's switch_click method.
            super().switch_click(switch)
        else:
            # Switches 5-6: Simulate encoder 1 rotation.
            direction = 1 if switch == 6 else -1  # Switch 5 = Previous, Switch 6 = Next.
            super().encoder_change(0, direction)  # Encoder 1 is index 0.
