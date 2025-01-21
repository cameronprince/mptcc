"""
MicroPython Tesla Coil Controller (MPTCC)
by Cameron Prince
teslauniverse.com

screens/midi_file/tracks.py
Provides the MIDI track listing screen.
"""

from mptcc.init import init
import mptcc.lib.utils as utils
import umidiparser

class MIDIFileTracks:
    def __init__(self, midi_file):
        """
        Initialize the tracks handler with the MIDIFile instance.

        Parameters:
        ----------
        midi_file : MIDIFile
            The parent MIDIFile instance.
        """
        self.midi_file = midi_file
        self.init = init
        self.display = self.init.display

    def draw(self):
        self.midi_file.current_page = "tracks"

        # Show the loading message.
        self.display.loading_screen()

        if not self.midi_file.track_list:
            self.get_tracks()
        if not self.midi_file.track_list:
            self.display.alert_screen("No tracks found")
            self.midi_file.handlers["files"].draw()
        else:
            # Calculate the number of mapped tracks
            mapped_tracks_count = sum(1 for output in self.midi_file.outputs if output is not None)
            self.display.header(f'MIDI Tracks {mapped_tracks_count}/{len(self.midi_file.outputs)}')
            start = self.midi_file.current_track_index
            end = min(self.midi_file.current_track_index + 4, len(self.midi_file.track_list))
            menu_y_end = 12
            for i in range(start, end):
                midi_track = self.midi_file.track_list[i]
                y = menu_y_end + ((i - start) * self.midi_file.line_height)
                v_padding = int((self.midi_file.line_height - self.midi_file.font_height) / 2)
                is_active = (i == self.midi_file.current_track_index + self.midi_file.track_cursor_position)
                background = int(is_active)
                self.display.fill_rect(0, y, self.display.width, self.midi_file.line_height, background)
                if is_active:
                    self.display.text(midi_track[:20], 0, y + v_padding, 0)
                else:
                    self.display.text(midi_track[:20], 0, y + v_padding, 1)
            self.display.show()
            active_track = self.midi_file.track_list[self.midi_file.current_track_index + self.midi_file.track_cursor_position]
            active_y_position = menu_y_end + ((self.midi_file.track_cursor_position) * self.midi_file.line_height)
            text_width = len(active_track) * self.midi_file.font_width
            if text_width > self.display.width:
                self.display.start_scroll_task(active_track, active_y_position)
            else:
                self.display.stop_scroll_task()

    def get_tracks(self):
        """
        Get the track names from the selected MIDI file.
        """
        self.midi_file.track_list = []

        file_path = self.init.SD_MOUNT_POINT + "/" + self.midi_file.file_list[self.midi_file.selected_file]

        # We're unable to share sd_init actions due to try/catch on load_map which
        # needed for "No tracks mapped" error during playback.
        self.midi_file.load_map_file(file_path)

        # Initialize the SD card reader so we can read the MIDI file.
        self.init.sd_card_reader.init_sd()
        
        midi = umidiparser.MidiFile(file_path, buffer_size=0, reuse_event_object=False)
        for track in midi.tracks:
            for event in track:
                if not event.is_meta():
                    break
                if event.status == umidiparser.TRACK_NAME:
                    self.midi_file.track_list.append(event.name)

        self.init.sd_card_reader.deinit_sd()

    def rotary_1(self, val):
        """
        Responds to rotation of encoder 1 for scrolling the track list.

        Parameters:
        ----------
        val : int
            The value from the rotary encoder.
        """
        direction = 1 if val > self.midi_file.last_rotary_1_value else -1
        self.midi_file.last_rotary_1_value = val

        item_list = self.midi_file.track_list
        cursor_position = self.midi_file.track_cursor_position
        index = self.midi_file.current_track_index

        new_position = index + cursor_position + direction

        # Check if the new position is within valid bounds.
        if 0 <= new_position < len(item_list):
            cursor_position += direction
            # Calculations for incrementing/decrementing cursor position
            # while maintaining four items on the screen.
            if cursor_position >= self.midi_file.per_page:
                index += 1
                cursor_position = (self.midi_file.per_page - 1)
            if cursor_position < 0:
                index -= 1
                cursor_position = 0
            if index + self.midi_file.per_page > len(item_list):
                index = max(0, len(item_list) - self.midi_file.per_page)

        self.midi_file.current_track_index = index
        self.midi_file.track_cursor_position = cursor_position

        # Refresh the display with the new cursor positioning.
        self.draw()

    def switch_1(self):
        """
        Responds to presses of encoder 1 to select tracks.
        """
        self.display.stop_scroll_task()
        self.midi_file.selected_track = self.midi_file.current_track_index + self.midi_file.track_cursor_position
        self.midi_file.handlers["assignment"].draw()

    def switch_2(self):
        """
        Responds to presses of encoder 2 to go back.
        """
        self.display.stop_scroll_task()
        self.midi_file.track_list = []
        self.midi_file.handlers["files"].draw()

