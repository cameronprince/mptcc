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
    def __init__(self, name):
        super().__init__(name)
        self.init = init
        self.display = self.init.display
        self.config = config.read_config()

        self.min_on_time = self.config.get("interrupter_min_on_time", config.DEF_INTERRUPTER_MIN_ON_TIME)
        self.min_freq = self.config.get("interrupter_min_freq", config.DEF_INTERRUPTER_MIN_FREQ)
        self.max_on_time = self.config.get("interrupter_max_on_time", config.DEF_INTERRUPTER_MAX_ON_TIME)
        self.max_freq = self.config.get("interrupter_max_freq", config.DEF_INTERRUPTER_MAX_FREQ)
        self.max_duty = self.config.get("interrupter_max_duty", config.DEF_INTERRUPTER_MAX_DUTY)

        self.frequency = self.min_freq
        self.on_time = self.min_on_time
        self.font_width = self.display.DISPLAY_FONT_WIDTH
        self.ten_x = False
        self.active = False
        self.val_old = [0, 0]
        self.banned_frequencies = self.init.BANNED_INTERRUPTER_FREQUENCIES
        self.thread = None
        self.settings_changed = True

    def draw(self):
        self.display.clear()
        self.display.header("Interrupter")
        self.display.text("On Time:", 0, 20, 1)
        self.display.text("Freq:", 0, 30, 1)
        self.display.text("10x", 100, 50, 0)
        self.display.text("Active", 0, 50, 0)
        self.update_display(update_on_time=True, update_frequency=True, initial=True)

    def update_display(self, update_on_time=True, update_frequency=True, update_ten_x=False, update_active=False, initial=False):
        max_chars = 5
        rect_width = max_chars * self.font_width

        if update_on_time:
            on_time_str = f"{self.on_time}us"
            if not initial:
                self.display.fill_rect(self.display.width - rect_width, 20, rect_width, 10, 0)
            self.display.text(on_time_str, self.display.width - len(on_time_str) * self.font_width, 20, 1)
        
        if update_frequency:
            freq_str = f"{self.frequency}Hz"
            if not initial:
                self.display.fill_rect(self.display.width - (max_chars + 1) * self.font_width, 30, (max_chars + 1) * self.font_width, 10, 0)
            self.display.text(freq_str, self.display.width - len(freq_str) * self.font_width, 30, 1)
        
        if update_ten_x:
            if self.ten_x:
                self.display.text("10x", 100, 50, 1)
            else:
                self.display.fill_rect(100, 50, 3 * self.font_width, 10, 0)
        
        if update_active:
            if self.active:
                self.display.text("Active", 0, 50, 1)
            else:
                self.display.fill_rect(0, 50, 6 * self.font_width, 10, 0)
        
        self.display.show()

    def enable_outputs(self):
        for i in range(4):
            self.init.output.set_output(i, self.frequency, self.on_time, self.active, self.max_duty)

    def output_control_thread(self):
        while self.active:
            if self.settings_changed:
                self.enable_outputs()
                self.settings_changed = False
            time.sleep(0.1)
        init.output.disable_outputs()
        self.settings_changed = True

    def calculate_max_on_time(self, frequency):
        max_on_time_based_on_duty = (self.max_duty / 100) * (1000000 / frequency)
        return min(self.max_on_time, int(max_on_time_based_on_duty))

    def rotary_1(self, val):
        increment = 10 if self.ten_x else 1
        delta = ((val - self.val_old[0]) + 101) % 101  # Adjust for wrapping
        if delta > 50:  # Handle wrapping in the negative direction
            delta -= 101
        new_on_time = self.on_time + increment * delta
        max_on_time = self.calculate_max_on_time(self.frequency)
        self.on_time = max(self.min_on_time, min(max_on_time, int(new_on_time)))
        self.val_old[0] = val
        self.update_display(update_on_time=True, update_frequency=False)
        self.settings_changed = True

    def rotary_2(self, val):
        increment = 10 if self.ten_x else 1
        delta = ((val - self.val_old[1]) + 101) % 101  # Adjust for wrapping
        if delta > 50:  # Handle wrapping in the negative direction
            delta -= 101
        new_frequency = self.frequency + increment * delta

        direction = new_frequency - self.frequency
        while new_frequency in self.banned_frequencies:
            if direction > 0:
                new_frequency += increment
            elif direction < 0:
                new_frequency -= increment

        max_on_time = self.calculate_max_on_time(new_frequency)
        self.frequency = max(self.min_freq, min(self.max_freq, new_frequency))
        if self.on_time > max_on_time:
            self.on_time = max_on_time
        self.val_old[1] = val       
        self.update_display(update_on_time=False, update_frequency=True)
        self.settings_changed = True

    def switch_2(self):
        self.active = False
        self.init.output.disable_outputs()
        parent_screen = self.parent
        if parent_screen:
            self.init.menu.set_screen(parent_screen)
            self.init.menu.draw()

    def switch_3(self):
        self.active = not self.active
        max_on_time = self.calculate_max_on_time(self.frequency)
        self.on_time = min(self.on_time, max_on_time)
        self.update_display(update_on_time=True, update_frequency=True, update_active=True)

        if self.active:
            if not self.thread:
                self.thread = _thread.start_new_thread(self.output_control_thread, ())
        else:
            self.thread = None

    def switch_4(self):
        self.ten_x = not self.ten_x
        self.update_display(update_on_time=False, update_frequency=False, update_ten_x=True)
