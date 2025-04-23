"""
MicroPython Tesla Coil Controller (MPTCC)
by Cameron Prince
teslauniverse.com

midi_file.py
Provides shared attributes/methods and routes inputs to sub-screens for the MIDI file feature.
"""

import json
import uos
from ...hardware.init import init
from ...lib.menu import Screen
from ...lib.config import Config as config


class MIDIFile(Screen):
    def __init__(self, name):
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
        self.outputs = [None] * self.init.NUMBER_OF_COILS
        self.last_rotary_1_value = 0
        self.per_page = 4
        self.output_y = None
        self.line_height = 12
        self.font_width = 8
        self.font_height = 8
        self.header_height = 10

        self.config = config.read_config()
        self.default_level = self.config.get("midi_file_output_level", config.DEF_MIDI_FILE_OUTPUT_LEVEL)
        self.levels = [self.default_level] * self.init.NUMBER_OF_COILS

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

        num_switches = max(6, self.init.NUMBER_OF_COILS)
        for i in range(1, num_switches + 1):
            setattr(self, f"switch_{i}", self._create_switch_method(i))

        num_rotaries = max(2, self.init.NUMBER_OF_COILS)
        for i in range(1, num_rotaries + 1):
            setattr(self, f"rotary_{i}", self._create_rotary_method(i))

        if self._has_master_encoder():
            setattr(self, "rotary_master", self._create_rotary_method("master"))
            setattr(self, "switch_master", self._create_switch_method("master"))

    def _has_master_encoder(self):
        for driver_key, driver_instances in self.init.input_instances.items():
            for instance_list in driver_instances.values():
                for instance in instance_list:
                    if hasattr(instance, "master") and instance.master:
                        return True
        return False

    def _create_rotary_method(self, encoder_id):
        def rotary_method(direction):
            self.rotary(encoder_id, direction)
        return rotary_method

    def _create_switch_method(self, switch_number):
        def switch_method():
            self.switch(switch_number)
        return switch_method

    def rotary(self, encoder_id, direction):
        handler = self.handlers.get(self.current_page)
        if handler:
            method_name = f"rotary_{encoder_id}"
            if hasattr(handler, method_name):
                getattr(handler, method_name)(direction)

    def switch(self, switch_number):
        handler = self.handlers.get(self.current_page)
        if handler and hasattr(handler, f"switch_{switch_number}"):
            getattr(handler, f"switch_{switch_number}")()

    def draw(self):
        self.handlers["files"].draw()

    def load_map_file(self, file_path):
        """
        Load the output assignments and levels from the map file, ensuring compatibility.
        """
        map_path = file_path.replace('.mid', '.map').replace('.midi', '.map')
        try:
            self.init.sd_card_reader.init_sd()
            with open(map_path, 'r') as f:
                map_data = json.load(f)

                if isinstance(map_data, dict):
                    mappings = map_data.get("mappings", [])
                    levels = map_data.get("levels", [self.default_level] * self.init.NUMBER_OF_COILS)
                else:
                    mappings = map_data
                    levels = [self.default_level] * self.init.NUMBER_OF_COILS

                if not isinstance(mappings, list) or not isinstance(levels, list):
                    raise ValueError("Invalid map file format: mappings and levels must be lists")

                # Pad or truncate mappings and levels to match NUMBER_OF_COILS
                mappings = (mappings + [0] * self.init.NUMBER_OF_COILS)[:self.init.NUMBER_OF_COILS]
                levels = (levels + [self.default_level] * self.init.NUMBER_OF_COILS)[:self.init.NUMBER_OF_COILS]

                # Assign mappings and levels
                for i in range(self.init.NUMBER_OF_COILS):
                    self.outputs[i] = mappings[i] if mappings[i] != 0 else None  # Changed: No -1
                    self.levels[i] = levels[i]
        except OSError:
            self.save_map_file(file_path, False)
        except Exception as e:
            print(f"Error loading map file: {e}")
            self.outputs = [None] * self.init.NUMBER_OF_COILS
            self.levels = [self.default_level] * self.init.NUMBER_OF_COILS
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
                "mappings": [output if output is not None else 0 for output in self.outputs],  # Changed: No +1
                "levels": self.levels
            }

            with open(map_path, 'w') as f:
                json.dump(map_data, f)
        except Exception as e:
            print(f"Error saving map file: {e}")
        finally:
            if initsd:
                self.init.sd_card_reader.deinit_sd()
