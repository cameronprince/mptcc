"""
MicroPython Tesla Coil Controller (MPTCC)
by Cameron Prince
teslauniverse.com

screens/midi_file/files.py
Provides the MIDI file listing screen.
"""

from mptcc.init import init
import mptcc.lib.utils as utils
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

    def draw(self):
        """
        Display the list of MIDI files on the screen.
        """
        # Show a loading message.
        utils.loading_screen()

        # Get the files from the SD card.
        sd_init = self.load_files()

        # Only proceed if the SD card was initialized successfully.
        if sd_init:
            if not self.midi_file.file_list:
                utils.alert_screen("No MIDI files found")
                parent_screen = self.midi_file.parent
                if parent_screen:
                    init.menu.set_screen(parent_screen)
                    init.menu.draw()
            else:
                self.midi_file.current_page = "files"
                self.update_display()

    def update_display(self):
        """
        Update the display with the list of MIDI files.
        """
        init.display.fill(0)
        utils.header("MIDI Files")

        start = self.midi_file.current_file_index
        end = min(self.midi_file.current_file_index + self.midi_file.per_page, len(self.midi_file.file_list))
        menu_y_end = self.midi_file.line_height
        for i in range(start, end):
            midi_file = self.midi_file.file_list[i]
            y = menu_y_end + ((i - start) * self.midi_file.line_height)
            v_padding = int((self.midi_file.line_height - self.midi_file.font_height) / 2)
            is_active = (i == self.midi_file.current_file_index + self.midi_file.file_cursor_position)
            background = int(is_active)
            init.display.fill_rect(0, y, init.display.width, self.midi_file.line_height, background)
            if is_active:
                init.display.text(midi_file[:20], 0, y + v_padding, 0)
            else:
                init.display.text(midi_file[:20], 0, y + v_padding, 1)
        init.display.show()

        # Handle scrolling of long filenames.
        active_file = self.midi_file.file_list[self.midi_file.current_file_index + self.midi_file.file_cursor_position]
        active_y_position = menu_y_end + ((self.midi_file.file_cursor_position) * self.midi_file.line_height)
        text_width = len(active_file) * self.midi_file.font_width
        if text_width > init.display.width:
            utils.start_scroll_task(active_file, active_y_position)
        else:
            utils.stop_scroll_task()

    def load_files(self):
        """
        Load the list of MIDI files from the SD card.
        """
        try:
            init.init_sd()

            self.midi_file.file_list = [
                f[0] if isinstance(f, tuple) else f 
                for f in uos.listdir(init.SD_MOUNT_POINT)
                if (isinstance(f, str) or isinstance(f, tuple)) and 
                    ((isinstance(f, str) and (f.endswith(".mid") or f.endswith(".midi")) and not f.startswith("._")) or
                    (isinstance(f, tuple) and f[0].endswith((".mid", ".midi")) and not f[0].startswith("._")))
            ]

            init.deinit_sd()
            return True
        except OSError as e:
            init.init_display()
            print(f"Error initializing SD card: {e}")
            utils.alert_screen("No SD Card")
            
            # Return to the main menu.
            self.midi_file.current_page = ""
            parent_screen = self.midi_file.parent
            if parent_screen:
                init.menu.set_screen(parent_screen)
                init.menu.draw()
            return False

    def rotary_1(self, val):
        """
        Responds to rotation of encoder 1 for scrolling the file list.

        Parameters:
        ----------
        val : int
            The value from the rotary encoder.
        """
        direction = 1 if val > self.midi_file.last_rotary_1_value else -1
        self.midi_file.last_rotary_1_value = val

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
        utils.stop_scroll_task()
        self.midi_file.selected_file = self.midi_file.current_file_index + self.midi_file.file_cursor_position
        self.midi_file.track_cursor_position = 0
        self.midi_file.handlers["tracks"].draw()

    def switch_2(self):
        """
        Responds to presses of encoder 2 to go back.
        """
        utils.stop_scroll_task()
        # Clear all positioning so return visits start at the top of the list.
        self.midi_file.current_file_index = 0
        self.midi_file.file_cursor_position = 0
        self.midi_file.selected_file = None
        self.midi_file.selected_track = None
        # Return to the main menu.
        parent_screen = self.midi_file.parent
        if parent_screen:
            init.menu.set_screen(parent_screen)
            init.menu.draw()

    def switch_3(self):
        """
        Responds to presses of encoder 3 to play the selected MIDI file.
        """
        utils.stop_scroll_task()
        self.midi_file.selected_file = self.midi_file.current_file_index + self.midi_file.file_cursor_position
        file_path = init.SD_MOUNT_POINT + "/" + self.midi_file.file_list[self.midi_file.selected_file]
        self.midi_file.handlers["play"].draw(file_path)

