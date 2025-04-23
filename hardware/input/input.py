"""
MicroPython Tesla Coil Controller (MPTCC)
by Cameron Prince
teslauniverse.com

hardware/input/input.py
Parent class for input devices.
"""

from ..hardware import Hardware
from ..init import init
from ...lib.menu import Screen
import time


class Input(Hardware):
    def __init__(self):
        super().__init__()
        self.init = init

    def switch_click(self, switch):
        """
        The primary switch callback function.

        Parameters:
        ----------
        switch : int
            The switch number corresponding to the encoder.
        """
        # Check to see if beep tone confirmation is to be fired.
        if hasattr(self.init, 'beep'):
            self.init.beep.on()

        # If we're on a screen, route the clicks to its switch functions.
        current_screen = self.init.menu.get_current_screen()
        if isinstance(current_screen, Screen):
            method_name = f"switch_{switch}"
            if hasattr(current_screen, method_name):
                getattr(current_screen, method_name)()
        else:
            if switch == 1:
                # Route clicks to the menu.
                self.init.menu.click()
            elif switch == 2:
                # Act as a back/return button.
                parent_screen = self.init.menu.current_screen.parent
                if parent_screen:
                    self.init.menu.set_screen(parent_screen)
                    self.init.menu.draw()

    def encoder_change(self, idx, direction):
        """
        The primary rotary encoder callback function.
        """
        # Get the current screen.
        current_screen = self.init.menu.get_current_screen()

        if current_screen:
            if isinstance(idx, int):
                method_name = f"rotary_{idx + 1}"
            else:
                method_name = f"rotary_{idx}"

            # Check to see if beep tone confirmation is to be fired.
            if hasattr(self.init, 'beep'):
                self.init.beep.on()

            if hasattr(current_screen, method_name):
                getattr(current_screen, method_name)(direction)
            else:
                if idx == 0:
                    self.init.menu.move(direction)
