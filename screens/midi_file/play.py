"""
MicroPython Tesla Coil Controller (MPTCC)
by Cameron Prince
teslauniverse.com

screens/midi_file/play.py
Provides the MIDI playback functionality.
"""

import _thread
import time
import uasyncio as asyncio
from ...hardware.init import init
from ...lib.utils import midi_to_frequency, velocity_to_ontime, constrain
from ...lib.config import Config as config
import umidiparser

class MIDIFilePlay:
    def __init__(self, midi_file):
        super().__init__()
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
        self.output = self.init.output
        self.levels_updated = False

        # Read the default output level from the configuration.
        self.config = config.read_config()

        # Dynamically create rotary_X methods based on NUMBER_OF_COILS.
        for i in range(self.init.NUMBER_OF_COILS):
            setattr(self, f"rotary_{i + 1}", lambda direction, idx=i: self.rotary(idx, direction))

    def draw(self, file_path):
        """
        The main MIDI file playback function.
        """
        self.midi_file.current_page = "play"
        self.file_path = file_path

        # Show a loading message.
        self.display.loading_screen()

        # Set the active flag.
        self.playback_active = True

        # Load the .map file so we can determine which tracks are to be played.
        self.midi_file.load_map_file(self.file_path)

        # Update levels from the loaded map file.
        self.levels = self.midi_file.levels

        if not hasattr(self.midi_file, 'outputs') or all(output is None for output in self.midi_file.outputs):
            # Stop and return to file listing when the selected file has no
            # corresponding map file.
            self.playback_active = False
            self.display.alert_screen("No tracks mapped")
            self.midi_file.handlers["files"].draw()
            return

        self.init.sd_card_reader.init_sd()

        # Initialize start_time before updating the display
        self.start_time = time.ticks_us()
        self.last_display_update = time.ticks_ms()

        # Update the display with the initial elapsed time (00:00)
        self.display.clear()
        self.update_display()

        # Start playback in a separate thread.
        _thread.start_new_thread(self.player, (self.file_path,))

        # Start the update display, RGB LED, and playback monitor tasks.
        asyncio.create_task(self._update_display_task())
        asyncio.create_task(self._monitor_playback_end_task())

        if self.init.RGB_LED_ASYNCIO_POLLING:
            asyncio.create_task(self._update_rgb_led_task())

    def player(self, file_path):
        """
        Plays the MIDI events sequentially.
        """
        try:
            midi_file = umidiparser.MidiFile(file_path)
            
            for event in midi_file.play():
                if not self.playback_active:
                    break

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
                        pass

            self.playback_active = False
        except Exception as e:
            print(f"Error during playback: {e}")
            self.playback_active = False

    def update_display(self):
        """
        Updates the display with the elapsed time and levels.
        """
        if not self.playback_active:
            return

        # Update the elapsed time.
        self.current_time = time.ticks_us()
        self.elapsed_time = time.ticks_diff(self.current_time, self.start_time) // 1000000
        self.minutes = self.elapsed_time // 60
        self.seconds = self.elapsed_time % 60

        # Calculate the maximum number of columns that fit on the screen.
        level_text_width = len("1:100%") * self.display.DISPLAY_FONT_WIDTH  # Width of one level entry
        max_columns = self.display.DISPLAY_WIDTH // level_text_width  # Maximum columns per row

        # Calculate the number of rows needed to display all levels.
        num_rows = (self.init.NUMBER_OF_COILS + max_columns - 1) // max_columns

        # Calculate the height of the levels display area.
        levels_area_height = num_rows * self.display.DISPLAY_LINE_HEIGHT

        # Clear the time and levels area dynamically.
        self.display.fill_rect(0, 16, self.display.width, levels_area_height + 16, 0)

        # Update the time.
        self.display.header("PLAY MIDI FILE")
        self.display.text(f"Time: {self.minutes:02}:{self.seconds:02}", 0, 16, 1)

        # Update the levels in multiple columns, wrapping based on screen width.
        y_start = 32  # Starting Y position for the first row of levels
        y_increment = self.display.DISPLAY_LINE_HEIGHT  # Vertical spacing between rows

        for i in range(0, self.init.NUMBER_OF_COILS, max_columns):
            row_levels = self.levels[i:i + max_columns]
            level_text = " ".join(f"{i + j + 1}:{level:3d}%" for j, level in enumerate(row_levels))
            self.display.text(level_text, 0, y_start + (i // max_columns) * y_increment, 1)

        # Refresh the display.
        self.display.show()

    async def _update_display_task(self):
        """
        Asyncio task to update the display with elapsed time and levels during playback.
        """
        while self.playback_active:
            if self.levels_updated or time.ticks_diff(time.ticks_ms(), self.last_display_update) >= 1000:
                self.levels_updated = False
                self.update_display()
                self.last_display_update = time.ticks_ms()
            await asyncio.sleep(0.1)

    async def _update_rgb_led_task(self):
        """
        Asyncio task to update the RGB LEDs during playback.
        """
        while self.playback_active:
            for output, color in self.init.rgb_led_color.items():
                if color:
                    r, g, b = color
                    try:
                        self.init.rgb_led[output].setColor(r, g, b)
                    except Exception as e:
                        print(f"Error updating RGB LED {output}: {e}")
                    self.init.rgb_led_color[output] = None
            await asyncio.sleep(0.1)

    async def _monitor_playback_end_task(self):
        """
        Asyncio task to monitor playback_ended and call stop_playback() when it becomes True.
        """
        while True:
            if not self.playback_active:
                await self.stop_playback()
                break
            await asyncio.sleep(0.1)

    async def stop_playback(self):
        """
        Stop MIDI playback and clean up resources.
        """
        # Clear the RGB LED color dictionary.
        if self.init.RGB_LED_ASYNCIO_POLLING:
            self.init.rgb_led_color.clear()

        self.output.set_all_outputs()

        # Explicitly set all RGB LEDs to off.
        for rgb_led in self.init.rgb_led:
            try:
                rgb_led.off()
            except Exception as e:
                print(f"Error turning off RGB LED: {e}")

        if (self.save_levels or self.config.get("midi_file_save_levels_on_end")):
            # Save the current levels to the .map file.
            self.save_levels = False
            self.midi_file.levels = self.levels
            self.midi_file.save_map_file(self.file_path, False)

            # Display "Levels saved" message.
            self.display.clear()
            self.display.alert_screen("Levels saved")

        self.init.sd_card_reader.deinit_sd()

        # Return to the file listing.
        self.midi_file.handlers["files"].draw()

    def rotary(self, index, direction):
        """
        The common rotary method which updates the output levels array and signals the display update.
        """
        increment = 1
        new_level = self.levels[index] + increment * direction

        # Constrain the new level between 1 and 100.
        self.levels[index] = constrain(new_level, 1, 100)

        # Signal that the levels need to be updated.
        self.levels_updated = True

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
