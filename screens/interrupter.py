"""
MicroPython Tesla Coil Controller (MPTCC)
by Cameron Prince

screens/interrupter.py
Provides functionality for the standard interrupter.
"""

from mptcc.init import init
from mptcc.lib.menu import CustomItem
from mptcc.lib.config import Config as config
import mptcc.lib.utils as utils
import _thread
import time

class Interrupter(CustomItem):
    """
    A class to represent and handle the standard interrupter functionality for the MicroPython Tesla Coil Controller (MPTCC).

    Attributes:
    -----------
    name : str
        The name of the interrupter screen.
    display : object
        The display object for rendering the screen.
    frequency : int
        The frequency of the interrupter output.
    on_time : int
        The on time of the interrupter output.
    min_freq : int
        The minimum frequency of the interrupter.
    max_freq : int
        The maximum frequency of the interrupter.
    min_on_time : int
        The minimum on time of the interrupter.
    max_on_time : int
        The maximum on time of the interrupter.
    max_duty : int
        The maximum duty cycle of the interrupter.
    font_width : int
        The width of the font used in the display.
    ten_x : bool
        Flag for enabling or disabling the 10x multiplier for controls.
    active : bool
        Flag indicating whether the interrupter and associated thread are active.
    val_old : list
        List to store old values of the rotary encoders.
    thread : _thread
        The thread that controls the output.
    """

    def __init__(self, name):
        """
        Constructs all the necessary attributes for the Interrupter object.

        Parameters:
        ----------
        name : str
            The name of the interrupter screen.
        """
        super().__init__(name)
        self.init = init
        self.display = self.init.display
        self.config = config.read_config()

        self.min_on_time = self.config.get("interrupter_min_on_time", config.DEF_INTERRUPTER_MIN_ON_TIME)
        self.min_freq = self.config.get("interrupter_min_freq", config.DEF_INTERRUPTER_MIN_FREQ)
        self.max_on_time = self.config.get("interrupter_max_on_time", config.DEF_INTERRUPTER_MAX_ON_TIME)
        self.max_freq = self.config.get("interrupter_max_freq", config.DEF_INTERRUPTER_MAX_FREQ)
        self.max_duty = self.config.get("interrupter_max_duty", config.DEF_INTERRUPTER_MAX_DUTY)

        self.frequency = self.min_freq  # Initialize with the saved min frequency
        self.on_time = self.min_on_time  # Initialize with the saved min on time
        self.font_width = self.display.DISPLAY_FONT_WIDTH
        self.ten_x = False
        self.active = False
        self.val_old = [0, 0]
        self.banned_frequencies = self.init.BANNED_INTERRUPTER_FREQUENCIES
        self.thread = None
        self.settings_changed = True  # Initialize to True for first-time setup

    def draw(self):
        """
        Display the interrupter control settings on the screen.
        """
        # Clear the display.
        self.display.clear()

        # Show the header.
        self.display.header("Interrupter")

        # Display the labels.
        self.display.text("On Time:", 0, 20, 1)
        self.display.text("Freq:", 0, 30, 1)
        self.display.text("10x", 100, 50, 0)
        self.display.text("Active", 0, 50, 0)

        # Display the initial values.
        self.update_display(update_on_time=True, update_frequency=True, initial=True)

    def update_display(self, update_on_time=True, update_frequency=True, update_ten_x=False, update_active=False, initial=False):
        """
        Update the display for on_time, frequency, ten_x, and active values.

        Parameters:
        ----------
        update_on_time : bool
            Flag to indicate whether to update the on_time value on the display.
        update_frequency : bool
            Flag to indicate whether to update the frequency value on the display.
        update_ten_x : bool
            Flag to indicate whether to update the ten_x indicator on the display.
        update_active : bool
            Flag to indicate whether to update the active indicator on the display.
        initial : bool
            Flag to indicate whether this is the initial drawing of the values.
        """
        max_chars = 5
        rect_width = max_chars * self.font_width

        if update_on_time:
            on_time_str = f"{self.on_time}us"
            if not initial:
                # Draw black rectangle to clear previous on_time value.
                self.display.fill_rect(self.display.width - rect_width, 20, rect_width, 10, 0)
            # Draw new on_time value.
            self.display.text(on_time_str, self.display.width - len(on_time_str) * self.font_width, 20, 1)
        
        if update_frequency:
            freq_str = f"{self.frequency}Hz"
            if not initial:
                # Ensure we clear a wide enough area.
                self.display.fill_rect(self.display.width - (max_chars + 1) * self.font_width, 30, (max_chars + 1) * self.font_width, 10, 0)
            # Draw new frequency value.
            self.display.text(freq_str, self.display.width - len(freq_str) * self.font_width, 30, 1)
        
        if update_ten_x:
            if self.ten_x:
                self.display.text("10x", 100, 50, 1)
            else:
                # Draw black rectangle to clear previous 10x value.
                self.display.fill_rect(100, 50, 3 * self.font_width, 10, 0)
        
        if update_active:
            if self.active:
                self.display.text("Active", 0, 50, 1)
            else:
                # Draw black rectangle to clear previous Active value.
                self.display.fill_rect(0, 50, 6 * self.font_width, 10, 0)
        
        self.display.show()

    def enable_outputs(self):
        """
        Helper method to fire all outputs equally.
        """
        for i in range(4):
            self.init.output.set_output(i, self.frequency, self.on_time, self.active, self.max_duty)

    def output_control_thread(self):
        """
        Thread that controls the outputs based on the attributes.
        """
        while self.active:
            if self.settings_changed:
                self.enable_outputs()
                self.settings_changed = False
            time.sleep(0.1)
        init.output.disable_outputs()
        self.settings_changed = True

    def calculate_max_on_time(self, frequency):
        """
        Determine the maximum on time value based on max duty setting and current frequency.

        Parameters:
        ----------
        frequency : int
            The current frequency of the interrupter.

        Returns:
        -------
        int
            The maximum on time based on the duty cycle and frequency.
        """
        max_on_time_based_on_duty = (self.max_duty / 100) * (1000000 / frequency)
        return min(self.max_on_time, int(max_on_time_based_on_duty))

    def rotary_1(self, val):
        """
        Respond to encoder 1 rotation to increase/decrease output on time.

        Parameters:
        ----------
        val : int
            The new value from the rotary encoder.
        """
        increment = 10 if self.ten_x else 1
        new_on_time = self.on_time + increment * (val - self.val_old[0])
        max_on_time = self.calculate_max_on_time(self.frequency)
        self.on_time = max(self.min_on_time, min(max_on_time, int(new_on_time)))
        self.val_old[0] = val
        self.update_display(update_on_time=True, update_frequency=False)
        self.settings_changed = True  # Set the flag to reapply settings

    def rotary_2(self, val):
        """
        Respond to encoder 2 rotation to increase/decrease output frequency.

        Parameters:
        ----------
        val : int
            The new value from the rotary encoder.
        """
        increment = 10 if self.ten_x else 1
        new_frequency = self.frequency + increment * (val - self.val_old[1])

        # Determine the direction of frequency change.
        direction = new_frequency - self.frequency

        # Skip banned frequencies.
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
        """
        Respond to encoder 2 presses to return to the main menu.
        """
        self.active = False
        self.init.output.disable_outputs()
        parent_screen = self.parent
        if parent_screen:
            self.init.menu.set_screen(parent_screen)
            self.init.menu.draw()

    def switch_3(self):
        """
        Respond to encoder 3 presses to enable or disable the interrupter outputs.
        """
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
        """
        Respond to encoder 4 presses to enable or disable the 10x multiplier for on time and frequency controls.
        """
        self.ten_x = not self.ten_x
        self.update_display(update_on_time=False, update_frequency=False, update_ten_x=True)

