"""
MicroPython Tesla Coil Controller (MPTCC)
by Cameron Prince
teslauniverse.com

hardware/input/switch_gpio.py
GPIO switch input driver.
"""

import time
from machine import Pin
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
        self.debounce_delay = 300  # Debounce delay in milliseconds.
        self.instances = []

        # Disable integrated switches in encoders.
        init.integrated_switches = False

        # Initialize GPIO pins for switches.
        self.switch_pins = []
        for i, pin in enumerate(self.pins):
            switch_pin = Pin(pin, Pin.IN, Pin.PULL_UP if self.pull_up else Pin.PULL_DOWN)
            switch_pin.irq(handler=lambda p, idx=i: self._handle_interrupt(idx), trigger=Pin.IRQ_FALLING)
            self.instances.append(switch_pin)

        # Print initialization details.
        print(f"GPIO switch driver initialized with {len(self.pins)} switches (pull_up={self.pull_up}):")
        for i, pin in enumerate(self.pins):
            print(f"- Switch {i + 1}: GPIO={pin}")

    def _handle_interrupt(self, idx):
        """
        Handle switch interrupts.

        Args:
            idx (int): The index of the switch.
        """
        current_time = time.ticks_ms()
        if time.ticks_diff(current_time, self.last_switch_click_time[idx]) > self.debounce_delay:
            self.last_switch_click_time[idx] = current_time
            self._handle_switch_click(idx + 1)  # Switch indices are 1-based.

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
            # Ignore navigation switches when not displaying the menu.
            current_screen = self.init.menu.get_current_screen()
            if not isinstance(current_screen, Screen):
                direction = 1 if switch == 6 else -1  # Switch 5 = Previous, Switch 6 = Next.
                super().encoder_change(0, direction)  # Encoder 1 is index 0.
