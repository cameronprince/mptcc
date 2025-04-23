"""
MicroPython Tesla Coil Controller (MPTCC)
by Cameron Prince
teslauniverse.com

screens/midi_file/assignment.py
Provides the track assignment screen.
"""

from ...hardware.init import init
from ...hardware.display.tasks import start_scroll, stop_scroll


class MIDIFileAssignment:
    def __init__(self, midi_file):
        """
        Initialize the assignment handler with the MIDIFile instance.

        Parameters:
        ----------
        midi_file : MIDIFile
            The parent MIDIFile instance.
        """
        self.midi_file = midi_file
        self.init = init
        self.display = self.init.display
        self.cursor_position = 0  # Cursor offset within visible rows.
        self.current_coil_index = 0  # Start index of visible coil list.
        self.per_page = 2  # Number of coils displayed per page (matches display capacity).
        self.coil_count = self.init.NUMBER_OF_COILS  # Total number of coils.
        self.selected_coils = set()  # Set of coils assigned to the current track.

    def draw(self):
        """
        Displays the track-to-coil assignment page with a scrollable list of coils.
        """
        self.midi_file.current_page = "assignment"

        # Load current assignments for the selected track.
        self.selected_coils = set()
        for i, track in enumerate(self.midi_file.outputs):
            if track == self.midi_file.selected_track:
                self.selected_coils.add(i)

        self.display.clear()
        self.display.header("Coil Assignment")

        # Calculate layout.
        available_height = self.display.height - self.midi_file.header_height
        total_text_height = self.midi_file.font_height * 2
        total_spacing = available_height - total_text_height
        track_y = self.midi_file.header_height + total_spacing // 3
        self.list_y = track_y + self.midi_file.font_height + total_spacing // 3

        # Display track name.
        track_generator = (track for track in self.midi_file.track_list if track["original_index"] == self.midi_file.selected_track)
        try:
            selected_track_info = next(track_generator)
            full_track_name = selected_track_info["name"]
        except StopIteration:
            full_track_name = "Unknown Track"

        text_width = len(full_track_name) * self.midi_file.font_width
        if text_width > self.display.width:
            start_scroll(self.display, full_track_name, track_y, self.midi_file.selected_track, background_color=0)
        else:
            self.display.fill_rect(0, track_y, self.display.width, self.midi_file.line_height, 0)
            self.display.center_text(full_track_name, track_y)

        # Draw the coil list.
        self.update_coil_list()

    def update_coil_list(self):
        """
        Updates the coil list display, showing checkboxes for each coil with consistent cursor style.
        """
        # Clear the list area.
        self.display.fill_rect(0, self.list_y, self.display.width, self.display.height - self.list_y, 0)

        # Determine the range of coils to display.
        start_index = self.current_coil_index
        end_index = min(self.coil_count, start_index + self.per_page)

        # Display each coil with a checkbox.
        for i in range(start_index, end_index):
            coil_index = i
            y_position = self.list_y + (i - start_index) * self.midi_file.line_height
            checkbox = "[x]" if coil_index in self.selected_coils else "[ ]"
            text = f"Coil {coil_index + 1:2d}: {checkbox}"  # Two-digit formatting.
            is_active = (i == self.current_coil_index + self.cursor_position)
            background = int(is_active)  # 1 for active (green), 0 for inactive (black).
            v_padding = int((self.midi_file.line_height - self.midi_file.font_height) / 2)

            # Draw the row.
            self.display.fill_rect(0, y_position, self.display.width, self.midi_file.line_height, background)
            self.display.text(text, 0, y_position + v_padding, not is_active)  # 0 (black) for active, 1 (green) for inactive.

            # Handle scrolling for the active item.
            if is_active:
                text_width = len(text) * self.midi_file.font_width
                if text_width > self.display.width:
                    start_scroll(self.display, text, y_position, coil_index, background_color=background)
                else:
                    stop_scroll(self.display)
                    # Redraw to ensure no scroll artifacts.
                    self.display.fill_rect(0, y_position, self.display.width, self.midi_file.line_height, background)
                    self.display.text(text, 0, y_position + v_padding, not is_active)

        self.display.show()

    def rotary_1(self, direction):
        """
        Responds to the rotation of encoder 1 to scroll through the coil list.

        Parameters:
        ----------
        direction : int
            The direction of rotation (1 for clockwise, -1 for counterclockwise).
        """
        new_position = self.current_coil_index + self.cursor_position + direction

        # Check if the new position is within valid bounds.
        if 0 <= new_position < self.coil_count:
            self.cursor_position += direction
            # Adjust cursor and index to keep cursor within visible rows.
            if self.cursor_position >= self.per_page:
                self.current_coil_index += 1
                self.cursor_position = self.per_page - 1
            if self.cursor_position < 0:
                self.current_coil_index -= 1
                self.cursor_position = 0
            if self.current_coil_index + self.per_page > self.coil_count:
                self.current_coil_index = max(0, self.coil_count - self.per_page)

            # Refresh the display.
            self.update_coil_list()

    def switch_1(self):
        """
        Responds to presses of encoder 1 to toggle coil assignment and update the map file.
        """
        coil_index = self.current_coil_index + self.cursor_position

        # Toggle the coil's assignment.
        if coil_index in self.selected_coils:
            self.selected_coils.remove(coil_index)
            self.midi_file.outputs[coil_index] = None
        else:
            # Check if the coil is assigned to another track.
            if self.midi_file.outputs[coil_index] is not None:
                # Clear the coil from the other track.
                self.midi_file.outputs[coil_index] = None
            # Assign the coil to the current track.
            self.selected_coils.add(coil_index)
            self.midi_file.outputs[coil_index] = self.midi_file.selected_track

        # Save the updated assignments to the map file.
        file_path = self.init.sd_card_reader.mount_point + "/" + self.midi_file.file_list[self.midi_file.selected_file]
        self.midi_file.save_map_file(file_path)

        # Update the display.
        self.update_coil_list()

    def switch_2(self):
        """
        Responds to presses of encoder 2 to go back to the track listing.
        """
        stop_scroll(self.display)
        self.midi_file.handlers["tracks"].draw()
