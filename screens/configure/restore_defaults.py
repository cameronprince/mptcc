"""
MicroPython Tesla Coil Controller (MPTCC)
by Cameron Prince
teslauniverse.com

screens/configure/restore_defaults.py
Provides the screen for restoring default settings.
"""

import os
from mptcc.hardware.init import init
from mptcc.lib.menu import Screen
import mptcc.lib.config as config

class RestoreDefaults(Screen):
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
        self.name = name
        self.init = init
        self.selection = "No"

    def draw(self):
        """
        Displays the restore defaults screen with options.
        """
        self.init.display.clear()
        self.init.display.header(self.name)

        # Calculate positions for centering text.
        screen_width = self.init.display.width
        font_width = self.init.display.DISPLAY_FONT_WIDTH
        font_height = self.init.display.DISPLAY_FONT_HEIGHT
        padding = 2
        vertical_spacing = 10

        restore_defaults_text = "Restore now?"
        restore_defaults_x = (screen_width - len(restore_defaults_text) * font_width) // 2

        yes_text = "Yes"
        no_text = "No"
        yes_no_text = f"{yes_text}       {no_text}"
        yes_no_x = (screen_width - len(yes_no_text) * font_width) // 2

        # Display the centered options.
        self.init.display.text(restore_defaults_text, restore_defaults_x, 20, 1)

        # Highlight the current selection.
        yes_background = int(self.selection == "Yes")
        no_background = int(self.selection == "No")

        yes_x = yes_no_x
        no_x = yes_no_x + len(yes_text) * font_width + 7 * font_width
        box_height = font_height + 2 * padding
        yes_y = 30 + vertical_spacing
        no_y = yes_y

        # Draw the background rectangles with padding.
        self.init.display.fill_rect(yes_x - padding, yes_y - padding, len(yes_text) * font_width + 2 * padding, box_height, yes_background)
        self.init.display.text(yes_text, yes_x, yes_y, int(not yes_background))

        self.init.display.fill_rect(no_x - padding, no_y - padding, len(no_text) * font_width + 2 * padding, box_height, no_background)
        self.init.display.text(no_text, no_x, no_y, int(not no_background))

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

    def rotary_1(self, direction):
        """
        Responds to encoder 1 rotation to select between "Yes" and "No".

        Parameters:
        ----------
        direction : int
            The direction of rotation (1 for clockwise, -1 for counterclockwise).
        """
        # Toggle the selection between "Yes" and "No".
        self.selection = "Yes" if self.selection == "No" else "No"

        self.draw()

    def switch_1(self):
        """
        Responds to switch 1 presses to perform the restore action if "Yes" is selected,
        or return to the configuration menu if "No" is selected.
        """
        if self.selection == "Yes":
            self.init.inputs.switch_disabled = True
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
