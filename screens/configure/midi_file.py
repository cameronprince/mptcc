"""
MicroPython Tesla Coil Controller (MPTCC)
by Cameron Prince
teslauniverse.com

screens/configure/midi_file.py
Provides the screen for configuring MIDI file settings.
"""

from mptcc.hardware.init import init
from mptcc.lib.menu import CustomItem
from mptcc.lib.config import Config as config

class MIDIFileConfig(CustomItem):
    """
    A class to represent and handle the screen for configuring the MIDI
    file playback feature in the MicroPython Tesla Coil Controller (MPTCC).

    Attributes:
    -----------
    name : str
        The name of the MIDI File config screen.
    display : object
        The display object for rendering the screen.
    config : dict
        The configuration dictionary read from the flash memory.
    output_level : int
        The default output level for MIDI file playback.
    save_levels : bool
        Whether to save levels on end of playback.
    font_width : int
        The width of the font used in the display.
    """

    def __init__(self, name):
        """
        Constructs all the necessary attributes for the MIDIFileConfig object.

        Parameters:
        ----------
        name : str
            The name of the MIDI File config screen.
        """
        super().__init__(name)
        self.init = init
        self.display = self.init.display
        self.config = config.read_config()
        self.output_level = self.config.get("midi_file_output_level", config.DEF_MIDI_FILE_OUTPUT_LEVEL)
        self.save_levels = self.config.get("midi_file_auto_save_levels", config.DEF_MIDI_FILE_AUTO_SAVE_LEVELS)
        self.font_width = self.init.display.DISPLAY_FONT_WIDTH

    def draw(self):
        """
        Displays the MIDI file configuration screen with the output level and the save levels on end setting.
        """
        self.display.clear()
        self.display.header("MIDI File Config")

        # Display output level
        output_level_str = f"{self.output_level}%"
        self.display.text("Def. output", 0, 20, 1)
        self.display.text("level:", 0, 30, 1)
        self.display.text(output_level_str, self.display.width - len(output_level_str) * self.font_width, 30, 1)

        # Display save levels on end setting on the same line as the label
        save_levels_label = "Save levels:"
        save_levels_str = "Yes" if self.save_levels else "No"
        self.display.text(save_levels_label, 0, 50, 1)
        self.display.text(save_levels_str, self.display.width - len(save_levels_str) * self.font_width, 50, 1)

        self.display.show()

    def save_config(self):
        """
        Writes the MIDI file configuration to flash memory.
        """
        self.config["midi_file_output_level"] = self.output_level
        self.config["midi_file_auto_save_levels"] = self.save_levels
        config.write_config(self.config)

    def rotary_1(self, direction):
        """
        Responds to encoder 1 rotation to adjust the default output level.

        Parameters:
        ----------
        direction : int
            The direction of rotation (1 for clockwise, -1 for counterclockwise).
        """
        increment = 1
        self.output_level = max(1, min(100, self.output_level + increment * direction))

        self.save_config()
        self.draw()

    def rotary_2(self, direction):
        """
        Responds to encoder 2 rotation to toggle the save levels on end setting.

        Parameters:
        ----------
        direction : int
            The direction of rotation (1 for clockwise, -1 for counterclockwise).
        """
        # Toggle the save levels on end setting
        self.save_levels = not self.save_levels
        self.save_config()
        self.draw()

    def switch_2(self):
        """
        Responds to encoder 2 presses to return to the configuration menu.
        """
        parent_screen = self.parent
        if parent_screen:
            self.init.menu.set_screen(parent_screen)
            self.init.menu.draw()
