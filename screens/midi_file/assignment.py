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
        output_selection : int or None
            Output assignment selection for display purposes.
        """
        self.midi_file = midi_file
        self.output_selection = None
        self.init = init
        self.display = self.init.display

    def draw(self):
        """
        Displays the track-to-output assignment page and sets the output value based on the map file.
        """
        self.midi_file.current_page = "assignment"

        # Initialize output_selection.
        self.output_selection = None
        for i, track in enumerate(self.midi_file.outputs):
            if track == self.midi_file.selected_track:
                self.output_selection = i + 1
                break

        self.display.clear()
        self.display.header("Track Assignment")

        available_height = init.display.height - self.midi_file.header_height
        total_text_height = self.midi_file.font_height * 2
        total_spacing = available_height - total_text_height
        track_y = self.midi_file.header_height + total_spacing // 3
        self.midi_file.output_y = track_y + self.midi_file.font_height + total_spacing // 3

        # Use a generator expression to find the selected track.
        track_generator = (track for track in self.midi_file.track_list if track["original_index"] == self.midi_file.selected_track)

        # Use next to get the first matching track, or handle StopIteration if no match is found.
        try:
            selected_track_info = next(track_generator)
        except StopIteration:
            selected_track_info = None

        if selected_track_info:
            full_track_name = selected_track_info["name"]
        else:
            full_track_name = "Unknown Track"

        # Handle scrolling for the track name if it's too long.
        text_width = len(full_track_name) * self.midi_file.font_width
        if text_width > self.display.width:
            # Pass the track index as the unique identifier.
            start_scroll(self.display, full_track_name, track_y, self.midi_file.selected_track, background_color=0)
        else:
            # If the text doesn't require scrolling, display it normally (inactive color).
            self.display.fill_rect(0, track_y, self.display.width, self.midi_file.line_height, 0)  # Clear the line.
            self.display.center_text(full_track_name, track_y)

        self.update_output_value()

    def update_output_value(self):
        """
        Updates the assignment values on the display without clearing the entire screen.
        """
        self.display.fill_rect(0, self.midi_file.output_y, self.display.width, self.midi_file.line_height, 0)

        output_value = self.output_selection
        output_text = "None" if output_value is None else str(output_value)
        self.display.center_text(f"Output: {output_text}", self.midi_file.output_y)
        self.display.show()

    def rotary_1(self, direction):
        """
        Responds to the rotation of encoder 1 for cycling through output values.

        Parameters:
        ----------
        direction : int
            The direction of rotation (1 for clockwise, -1 for counterclockwise).
        """
        # Calculate the new output index.
        if self.output_selection is None:
            new_output = -1
        else:
            new_output = self.output_selection - 1

        new_output += direction

        # Ensure new_output cycles within the range of -1 to (NUMBER_OF_COILS - 1).
        if new_output > (self.init.NUMBER_OF_COILS - 1):
            new_output = -1
        if new_output < -1:
            new_output = (self.init.NUMBER_OF_COILS - 1)

        self.output_selection = new_output + 1 if new_output != -1 else None
        self.update_output_value()

    def switch_1(self):
        """
        Responds to presses of encoder 1 to save the output assignment and go back.
        """
        if self.output_selection is not None:
            output_index = self.output_selection - 1
        else:
            output_index = None

        # Clear any existing assignment for the selected track.
        for i, track in enumerate(self.midi_file.outputs):
            if track == self.midi_file.selected_track and i != output_index:
                self.midi_file.outputs[i] = None

        # Assign the new output to the selected track.
        if output_index is not None:
            self.midi_file.outputs[output_index] = self.midi_file.selected_track

        file_path = self.init.SD_CARD_READER_MOUNT_POINT + "/" + self.midi_file.file_list[self.midi_file.selected_file]

        # Save the updated output assignments to the map file.
        self.midi_file.save_map_file(file_path)

        # Return to the track listing.
        stop_scroll(self.display)
        self.midi_file.handlers["tracks"].draw()

    def switch_2(self):
        """
        Responds to presses of encoder 2 to go back.
        """
        stop_scroll(self.display)
        self.midi_file.handlers["tracks"].draw()
