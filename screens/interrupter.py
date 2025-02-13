"""
MicroPython Tesla Coil Controller (MPTCC)
by Cameron Prince

screens/interrupter.py
Provides functionality for the standard interrupter.
"""

import _thread
import time
from mptcc.hardware.init import init
from mptcc.lib.menu import CustomItem
from mptcc.lib.config import Config as config
import mptcc.lib.utils as utils

class Interrupter(CustomItem):
    """
    A class to handle the functionality of the standard interrupter for the MPTCC.
    """

    def __init__(self, name):
        super().__init__(name)
        self.init = init
        self.display = self.init.display
        self.font_width = self.display.DISPLAY_FONT_WIDTH
        self.init_settings()

    def init_settings(self):
        """
        Allows refreshing of settings each time the screen is drawn.
        """
        self.config = config.read_config()
        self.min_on_time = self.config.get("interrupter_min_on_time", config.INTERRUPTER_MIN_ON_TIME_DEF)
        self.min_freq = self.config.get("interrupter_min_freq", config.INTERRUPTER_MIN_FREQ_DEF)
        self.max_on_time = self.config.get("interrupter_max_on_time", config.INTERRUPTER_MAX_ON_TIME_DEF)
        self.max_freq = self.config.get("interrupter_max_freq", config.INTERRUPTER_MAX_FREQ_DEF)
        self.max_duty = self.config.get("interrupter_max_duty", config.INTERRUPTER_MAX_DUTY_DEF)
        self.freq = self.min_freq
        self.on_time = self.min_on_time
        self.ten_x = False
        self.active = False
        self.thread = None
        self.settings_changed = True
        self.output = self.init.output

    def draw(self):
        """
        Draws the initial interrupter screen.
        """
        self.init_settings()
        self.display.clear()
        self.display.header("Interrupter")
        self.display.text("On Time:", 0, 16, 1)
        self.display.text("Freq:", 0, 28, 1)
        self.display.text("10x", 100, 56, 0)
        self.display.text("Active", 0, 56, 0)
        self.update_display(update_on_time=True, update_frequency=True, initial=True)

    def update_display(self, update_on_time=True, update_frequency=True, update_ten_x=False, update_active=False, initial=False):
        """
        Updates the display with the current settings.
        """
        max_chars = 5
        rect_width = max_chars * self.font_width

        if update_on_time:
            on_time_str = f"{self.on_time}us"
            if not initial:
                self.display.fill_rect(self.display.width - rect_width, 16, rect_width, 10, 0)
            self.display.text(on_time_str, self.display.width - len(on_time_str) * self.font_width, 16, 1)

        if update_frequency:
            freq_str = f"{self.freq}Hz"
            if not initial:
                self.display.fill_rect(self.display.width - (max_chars + 1) * self.font_width, 28, (max_chars + 1) * self.font_width, 10, 0)
            self.display.text(freq_str, self.display.width - len(freq_str) * self.font_width, 28, 1)

        if update_ten_x:
            ten_x_x = self.display.width - len("10x") * self.font_width
            if self.ten_x:
                self.display.text("10x", ten_x_x, 56, 1)
            else:
                self.display.fill_rect(ten_x_x, 56, 3 * self.font_width, 10, 0)
        
        if update_active:
            if self.active:
                self.display.text("Active", 0, 56, 1)
            else:
                self.display.fill_rect(0, 56, 6 * self.font_width, 10, 0)
        
        self.display.show()

    def set_all_outputs(self):
        """
        Enables the outputs based on the current settings.
        """
        self.output.set_all_outputs(self.active, self.freq, self.on_time, self.max_duty, self.max_on_time)

    def output_control_thread(self):
        """
        The thread that controls the output, ensuring settings are applied.
        """
        while self.active:
            if self.settings_changed:
                self.set_all_outputs()
                self.settings_changed = False
            time.sleep(0.1)
        self.output.disable_outputs()
        self.settings_changed = True

    def update_on_time(self):
        """
        Updates the duty cycle based on the current on time and frequency.
        """
        self.on_time = utils.calculate_on_time(self.on_time, self.freq, self.max_duty, self.max_on_time)

    def rotary_1(self, direction):
        """
        Handles the first rotary encoder input to adjust the on time.
        """
        increment = 10 if self.ten_x else 1

        new_on_time = self.on_time + increment * direction
        max_on_time = utils.calculate_max_on_time(self.freq, self.max_duty, self.max_on_time)

        if new_on_time < self.min_on_time:
            if self.on_time == self.min_on_time:
                return
        elif new_on_time > max_on_time:
            if self.on_time == max_on_time:
                return

        self.on_time = max(self.min_on_time, min(max_on_time, int(new_on_time)))
        self.update_on_time()
        self.update_display(update_on_time=True, update_frequency=False)
        self.settings_changed = True

    def rotary_2(self, direction):
        """
        Handles the second rotary encoder input to adjust the frequency.
        """
        increment = 10 if self.ten_x else 1

        new_freq = self.freq + increment * direction

        if new_freq < self.min_freq:
            if self.freq == self.min_freq:
                return
        elif new_freq > self.max_freq:
            if self.freq == self.max_freq:
                return

        max_on_time = utils.calculate_max_on_time(new_freq, self.max_duty, self.max_on_time)
        self.freq = max(self.min_freq, min(self.max_freq, new_freq))
        self.update_on_time()
        self.update_display(update_on_time=True, update_frequency=True)
        self.settings_changed = True

    def switch_2(self):
        """
        Handles the second switch input to deactivate the interrupter and return to the parent screen.
        """
        self.active = False
        self.output.disable_outputs()
        parent_screen = self.parent
        if parent_screen:
            self.init.menu.set_screen(parent_screen)
            self.init.menu.draw()

    def switch_3(self):
        """
        Handles the third switch input to toggle the active state of the interrupter.
        """
        self.active = not self.active
        max_on_time = utils.calculate_max_on_time(self.freq, self.max_duty, self.max_on_time)
        self.on_time = min(self.on_time, max_on_time)
        self.update_on_time()
        self.update_display(update_on_time=True, update_frequency=True, update_active=True)

        if self.active:
            if not self.thread:
                self.thread = _thread.start_new_thread(self.output_control_thread, ())
        else:
            self.thread = None

    def switch_4(self):
        """
        Handles the fourth switch input to toggle the 10x mode.
        """
        self.ten_x = not self.ten_x
        self.update_display(update_on_time=False, update_frequency=False, update_ten_x=True)
