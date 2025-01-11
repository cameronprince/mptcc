"""
MicroPython Tesla Coil Controller (MPTCC)
by Cameron Prince
teslauniverse.com

screens/midi_file/assignment.py
Provides the track assignment screen.
"""

from mptcc.init import init
import mptcc.utils as utils

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

        init.display.fill(0)

        available_height = init.display.height - self.midi_file.header_height
        total_text_height = self.midi_file.font_height * 2
        total_spacing = available_height - total_text_height
        track_y = self.midi_file.header_height + total_spacing // 3
        self.midi_file.output_y = track_y + self.midi_file.font_height + total_spacing // 3
        full_track_name = self.midi_file.track_list[self.midi_file.selected_track]

        utils.truncate_text(full_track_name, track_y, center=True)
        self.update_output_value()

    def update_output_value(self):
        """
        Updates the assignment values on the display without clearing the entire screen.
        """
        init.display.fill_rect(0, self.midi_file.output_y, init.display.width, self.midi_file.line_height, 0)

        output_value = self.output_selection
        output_text = "None" if output_value is None else str(output_value)
        utils.center_text(f"Output: {output_text}", self.midi_file.output_y)
        init.display.show()

    def rotary_1(self, val):
        """
        Responds to the rotation of encoder 1 for cycling through output values.

        Parameters:
        ----------
        val : int
            The value from the rotary encoder.
        """
        direction = 1 if val > self.midi_file.last_rotary_1_value else -1
        self.midi_file.last_rotary_1_value = val

        # Calculate the new output index.
        if self.output_selection is None:
            new_output = -1
        else:
            new_output = self.output_selection - 1

        new_output += direction

        # Ensure new_output cycles within the range of -1 to 3 (for "None" and four outputs).
        if new_output > 3:
            new_output = -1
        if new_output < -1:
            new_output = 3

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

        # Save the updated output assignments to the map file.
        self.midi_file.save_map_file()
        # Return to the track listing.
        self.midi_file.handlers["tracks"].draw()

    def switch_2(self):
        """
        Responds to presses of encoder 2 to go back.
        """
        self.midi_file.handlers["tracks"].draw()