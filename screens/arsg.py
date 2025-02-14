"""
MicroPython Tesla Coil Controller (MPTCC)
by Cameron Prince

screens/arsg.py
Provides functionality for the ARSG emulator.
"""

import _thread
import time
import uasyncio as asyncio
from mptcc.hardware.init import init
from mptcc.lib.menu import Screen
from mptcc.lib.config import Config as config
import mptcc.lib.utils as utils

class ARSG(Screen):
    """
    A class to handle the functionality of the ARSG emulator for the MPTCC.
    """

    def __init__(self, name):
        super().__init__(name)
        self.name = name
        self.init = init
        self.display = self.init.display
        self.font_width = self.display.DISPLAY_FONT_WIDTH
        self.init_settings()

    def init_settings(self):
        """
        Allows refreshing of settings each time the screen is drawn.
        """
        self.config = config.read_config()
        self.min_line_freq = self.config.get("arsg_min_line_freq", config.ARSG_MIN_LINE_FREQ_DEF)
        self.min_on_time = self.config.get("arsg_min_on_time", config.ARSG_MIN_ON_TIME_DEF)
        self.min_freq = self.config.get("arsg_min_freq", config.ARSG_MIN_FREQ_DEF)
        self.max_line_freq = self.config.get("arsg_max_line_freq", config.ARSG_MAX_LINE_FREQ_DEF)
        self.max_on_time = self.config.get("arsg_max_on_time", config.ARSG_MAX_ON_TIME_DEF)
        self.max_freq = self.config.get("arsg_max_freq", config.ARSG_MAX_FREQ_DEF)
        self.max_duty = self.config.get("arsg_max_duty", config.ARSG_MAX_DUTY_DEF)
        self.line_freq = self.min_line_freq
        self.on_time = self.min_on_time
        self.freq = self.min_freq
        self.ten_x = False
        self.active = False
        # Flag to toggle outputs at line frequency.
        self.enable = False
        self.settings_changed = True
        # Asyncio task for toggling the enable flag.
        self.enable_task = None
        # Thread for controlling outputs.
        self.output_thread = None
        self.output = self.init.output

    def draw(self):
        """
        Draws the initial ARSG emulator screen.
        """
        self.init_settings()
        self.display.clear()
        self.display.header(self.name)
        self.display.text("Line Freq:", 0, 16, 1)
        self.display.text("On Time:", 0, 28, 1)
        self.display.text("Freq:", 0, 40, 1)
        self.display.text("10x", 100, 56, 0)
        self.display.text("Active", 0, 56, 0)
        self.update_display(update_line_freq=True, update_on_time=True, update_freq=True, initial=True)

    def update_display(self, update_line_freq=False, update_on_time=False, update_freq=False, update_ten_x=False, update_active=False, initial=False):
        """
        Updates the display with the current settings.
        """
        max_chars = 5
        rect_width = max_chars * self.font_width

        if update_line_freq:
            line_freq_str = f"{self.line_freq}Hz"
            if not initial:
                self.display.fill_rect(self.display.width - rect_width, 16, rect_width, 10, 0)
            self.display.text(line_freq_str, self.display.width - len(line_freq_str) * self.font_width, 16, 1)

        if update_on_time:
            on_time_str = f"{self.on_time}us"
            if not initial:
                self.display.fill_rect(self.display.width - rect_width, 28, rect_width, 10, 0)
            self.display.text(on_time_str, self.display.width - len(on_time_str) * self.font_width, 28, 1)

        if update_freq:
            freq_str = f"{self.freq}Hz"
            if not initial:
                self.display.fill_rect(self.display.width - rect_width, 40, rect_width, 10, 0)
            self.display.text(freq_str, self.display.width - len(freq_str) * self.font_width, 40, 1)

        if update_ten_x:
            ten_x_x = self.display.width - len("10x") * self.font_width
            if self.ten_x:
                self.display.text("10x", ten_x_x, 56, 1)
            else:
                self.display.fill_rect(ten_x_x, 56, 3 * self.font_width, 16, 0)
        
        if update_active:
            if self.active:
                self.display.text("Active", 0, 56, 1)
            else:
                self.display.fill_rect(0, 56, 6 * self.font_width, 10, 0)
        
        self.display.show()

    async def toggle_enable_flag(self):
        """
        Toggles the enable flag at the line frequency.
        """
        while self.active:
            self.enable = not self.enable
            # Toggle at twice the line frequency.
            await asyncio.sleep(1 / (2 * self.line_freq))

    def output_control_thread(self):
        """
        The thread that controls the output, ensuring settings are applied.
        """
        while self.active:
            if self.settings_changed:
                self.enable_outputs()
                self.settings_changed = False
            elif self.enable:
                # Enable outputs if the enable flag is True.
                self.enable_outputs()
            else:
                # Disable outputs if the enable flag is False.
                self.output.set_all_outputs()
            # Small delay to avoid busy-waiting.
            time.sleep(0.01)
        self.output.set_all_outputs()
        self.settings_changed = True

    def enable_outputs(self):
        """
        Enables the outputs based on the current settings.
        """
        self.output.set_all_outputs(self.enable, self.freq, self.on_time, self.max_duty, self.max_on_time)

    def update_on_time(self):
        """
        Updates the on time to ensure it does not exceed the maximum allowed duty cycle or on-time.
        """
        self.on_time = utils.calculate_on_time(self.on_time, self.freq, self.max_duty, self.max_on_time)

    def rotary_1(self, direction):
        """
        Handles the first rotary encoder input to adjust the line frequency.
        """
        increment = 1 if not self.ten_x else 10
        new_line_freq = self.line_freq + increment * direction
        self.line_freq = max(self.min_line_freq, min(self.max_line_freq, new_line_freq))
        self.update_display(update_line_freq=True)
        self.settings_changed = True

    def rotary_2(self, direction):
        """
        Handles the second rotary encoder input to adjust the on time.
        """
        increment = 1 if not self.ten_x else 10
        new_on_time = self.on_time + increment * direction
        self.on_time = max(self.min_on_time, min(new_on_time, self.max_on_time))
        self.update_on_time()
        self.update_display(update_on_time=True)
        self.settings_changed = True

    def rotary_3(self, direction):
        """
        Handles the third rotary encoder input to adjust the frequency.
        """
        increment = 1 if not self.ten_x else 10
        new_freq = self.freq + increment * direction
        self.freq = max(self.min_freq, min(self.max_freq, new_freq))
        self.update_on_time()
        self.update_display(update_freq=True)
        self.settings_changed = True

    def switch_2(self):
        """
        Handles the second switch input to deactivate the ARSG emulator and return to the parent screen.
        """
        self.active = False
        parent_screen = self.parent
        if parent_screen:
            self.init.menu.set_screen(parent_screen)
            self.init.menu.draw()

    def switch_3(self):
        """
        Handles the third switch input to toggle the active state of the ARSG emulator.
        """
        self.active = not self.active
        if self.active:
            if not self.output_thread:
                self.output_thread = _thread.start_new_thread(self.output_control_thread, ())
            if not self.enable_task:
                self.enable_task = asyncio.create_task(self.toggle_enable_flag())
        else:
            if self.enable_task:
                self.enable_task.cancel()
                self.enable_task = None
            if self.output_thread:
                self.output_thread = None
        self.update_display(update_active=True)

    def switch_4(self):
        """
        Handles the fourth switch input to toggle the 10x mode.
        """
        self.ten_x = not self.ten_x
        self.update_display(update_ten_x=True)
