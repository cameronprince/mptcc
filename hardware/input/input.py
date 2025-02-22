"""
MicroPython Tesla Coil Controller (MPTCC)
by Cameron Prince
teslauniverse.com

hardware/input/input.py
Parent class for input devices.
"""

from ..hardware import Hardware
from ...lib.menu import Screen
import time

class Input(Hardware):
    def __init__(self):
        super().__init__()
        self.switch_disabled = False

    def switch_click(self, switch):
        """
        The primary switch callback function.

        Parameters:
        ----------
        switch : int
            The switch number corresponding to the encoder (1 to 4).
        """
        if self.switch_disabled:
            self.switch_disabled = False
            return

        current_screen = self.init.menu.get_current_screen()
        if isinstance(current_screen, Screen):
            method_name = f'switch_{switch}'
            if hasattr(current_screen, method_name):
                getattr(current_screen, method_name)()
        else:
            if switch == 1:
                self.init.menu.click()
            elif switch == 2:
                parent_screen = self.init.menu.current_screen.parent
                if parent_screen:
                    self.init.menu.set_screen(parent_screen)
                    self.init.menu.draw()

    def rotary_encoder_change(self, idx, new_value):
        """
        The primary rotary encoder callback function.

        Parameters:
        ----------
        idx : int
            Index of the encoder.
        new_value : int
            The new value of the encoder.
        """
        if self.last_rotations[idx] != new_value:
            # Handle wrap-around cases.
            if self.last_rotations[idx] == 0 and new_value == 100:
                direction = -1
            elif self.last_rotations[idx] == 100 and new_value == 0:
                direction = 1
            else:
                direction = 1 if new_value > self.last_rotations[idx] else -1

            current_screen = self.init.menu.get_current_screen()
            method_name = f'rotary_{idx + 1}'
            if isinstance(current_screen, Screen) and hasattr(current_screen, method_name):
                getattr(current_screen, method_name)(direction)
            elif idx == 0:
                self.init.menu.move(direction)
            self.last_rotations[idx] = new_value
            time.sleep_ms(50)
