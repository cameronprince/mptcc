"""
MicroPython Tesla Coil Controller (MPTCC)
by Cameron Prince
teslauniverse.com

screens/configure/restore_defaults.py
Provides the screen for restoring default settings.
"""

import os
from mptcc.hardware.init import init
from mptcc.lib.menu import CustomItem
import mptcc.lib.config as config

class RestoreDefaults(CustomItem):
    """
    A class to represent and handle the screen for restoring default settings
    in the MicroPython Tesla Coil Controller (MPTCC).

    Attributes:
    -----------
    name : str
        The name of the restore defaults screen.
    selection : str
        The current selection ("Yes" or "No").
    """

    def __init__(self, name):
        """
        Constructs all the necessary attributes for the RestoreDefaults object.

        Parameters:
        ----------
        name : str
            The name of the restore defaults screen.
        """
        super().__init__(name)
        self.init = init
        self.selection = "No"  # Default to "No" initially
        self.val_old = 0

    def draw(self):
        """
        Displays the restore defaults screen with options.
        """
        self.init.display.clear()
        self.init.display.header("Restore Defaults")

        # Display the options
        self.init.display.text("Restore defaults:", 0, 20, 1)

        # Highlight the current selection
        yes_background = int(self.selection == "Yes")
        no_background = int(self.selection == "No")

        self.init.display.fill_rect(0, 30, 35, 10, yes_background)
        self.init.display.text("Yes", 0, 30, int(not yes_background))

        self.init.display.fill_rect(40, 30, 35, 10, no_background)
        self.init.display.text("No", 40, 30, int(not no_background))

        self.init.display.show()

    def restore_defaults(self):
        """
        Performs the default restoration which consists of removing the config file.
        """
        try:
            os.remove(init.CONFIG_PATH)
        except OSError:
            pass
        self.init.display.clear()
        # Display the success message for two seconds and return to the main menu.
        self.init.display.alert_screen("Defaults restored")

        # Return to the main menu.
        self.init.menu.reset()
        self.init.menu.draw()

    def rotary_1(self, val):
        """
        Responds to encoder 1 rotation to select between "Yes" and "No".

        Parameters:
        ----------
        val : int
            The new value from the rotary encoder.
        """
        direction = val - self.val_old
        if direction == 0:
            return  # No change in direction, so no update needed.

        # Toggle the selection between "Yes" and "No"
        self.selection = "Yes" if self.selection == "No" else "No"

        self.val_old = val
        self.draw()

    def switch_1(self):
        """
        Responds to switch 1 presses to perform the restore action if "Yes" is selected,
        or return to the configuration menu if "No" is selected.
        """
        if self.selection == "Yes":
            self.restore_defaults()
        else:
            self.switch_2()

    def switch_2(self):
        """
        Responds to encoder 2 presses to return to the configuration menu.
        """
        parent_screen = self.parent
        if parent_screen:
            self.init.menu.set_screen(parent_screen)
            self.init.menu.draw()