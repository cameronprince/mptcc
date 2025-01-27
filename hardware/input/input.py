"""
MicroPython Tesla Coil Controller (MPTCC)
by Cameron Prince
teslauniverse.com

hardware/input/input.py
Parent class for input devices.
"""
from ..hardware import Hardware
from ...lib.menu import CustomItem
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
        if isinstance(current_screen, CustomItem):
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
            current_screen = self.init.menu.get_current_screen()
            method_name = f'rotary_{idx + 1}'
            if isinstance(current_screen, CustomItem) and hasattr(current_screen, method_name):
                getattr(current_screen, method_name)(new_value)
            elif idx == 0:
                self.init.menu.move(-1 if self.last_rotations[idx] > new_value else 1)
            self.last_rotations[idx] = new_value
            time.sleep_ms(50)