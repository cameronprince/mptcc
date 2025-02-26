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
        """
        # print(f"rotary_encoder_change: Encoder {idx} value changed to {new_value}")  # Debugging
        if not self.init.ignore_input and self.last_rotations[idx] != new_value:
            # Handle wrap-around cases.
            if self.last_rotations[idx] == 0 and new_value == 100:
                direction = -1
            elif self.last_rotations[idx] == 100 and new_value == 0:
                direction = 1
            else:
                direction = 1 if new_value > self.last_rotations[idx] else -1

            # Update the timestamp for the last rotary input.
            self.init.last_rotary_input = time.ticks_ms()

            # Get the current screen.
            current_screen = self.init.menu.get_current_screen()
            # print(f"rotary_encoder_change: Current screen is {current_screen}")  # Debugging

            if current_screen:
                method_name = f'rotary_{idx + 1}'
                # print(f"rotary_encoder_change: Looking for method {method_name} on current screen")  # Debugging
                # print("direction: ", direction)

                if hasattr(current_screen, method_name):
                    # print(f"rotary_encoder_change: Calling {method_name} on current screen")  # Debugging
                    getattr(current_screen, method_name)(direction)
                else:
                    # print(f"rotary_encoder_change: Method {method_name} not found on current screen")  # Debugging
                    if idx == 0:
                        # print("rotary_encoder_change: Falling back to menu.move")  # Debugging
                        self.init.menu.move(direction)
            else:
                pass
                # print("rotary_encoder_change: No current screen found")  # Debugging

            # Update the last rotation value.
            self.last_rotations[idx] = new_value
            time.sleep_ms(50)
