"""
MicroPython Tesla Coil Controller (MPTCC)
by Cameron Prince

screens/midi_file/play.py
Provides the MIDI playback functionality.
"""

from mptcc.init import init
import mptcc.lib.utils as utils
import _thread
import gc
import time
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
        self.levels = [50] * 4
        self.events = []
        self.val_old = [0, 0, 0, 0]
        self.playback_active = False

    def draw(self, file_path):
        """
        The main MIDI file playback function.

        Parameters:
        ----------
        file_path : str
            The path to the MIDI file.
        """
        self.midi_file.current_page = "play"

        # Show a loading message.
        utils.loading_screen()

        self.playback_active = True

        # Load the .map file so we can determine which tracks are to be played.
        self.midi_file.load_map_file(file_path)

        if not hasattr(self.midi_file, 'outputs') or all(output is None for output in self.midi_file.outputs):
            # Stop and return to file listing when the selected file has no corresponding map file.
            self.playback_active = False
            utils.alert_screen("No tracks mapped")
            self.midi_file.handlers["files"].draw()
            return

        # Initialize the SD card reader so we can read the MIDI file.
        init.init_sd()

        # Parse the MIDI file and prepare the events array.
        midi = umidiparser.MidiFile(file_path, buffer_size=0, reuse_event_object=False)
        init.deinit_sd()

        # Create a list of track indices from the outputs array and adjust by +1.
        # This skips the metadata track.
        track_indices = [track_index + 1 for track_index in self.midi_file.outputs if track_index is not None]

        for track_index in track_indices:
            current_time = 0
            for event in midi.tracks[track_index]:
                if event.status in (umidiparser.NOTE_ON, umidiparser.NOTE_OFF):
                    current_time += event.delta_us / 1e6
                    self.events.append((current_time, track_index, event))

        # Sort the events by time.
        self.events.sort(key=lambda x: x[0])

        if not self.events:
            self.playback_active = False
            utils.alert_screen("No MIDI events found")
            return

        # Start playback in a separate thread.
        _thread.start_new_thread(self.midi_events_handler, ())

    def midi_events_handler(self):
        """
        Plays the MIDI events sequentially and updates the display with elapsed time.
        """
        try:
            start_time = time.ticks_us()
            display_update_interval = 1
            last_display_update = time.ticks_ms()

            # Ensure the display is populated as soon as playback begins.
            self.update_elapsed_time(start_time)
            
            while self.playback_active and self.events:
                current_time = time.ticks_us()
                elapsed_time = time.ticks_diff(current_time, start_time) / 1e6

                if elapsed_time >= self.events[0][0]:
                    event_time, track, event = self.events.pop(0)

                    if track - 1 in self.midi_file.outputs:
                        output = self.midi_file.outputs.index(track - 1)

                        if event.status == umidiparser.NOTE_ON:
                            note = event.note
                            velocity = event.velocity
                            if velocity == 0:
                                utils.set_output(output, 0, 0, False)
                            else:
                                frequency = utils.midi_to_frequency(note)
                                on_time = utils.velocity_to_ontime(velocity)
                                # Scale the on_time by the level control percentage.
                                scaled_on_time = int(on_time * self.levels[output] / 100)
                                utils.set_output(output, int(frequency), scaled_on_time, True)
                        elif event.status == umidiparser.NOTE_OFF:
                            utils.set_output(output, 0, 0, False)
                    else:
                        print(f"Warning: No output mapped for track {track}")

                if time.ticks_diff(time.ticks_ms(), last_display_update) >= display_update_interval * 1000:
                    self.update_elapsed_time(start_time)
                    last_display_update = time.ticks_ms()

                time.sleep(0.01)

            self.stop_playback()
        except Exception as e:
            print(f"Exception: {e}")

    def update_elapsed_time(self, start_time):
        """
        Updates the elapsed time and output level values.

        Parameters:
        ----------
        start_time : int
            The start time in microseconds.
        """
        # Check if playback is active before updating the display.
        if not self.playback_active:
            return

        current_time = time.ticks_us()
        elapsed_time = time.ticks_diff(current_time, start_time) // 1000000
        minutes = elapsed_time // 60
        seconds = elapsed_time % 60

        # Clear only the areas that need to be updated.
        init.display.fill_rect(0, 16, 128, 16, 0)
        init.display.fill_rect(0, 32, 128, 32, 0)

        # Update the time and levels.
        utils.header("PLAY MIDI FILE")
        init.display.text(f"Time: {minutes:02}:{seconds:02}", 0, 16)
        init.display.text(f"1:{self.levels[0]:3d}%  2:{self.levels[1]:3d}%", 0, 32)
        init.display.text(f"3:{self.levels[2]:3d}%  4:{self.levels[3]:3d}%", 0, 48)
        init.display.show()

    def stop_playback(self):
        """
        Stop MIDI playback and return to the file listing.
        """
        self.playback_active = False

        utils.disable_outputs()

        # Clear events.
        self.events = []

        # Force garbage collection to free up memory.
        gc.collect()

        # Return to the file listing.
        # self.midi_file.handlers["files"].draw()

        self.midi_file.current_page = ""
        parent_screen = self.midi_file.parent
        if parent_screen:
            init.menu.set_screen(parent_screen)
            init.menu.draw()

    def update_levels(self):
        """
        Updates the display with the current levels of channels 1 to 4.
        """
        # Clear only the areas that need to be updated.
        init.display.fill_rect(0, 32, 128, 32, 0)

        # Update the levels.
        init.display.text(f"1:{self.levels[0]:3d}%  2:{self.levels[1]:3d}%", 0, 32)
        init.display.text(f"3:{self.levels[2]:3d}%  4:{self.levels[3]:3d}%", 0, 48)
        init.display.show()

    def rotary(self, index, val):
        """
        The common rotary method which updates the output levels array and prints debug information.

        Parameters:
        ----------
        index : int
            The index of the output to adjust.
        val : int
            The new value from the rotary encoder.
        """
        increment = 1
        new_level = self.levels[index] + increment * (val - self.val_old[index])
        self.levels[index] = max(0, min(100, new_level))
        self.val_old[index] = val
        self.update_levels()

    def rotary_1(self, val):
        self.rotary(0, val)

    def rotary_2(self, val):
        self.rotary(1, val)

    def rotary_3(self, val):
        self.rotary(2, val)

    def rotary_4(self, val):
        self.rotary(3, val)

    # All switches act as stop buttons.
    def switch_1(self):
        self.playback_active = False

    def switch_2(self):
        self.playback_active = False

    def switch_3(self):
        self.playback_active = False

    def switch_4(self):
        self.playback_active = False