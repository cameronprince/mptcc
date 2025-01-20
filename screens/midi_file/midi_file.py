"""
MicroPython Tesla Coil Controller (MPTCC)
by Cameron Prince
teslauniverse.com

midi_file.py
Provides shared attributes/methods and routes inputs to sub-screens for the MIDI file feature.
The modules in the midi_file subdirectory provide the primary functionality.
"""

from mptcc.init import init
from mptcc.lib.menu import CustomItem
import mptcc.lib.utils as utils
import json
import uos

class MIDIFile(CustomItem):
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
    selected_track : str
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
            The name of the MIDI file.
        """
        super().__init__(name)
        self.file_list = []
        self.track_list = []
        self.current_file_index = 0
        self.current_track_index = 0
        self.file_cursor_position = 0
        self.track_cursor_position = 0
        self.current_page = None
        self.selected_filename = None
        self.selected_track = None
        self.outputs = [None] * 4
        self.last_rotary_1_value = 0
        self.per_page = init.DISPLAY_ITEMS_PER_PAGE
        self.output_y = None
        self.line_height = init.DISPLAY_LINE_HEIGHT
        self.font_width = init.DISPLAY_FONT_WIDTH
        self.font_height = init.DISPLAY_FONT_HEIGHT
        self.header_height = init.DISPLAY_HEADER_HEIGHT

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

    def draw(self):
        self.handlers["files"].draw()

    def load_map_file(self, file_path):
        """
        Load the output assignments from the map file.

        Parameters:
        ----------
        file_path : str
            Path to the MIDI file, which will be used to determine the map file path.
        init_sd : bool
            Flag to indicate whether to initialize the SD card.
        """
        map_path = file_path.replace('.mid', '.map').replace('.midi', '.map')

        # Ensure the outputs array is always initialized with a fixed length of four
        self.outputs = [None] * 4

        try:
            init.init_sd()
            with open(map_path, 'r') as f:
                map_data = json.load(f)
                for i in range(min(len(self.outputs), len(map_data))):
                    self.outputs[i] = map_data[i] - 1 if map_data[i] != 0 else None
        except OSError:
            pass
        except Exception as e:
            pass
        finally:
            init.deinit_sd()

    def save_map_file(self):
        """
        Save the output assignments to the map file.
        Assumes the SD card is already mounted.
        """
        map_filename = self.file_list[self.selected_file].replace('.mid', '.map').replace('.midi', '.map')
        map_path = init.SD_MOUNT_POINT + "/" + map_filename

        try:
            init.init_sd()

            if self.selected_track is None:
                raise ValueError("No track selected.")

            current_track = self.selected_track
            current_output = self.outputs[current_track]

            for i in range(len(self.outputs)):
                if i != current_track and self.outputs[i] == current_output:
                    self.outputs[i] = None

            map_data = [(output + 1) if output is not None else 0 for output in self.outputs]

            with open(map_path, 'w') as f:
                json.dump(map_data, f)
        except Exception as e:
            pass
        finally:
            init.deinit_sd()

    def rotary_1(self, val):
        """
        Respond to rotation of encoder 1.

        Parameters:
        ----------
        val : int
            The value from the rotary encoder.
        """
        handler = self.handlers.get(self.current_page)
        if handler and hasattr(handler, "rotary_1"):
            handler.rotary_1(val)

    def rotary_2(self, val):
        """
        Respond to rotation of encoder 2.

        Parameters:
        ----------
        val : int
            The value from the rotary encoder.
        """
        handler = self.handlers.get(self.current_page)
        if handler and hasattr(handler, "rotary_2"):
            handler.rotary_2(val)

    def rotary_3(self, val):
        """
        Respond to rotation of encoder 3.

        Parameters:
        ----------
        val : int
            The value from the rotary encoder.
        """
        handler = self.handlers.get(self.current_page)
        if handler and hasattr(handler, "rotary_3"):
            handler.rotary_3(val)

    def rotary_4(self, val):
        """
        Respond to rotation of encoder 4.

        Parameters:
        ----------
        val : int
            The value from the rotary encoder.
        """
        handler = self.handlers.get(self.current_page)
        if handler and hasattr(handler, "rotary_4"):
            handler.rotary_4(val)

    def switch_1(self):
        """
        Respond to presses of encoder 1.
        """
        handler = self.handlers.get(self.current_page)
        if handler and hasattr(handler, "switch_1"):
            handler.switch_1()

    def switch_2(self):
        """
        Respond to presses of encoder 2.
        """
        handler = self.handlers.get(self.current_page)
        if handler and hasattr(handler, "switch_2"):
            handler.switch_2()

    def switch_3(self):
        """
        Respond to presses of encoder 3.
        """
        handler = self.handlers.get(self.current_page)
        if handler and hasattr(handler, "switch_3"):
            handler.switch_3()

    def switch_4(self):
        """
        Respond to presses of encoder 4.
        """
        handler = self.handlers.get(self.current_page)
        if handler and hasattr(handler, "switch_4"):
            handler.switch_4()
