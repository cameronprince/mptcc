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

    def switch_click(self, switch):
        """
        The primary switch callback function.

        Parameters:
        ----------
        switch : int
            The switch number corresponding to the encoder (1 to 4).
        """
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

    def rotary_encoder_change(self, idx, new_value=None, direction=None):
        """
        The primary rotary encoder callback function.
        """
        # Get the current screen.
        current_screen = self.init.menu.get_current_screen()

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
        if current_screen:
            method_name = f'rotary_{idx + 1}'

            if hasattr(current_screen, method_name):
                getattr(current_screen, method_name)(direction)
            else:
                if idx == 0:
                    self.init.menu.move(direction)

        if new_value is not None:
            self.last_rotations[idx] = new_value

        time.sleep_ms(50)
