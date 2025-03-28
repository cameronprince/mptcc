"""
MicroPython Tesla Coil Controller (MPTCC)
by Cameron Prince
teslauniverse.com

screens/midi_file/files.py
Provides the MIDI file listing screen.
"""

from ...hardware.init import init
from ...lib.config import Config as config
from ...hardware.display.tasks import start_scroll, stop_scroll
import uos


class MIDIFileFiles:
    def __init__(self, midi_file):
        """
        Initialize the display files handler with the MIDIFile instance.

        Parameters:
        ----------
        midi_file : MIDIFile
            The parent MIDIFile instance.
        """
        self.midi_file = midi_file
        self.init = init
        self.display = self.init.display
        self.previous_active_file = None
        self.previous_active_y_position = None

    def draw(self):
        """
        Display the list of MIDI files on the screen.
        """
        # Show a loading message.
        self.display.loading_screen()

        # Get the files from the SD card.
        self.init.sd_card_reader.init_sd()
        sd_init = self.load_files()
        self.init.sd_card_reader.deinit_sd()

        # Only proceed if the SD card was initialized successfully.
        if sd_init:
            if not self.midi_file.file_list:
                self.display.alert_screen("No MIDI files found")
                parent_screen = self.midi_file.parent
                if parent_screen:
                    self.init.menu.set_screen(parent_screen)
                    self.init.menu.draw()
            else:
                self.midi_file.current_page = "files"
                self.update_display()
        self.init.ignore_input = False

    def update_display(self):
        """
        Update the display with the list of MIDI files.
        """
        self.display.header("MIDI Files")

        start = self.midi_file.current_file_index
        end = min(self.midi_file.current_file_index + self.midi_file.per_page, len(self.midi_file.file_list))
        menu_y_end = self.midi_file.line_height

        for i in range(start, end):
            midi_file = self.midi_file.file_list[i]
            y = menu_y_end + ((i - start) * self.midi_file.line_height)
            v_padding = int((self.midi_file.line_height - self.midi_file.font_height) / 2)
            is_active = (i == self.midi_file.current_file_index + self.midi_file.file_cursor_position)
            background = int(is_active)
            self.display.fill_rect(0, y, self.display.width, self.midi_file.line_height, background)
            self.display.text(midi_file, 0, y + v_padding, not is_active)

            if is_active:
                # Handle scrolling for the new active file.
                text_width = len(midi_file) * self.midi_file.font_width
                if text_width > self.display.width:
                    start_scroll(self.display, midi_file, y, i)  # Pass the file index as the unique identifier.
                else:
                    # If the text doesn't require scrolling, stop the scrolling task.
                    stop_scroll(self.display)
                    # Ensure the display is updated.
                    self.display.fill_rect(0, y, self.display.width, self.midi_file.line_height, background)
                    self.display.text(midi_file, 0, y + v_padding, not is_active)
                    self.display.show()

        self.display.show()

    def load_files(self):
        """
        Load the list of MIDI files from the SD card.
        """
        try:
            self.midi_file.file_list = [
                f[0] if isinstance(f, tuple) else f 
                for f in uos.listdir(self.init.SD_CARD_READER_MOUNT_POINT)
                if (isinstance(f, str) or isinstance(f, tuple)) and 
                    ((isinstance(f, str) and (f.endswith(".mid") or f.endswith(".midi")) and not f.startswith("._")) or
                    (isinstance(f, tuple) and f[0].endswith((".mid", ".midi")) and not f[0].startswith("._")))
            ]
            return True
        except OSError as e:
            print(f"Error initializing SD card: {e}")
            self.display.alert_screen("No SD Card")

            # Return to the main menu.
            self.midi_file.current_page = ""
            parent_screen = self.midi_file.parent
            if parent_screen:
                self.init.menu.set_screen(parent_screen)
                self.init.menu.draw()
            return False

    def rotary_1(self, direction):
        """
        Responds to rotation of encoder 1 for scrolling the file list.

        Parameters:
        ----------
        direction : int
            The direction of rotation (1 for clockwise, -1 for counterclockwise).
        """
        item_list = self.midi_file.file_list
        cursor_position = self.midi_file.file_cursor_position
        index = self.midi_file.current_file_index

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

            self.midi_file.current_file_index = index
            self.midi_file.file_cursor_position = cursor_position

            # Refresh the display with the new cursor positioning.
            self.update_display()

    def switch_1(self):
        """
        Responds to presses of encoder 1 to select files.
        """
        stop_scroll(self.display)
        self.midi_file.selected_file = self.midi_file.current_file_index + self.midi_file.file_cursor_position
        self.midi_file.track_cursor_position = 0
        self.midi_file.outputs = [None] * self.init.NUMBER_OF_COILS
        self.midi_file.levels = [config.DEF_MIDI_FILE_OUTPUT_LEVEL] * self.init.NUMBER_OF_COILS
        self.midi_file.handlers["tracks"].draw()
        # Prevent clicks from propagating to the tracks sub-screen on files with
        # a lot of tracks.
        self.init.switch_disabled = True

    def switch_2(self):
        """
        Responds to presses of encoder 2 to go back.
        """
        stop_scroll(self.display)
        # Clear all positioning so return visits start at the top of the list.
        self.midi_file.current_file_index = 0
        self.midi_file.file_cursor_position = 0
        self.midi_file.selected_file = None
        self.midi_file.selected_track = None
        # Return to the main menu.
        parent_screen = self.midi_file.parent
        if parent_screen:
            self.display.clear()
            self.init.menu.set_screen(parent_screen)
            self.init.menu.draw()

    def switch_3(self):
        """
        Responds to presses of encoder 3 to play the selected MIDI file.
        """
        stop_scroll(self.display)
        self.midi_file.selected_file = self.midi_file.current_file_index + self.midi_file.file_cursor_position
        file_path = self.init.SD_CARD_READER_MOUNT_POINT + "/" + self.midi_file.file_list[self.midi_file.selected_file]
        self.midi_file.handlers["play"].draw(file_path)
