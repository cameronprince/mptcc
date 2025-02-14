"""
MicroPython Tesla Coil Controller (MPTCC)
by Cameron Prince
teslauniverse.com

screens/midi_file/play.py
Provides the MIDI playback functionality.
"""

import _thread
import time
from mptcc.hardware.init import init
from mptcc.lib.utils import midi_to_frequency, velocity_to_ontime
from mptcc.lib.config import Config as config
import umidiparser

class MIDIFilePlay:
    def __init__(self, midi_file):
        """
        Initialize the MIDI playback handler with the MIDIFile instance.

        Parameters:
        ----------
        midi_file : MIDIFile
            The parent MIDIFile instance.
        """
        self.midi_file = midi_file
        self.events = []
        self.playback_active = False
        self.init = init
        self.display = self.init.display
        self.save_levels = False
        self.file_path = None

        self.current_time = 0
        self.elapsed_time = 0
        self.minutes = 0
        self.seconds = 0
        self.start_time = 0
        self.last_display_update = 0

        # Read the default output level from the configuration.
        self.config = config.read_config()

        # Add a mutex for thread-safe display updates.
        self.display_mutex = _thread.allocate_lock()

    def draw(self, file_path):
        """
        The main MIDI file playback function.

        Parameters:
        ----------
        file_path : str
            The path to the MIDI file.
        """
        self.midi_file.current_page = "play"

        self.file_path = file_path

        # Show a loading message.
        self.display.loading_screen()
        self.display.clear()

        self.playback_active = True

        # Load the .map file so we can determine which tracks are to be played.
        self.midi_file.load_map_file(self.file_path)

        # Update levels from the loaded map file
        self.levels = self.midi_file.levels

        if not hasattr(self.midi_file, 'outputs') or all(output is None for output in self.midi_file.outputs):
            # Stop and return to file listing when the selected file has no
            # corresponding map file.
            self.playback_active = False
            self.display.alert_screen("No tracks mapped")
            self.midi_file.handlers["files"].draw()
            return

        self.init.sd_card_reader.init_sd()

        # Start playback in a separate thread.
        _thread.start_new_thread(self.player, (self.file_path,))

    def player(self, file_path):
        """
        Plays the MIDI events sequentially and updates the display with elapsed time.
        """
        try:
            self.start_time = time.ticks_us()
            self.last_display_update = time.ticks_ms()

            # Show the initial screen values prior to playback start.
            self.update_levels()
            self.update_elapsed_time()

            midi_file = umidiparser.MidiFile(file_path)
            
            for event in midi_file.play():
                if not self.playback_active:
                    break

                # Update the display every second.
                current_time_ms = time.ticks_ms()
                if time.ticks_diff(current_time_ms, self.last_display_update) >= 1000:
                    self.update_elapsed_time()
                    self.last_display_update = current_time_ms

                if event.status in (umidiparser.NOTE_ON, umidiparser.NOTE_OFF):
                    track_index = event.track
                    if track_index in self.midi_file.outputs:
                        output = self.midi_file.outputs.index(track_index)
                        if event.status == umidiparser.NOTE_ON:
                            note = event.note
                            velocity = event.velocity
                            if velocity == 0:
                                self.init.output.set_output(output, False)
                            else:
                                frequency = midi_to_frequency(note)
                                on_time = velocity_to_ontime(velocity)
                                # Scale the on_time by the level control percentage.
                                scaled_on_time = int(on_time * self.levels[output] / 100)
                                self.init.output.set_output(output, True, frequency, scaled_on_time)
                        elif event.status == umidiparser.NOTE_OFF:
                            self.init.output.set_output(output, False)
                    else:
                        # print(f"Warning: No output mapped for track {event.track}")
                        pass

            self.stop_playback()
        except Exception as e:
            print(f"Exception: {e}")
            self.stop_playback()

    def update_elapsed_time(self):
        """
        Updates the elapsed time display during MIDI playback.
        """
        # Check if playback is active before updating the display.
        if not self.playback_active:
            return

        # Acquire the display mutex to ensure thread-safe updates.
        self.display_mutex.acquire()
        try:
            self.current_time = time.ticks_us()
            self.elapsed_time = time.ticks_diff(self.current_time, self.start_time) // 1000000
            self.minutes = self.elapsed_time // 60
            self.seconds = self.elapsed_time % 60

            # Clear only the area that needs to be updated.
            self.display.fill_rect(0, 16, 128, 16, 0)

            # Update the time.
            self.display.header("PLAY MIDI FILE")
            self.display.text(f"Time: {self.minutes:02}:{self.seconds:02}", 0, 16, 1)
            self.display.show()
        finally:
            # Release the mutex to allow other threads to update the display.
            self.display_mutex.release()

    def stop_playback(self):
        """
        Stop MIDI playback and return to the file listing.
        """
        self.playback_active = False
        self.output.set_all_outputs()

        if (self.save_levels or self.config.get("midi_file_save_levels_on_end")):
            # Save the current levels to the .map file
            self.save_levels = False
            self.midi_file.levels = self.levels
            self.midi_file.save_map_file(self.file_path, False)

            # Display "Levels saved" message
            self.display.clear()
            self.display.alert_screen("Levels saved")

        self.init.sd_card_reader.deinit_sd()

        # Return to the file listing.
        self.midi_file.handlers["files"].draw()

    def update_levels(self):
        """
        Updates the display with the current levels of channels 1 to 4.
        """
        # Acquire the display mutex to ensure thread-safe updates.
        self.display_mutex.acquire()
        try:
            # Clear only the areas that need to be updated.
            self.display.fill_rect(0, 32, 128, 32, 0)

            # Update the levels.
            self.display.text(f"1:{self.levels[0]:3d}%  2:{self.levels[1]:3d}%", 0, 32, 1)
            self.display.text(f"3:{self.levels[2]:3d}%  4:{self.levels[3]:3d}%", 0, 48, 1)
            self.display.show()
        finally:
            # Release the mutex to allow other threads to update the display.
            self.display_mutex.release()

    def rotary(self, index, direction):
        """
        The common rotary method which updates the output levels array and prints debug information.

        Parameters:
        ----------
        index : int
            The index of the output to adjust.
        direction : int
            The direction of rotation (1 for clockwise, -1 for counterclockwise).
        """
        increment = 1
        new_level = self.levels[index] + increment * direction

        # Constrain the new level between 1 and 100.
        self.levels[index] = max(1, min(100, new_level))

        # Update the levels display.
        self.update_levels()

    def rotary_1(self, direction):
        self.rotary(0, direction)

    def rotary_2(self, direction):
        self.rotary(1, direction)

    def rotary_3(self, direction):
        self.rotary(2, direction)

    def rotary_4(self, direction):
        self.rotary(3, direction)

    # All switches act as stop buttons.
    def switch_1(self):
        self.save_levels = True
        self.playback_active = False

    def switch_2(self):
        self.playback_active = False

    def switch_3(self):
        self.playback_active = False

    def switch_4(self):
        self.playback_active = False
