"""
MicroPython Tesla Coil Controller (MPTCC)
by Cameron Prince
teslauniverse.com

midi_file.py
Provides shared attributes/methods and routes inputs to sub-screens for the MIDI file feature.
The modules in the midi_file subdirectory provide the primary functionality.
"""

import json
import uos
from ...hardware.init import init
from ...lib.menu import Screen
from ...lib.config import Config as config

class MIDIFile(Screen):
    """
    A class to represent and handle MIDI file playback functionality for
    the MicroPython Tesla Coil Controller (MPTCC).

    Attributes:
    -----------
    file_list : list
        List of MIDI files available on the SD card.
    track_list : list
        List of tracks from the selected MIDI file.
    current_file_index : int
        Index of the currently selected file.
    current_track_index : int
        Index of the currently selected track.
    file_cursor_position : int
        Cursor position for file selection.
    track_cursor_position : int
        Cursor position for track selection.
    current_page : str
        Current page being displayed.
    selected_filename : str
        Name of the selected file.
    selected_track : int
        Index of the selected track.
    outputs : list
        List of outputs for each track.
    last_rotary_1_value : int
        Last value of rotary encoder 1.
    per_page : int
        Number of items displayed per page.
    output_y : int
        Y position of the output text on the display.
    line_height : int
        Display line height.
    font_width : int
        Display font width.
    font_height : int
        Display font height.
    header_height : int
        Display header height.
    handlers : dict
        Dictionary of screen handlers.
    """

    def __init__(self, name):
        """
        Constructs all the necessary attributes for the MIDIFile object.

        Parameters:
        ----------
        name : str
            The name of the screen.
        """
        super().__init__(name)

        self.name = name
        self.init = init
        self.display = self.init.display

        self.file_list = []
        self.track_list = []
        self.current_file_index = 0
        self.current_track_index = 0
        self.file_cursor_position = 0
        self.track_cursor_position = 0
        self.current_page = None
        self.selected_filename = None
        self.selected_track = None
        self.outputs = [None] * self.init.NUMBER_OF_COILS  # Dynamically sized based on NUMBER_OF_COILS
        self.last_rotary_1_value = 0
        self.levels = [config.DEF_MIDI_FILE_OUTPUT_LEVEL] * self.init.NUMBER_OF_COILS  # Dynamically sized
        self.per_page = self.display.DISPLAY_ITEMS_PER_PAGE
        self.output_y = None
        self.line_height = self.display.DISPLAY_LINE_HEIGHT
        self.font_width = self.display.DISPLAY_FONT_WIDTH
        self.font_height = self.display.DISPLAY_FONT_HEIGHT
        self.header_height = self.display.DISPLAY_HEADER_HEIGHT

        self.config = config.read_config()
        self.default_level = self.config.get("midi_file_output_level", config.DEF_MIDI_FILE_OUTPUT_LEVEL)

        # Initialize handlers.
        from mptcc.screens.midi_file import (
            MIDIFileFiles,
            MIDIFileTracks,
            MIDIFileAssignment,
            MIDIFilePlay
        )

        self.handlers = {
            "files": MIDIFileFiles(self),
            "tracks": MIDIFileTracks(self),
            "assignment": MIDIFileAssignment(self),
            "play": MIDIFilePlay(self),
        }

        # Dynamically create rotary_X and switch_X methods based on NUMBER_OF_COILS.
        for i in range(self.init.NUMBER_OF_COILS):
            setattr(self, f"rotary_{i + 1}", self._create_rotary_method(i + 1))
            setattr(self, f"switch_{i + 1}", self._create_switch_method(i + 1))

    def _create_rotary_method(self, encoder_number):
        """
        Factory function to create a rotary method for a specific encoder number.
        """
        def rotary_method(direction):
            self.rotary(encoder_number, direction)
        return rotary_method

    def _create_switch_method(self, switch_number):
        """
        Factory function to create a switch method for a specific switch number.
        """
        def switch_method():
            self.switch(switch_number)
        return switch_method

    def rotary(self, encoder_number, direction):
        """
        Respond to rotation of a rotary encoder.

        Parameters:
        ----------
        encoder_number : int
            The number of the rotary encoder (1, 2, 3, or 4).
        direction : int
            The rotary encoder direction.
        """
        handler = self.handlers.get(self.current_page)
        if handler:
            if hasattr(handler, f"rotary_{encoder_number}"):
                getattr(handler, f"rotary_{encoder_number}")(direction)

    def switch(self, switch_number):
        """
        Respond to presses of a switch.

        Parameters:
        ----------
        switch_number : int
            The number of the switch (1, 2, 3, or 4).
        """
        handler = self.handlers.get(self.current_page)
        if handler and hasattr(handler, f"switch_{switch_number}"):
            getattr(handler, f"switch_{switch_number}")()

    def draw(self):
        """
        Calls the draw function of the sub-screen.
        """
        self.handlers["files"].draw()

    def load_map_file(self, file_path):
        """
        Load the output assignments and levels from the map file.
        """
        map_path = file_path.replace('.mid', '.map').replace('.midi', '.map')

        try:
            self.init.sd_card_reader.init_sd()
            with open(map_path, 'r') as f:
                map_data = json.load(f)

                if isinstance(map_data, dict):
                    mappings = map_data["mappings"]
                    levels = map_data["levels"]
                else:
                    mappings = map_data
                    levels = [self.default_level] * self.init.NUMBER_OF_COILS  # Default levels

                if not isinstance(mappings, list) or not isinstance(levels, list):
                    raise ValueError("Invalid map file format: mappings and levels must be lists")

                # Ensure mappings and levels match the current NUMBER_OF_COILS
                if len(mappings) < self.init.NUMBER_OF_COILS:
                    mappings.extend([0] * (self.init.NUMBER_OF_COILS - len(mappings)))  # Pad with zeros
                if len(levels) < self.init.NUMBER_OF_COILS:
                    levels.extend([self.default_level] * (self.init.NUMBER_OF_COILS - len(levels)))  # Pad with default levels

                # Truncate if the map file has more elements than NUMBER_OF_COILS
                mappings = mappings[:self.init.NUMBER_OF_COILS]
                levels = levels[:self.init.NUMBER_OF_COILS]

                # Assign mappings and levels
                for i in range(self.init.NUMBER_OF_COILS):
                    self.outputs[i] = mappings[i] - 1 if mappings[i] != 0 else None
                    self.levels[i] = levels[i]
        except OSError:
            self.save_map_file(file_path, False)
        except Exception as e:
            print(f"Error loading map file: {e}")
        finally:
            self.init.sd_card_reader.deinit_sd()

    def save_map_file(self, file_path, initsd=True):
        """
        Save the output assignments and levels to the map file.
        """
        map_path = file_path.replace('.mid', '.map').replace('.midi', '.map')

        try:
            if initsd:
                self.init.sd_card_reader.init_sd()

            map_data = {
                "mappings": [(output + 1) if output is not None else 0 for output in self.outputs],
                "levels": self.levels
            }

            with open(map_path, 'w') as f:
                json.dump(map_data, f)
        except Exception as e:
            print(f"Error saving map file: {e}")
        finally:
            if initsd:
                self.init.sd_card_reader.deinit_sd()
