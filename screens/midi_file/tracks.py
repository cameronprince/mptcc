"""
MicroPython Tesla Coil Controller (MPTCC)
by Cameron Prince
teslauniverse.com

screens/midi_file/tracks.py
Provides the MIDI track listing screen.
"""

from ...hardware.init import init
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

    def draw(self, surpress_loading_message=False):
        """
        Draw the MIDI tracks on the display.
        """
        self.midi_file.current_page = "tracks"

        if not surpress_loading_message:
            # Show a loading message.
            self.display.loading_screen()

        if not self.midi_file.track_list:
            self.get_tracks()
        if not self.midi_file.track_list:
            self.display.alert_screen("No tracks found")
            self.midi_file.handlers["files"].draw()
        else:
            # Calculate the number of mapped tracks.
            mapped_tracks_count = sum(1 for output in self.midi_file.outputs if output is not None)
            self.display.header(f'MIDI Tracks {mapped_tracks_count}/{len(self.midi_file.outputs)}')
            start = self.midi_file.current_track_index
            end = min(self.midi_file.current_track_index + self.init.NUMBER_OF_COILS, len(self.midi_file.track_list))  # Updated to use NUMBER_OF_COILS
            menu_y_end = 12
            for i in range(start, end):
                track_info = self.midi_file.track_list[i]
                track_name = track_info["name"]
                original_index = track_info["original_index"]

                # Check if the track is mapped.
                if original_index in self.midi_file.outputs:
                    track_name = f"* {track_name}"

                y = menu_y_end + ((i - start) * self.midi_file.line_height)
                v_padding = int((self.midi_file.line_height - self.midi_file.font_height) / 2)
                is_active = (i == self.midi_file.current_track_index + self.midi_file.track_cursor_position)
                background = int(is_active)
                self.display.fill_rect(0, y, self.display.width, self.midi_file.line_height, background)
                self.display.text(track_name[:20], 0, y + v_padding, 0 if is_active else 1)

            self.display.show()

            # Handle scrolling for the active track.
            active_track_info = self.midi_file.track_list[self.midi_file.current_track_index + self.midi_file.track_cursor_position]
            active_track_name = active_track_info["name"]
            if active_track_info["original_index"] in self.midi_file.outputs:
                active_track_name = f"* {active_track_name}"
            active_y_position = menu_y_end + ((self.midi_file.track_cursor_position) * self.midi_file.line_height)
            text_width = len(active_track_name) * self.midi_file.font_width
            if text_width > self.display.width:
                # Pass the track index as the unique identifier.
                self.display.start_scroll_task(active_track_name, active_y_position, self.midi_file.current_track_index + self.midi_file.track_cursor_position)
            else:
                self.display.stop_scroll_task()
                # If the text doesn't require scrolling, ensure the display is updated.
                self.display.fill_rect(0, active_y_position, self.display.width, self.midi_file.line_height, 1)  # Clear the line.
                v_padding = int((self.midi_file.line_height - self.midi_file.font_height) / 2)
                self.display.text(active_track_name, 0, active_y_position + v_padding, 0)
                self.display.show()

    def get_tracks(self):
        """
        Get the track names from the selected MIDI file, filtering out tracks
        without NOTE_ON events.
        """
        self.midi_file.track_list = []

        file_path = self.init.SD_CARD_READER_MOUNT_POINT + "/" + self.midi_file.file_list[self.midi_file.selected_file]

        # We're unable to share sd_init actions due to try/catch on load_map which
        # needed for "No tracks mapped" error during playback.
        self.midi_file.load_map_file(file_path)

        # Initialize the SD card reader so we can read the MIDI file.
        self.init.sd_card_reader.init_sd()

        # Track counter for default names.
        track_counter = 1

        for index, track in enumerate(umidiparser.MidiFile(file_path, buffer_size=0).tracks):
            has_note_on = False
            track_name = None

            # First pass: Check for NOTE_ON events and track name.
            for event in track:
                if event.is_meta() and event.status == umidiparser.TRACK_NAME:
                    track_name = event.name
                elif not event.is_meta() and event.status == umidiparser.NOTE_ON:
                    has_note_on = True
                    break  # Exit the loop early once a NOTE_ON event is found.

            # Only add tracks with NOTE_ON events.
            if has_note_on:
                # Assign a default name if the track has no name.
                if not track_name:
                    track_name = f"Track {track_counter}"
                    track_counter += 1  # Increment the track counter.
                self.midi_file.track_list.append({"name": track_name, "original_index": index})

        self.init.sd_card_reader.deinit_sd()

    def rotary_1(self, direction):
        """
        Responds to rotation of encoder 1 for scrolling the track list.

        Parameters:
        ----------
        direction : int
            The direction of rotation (1 for clockwise, -1 for counterclockwise).
        """
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
        self.draw(True)

    def switch_1(self):
        """
        Responds to presses of encoder 1 to select tracks.
        """
        print("switch_1")
        self.display.stop_scroll_task()
        selected_track_info = self.midi_file.track_list[self.midi_file.current_track_index + self.midi_file.track_cursor_position]
        self.midi_file.selected_track = selected_track_info["original_index"]
        self.midi_file.handlers["assignment"].draw()

    def switch_2(self):
        """
        Responds to presses of encoder 2 to go back.
        """
        self.display.stop_scroll_task()
        self.midi_file.track_list = []
        self.midi_file.handlers["files"].draw()
