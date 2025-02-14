"""
MicroPython Tesla Coil Controller (MPTCC)
by Cameron Prince
teslauniverse.com

screens/configure/arsg.py
Provides the screen for configuring ARSG emulator settings.
"""

from mptcc.hardware.init import init
from mptcc.lib.menu import Screen
from mptcc.lib.config import Config as config
import mptcc.lib.utils as utils

class ARSGConfig(Screen):
    """
    A class to represent and handle the configuration screen for the ARSG emulator settings 
    in the MicroPython Tesla Coil Controller (MPTCC).

    Attributes:
    -----------
    name : str
        The name of the screen.
    display : object
        The display object for rendering the screen.
    config : dict
        The configuration dictionary read from the flash memory.
    min_lin_freq : int
        The minimum line frequency for the ARSG emulator.
    min_on_time : int
        The minimum on time for the ARSG emulator.
    min_freq : int
        The minimum frequency for the ARSG emulator.
    max_line_freq : int
        The maximum line frequency for the ARSG emulator.
    max_on_time : int
        The maximum on time for the ARSG emulator.
    max_freq : int
        The maximum frequency for the ARSG emulator.
    max_duty : float
        The maximum duty cycle for the ARSG emulator.
    page : int
        The current page index for the configuration screen.
    font_width : int
        The width of the font used in the display.
    """

    def __init__(self, name):
        super().__init__(name)
        self.name = name
        self.init = init
        self.display = self.init.display
        self.config = config.read_config()
        self.min_line_freq = self.config.get("arsg_min_line_freq", config.ARSG_MIN_LINE_FREQ_DEF)
        self.min_on_time = self.config.get("arsg_min_on_time", config.ARSG_MIN_ON_TIME_DEF)
        self.min_freq = self.config.get("arsg_min_freq", config.ARSG_MIN_FREQ_DEF)
        self.max_line_freq = self.config.get("arsg_max_line_freq", config.ARSG_MAX_LINE_FREQ_DEF)
        self.max_on_time = self.config.get("arsg_max_on_time", config.ARSG_MAX_ON_TIME_DEF)
        self.max_freq = self.config.get("arsg_max_freq", config.ARSG_MAX_FREQ_DEF)
        self.max_duty = self.config.get("arsg_max_duty", config.ARSG_MAX_DUTY_DEF)
        self.page = 0
        self.font_width = self.init.display.DISPLAY_FONT_WIDTH

    def draw(self):
        """
        Displays one of three pages which contain ARSG configuration inputs.
        """
        self.display.clear()
        self.display.header(self.name)

        # Display the first page with minimum line frequency, on time, and frequency inputs.
        if self.page == 0:
            min_line_freq_str = f"{self.min_line_freq}"
            min_on_time_str = f"{self.min_on_time}"
            min_freq_str = f"{self.min_freq}"
            self.display.text("Min Line Fr:", 0, 16, 1)
            self.display.text(min_line_freq_str, self.display.width - len(min_line_freq_str) * self.font_width, 16, 1)
            self.display.text("Min On Time:", 0, 28, 1)
            self.display.text(min_on_time_str, self.display.width - len(min_on_time_str) * self.font_width, 28, 1)
            self.display.text("Min Freq:", 0, 40, 1)
            self.display.text(min_freq_str, self.display.width - len(min_freq_str) * self.font_width, 40, 1)
            self.display.text("Page 1/3", 0, 56, 1)
        # Display the second page with maximum line frequency, on time, and frequency inputs.
        elif self.page == 1:
            max_line_freq_str = f"{self.max_line_freq}"
            max_on_time_str = f"{self.max_on_time}"
            max_freq_str = f"{self.max_freq}"
            self.display.text("Max Line Fr:", 0, 16, 1)
            self.display.text(max_line_freq_str, self.display.width - len(max_line_freq_str) * self.font_width, 16, 1)
            self.display.text("Max On Time:", 0, 28, 1)
            self.display.text(max_on_time_str, self.display.width - len(max_on_time_str) * self.font_width, 28, 1)
            self.display.text("Max Freq:", 0, 40, 1)
            self.display.text(max_freq_str, self.display.width - len(max_freq_str) * self.font_width, 40, 1)
            self.display.text("Page 2/3", 0, 56, 1)
        # Display the third page with the max duty cycle input.
        elif self.page == 2:
            max_duty_str = f"{self.max_duty:.1f}%"
            self.display.text("Max Duty:", 0, 16, 1)
            self.display.text(max_duty_str, self.display.width - len(max_duty_str) * self.font_width, 16, 1)
            self.display.text("Page 3/3", 0, 56, 1)
        
        self.display.show()

    def save_config(self):
        """
        Writes the ARSG configuration to flash memory.
        """
        self.config["arsg_min_line_freq"] = self.min_line_freq
        self.config["arsg_min_on_time"] = self.min_on_time
        self.config["arsg_min_freq"] = self.min_freq
        self.config["arsg_max_line_freq"] = self.max_line_freq
        self.config["arsg_max_on_time"] = self.max_on_time
        self.config["arsg_max_freq"] = self.max_freq
        self.config["arsg_max_duty"] = self.max_duty
        config.write_config(self.config)

    def rotary_1(self, direction):
        """
        Respond to encoder 1 rotation to adjust the first value on the current page.

        Parameters:
        ----------
        direction : int
            The direction of rotation (1 for clockwise, -1 for counterclockwise).
        """
        if self.page == 0:
            increment = 1
            self.min_line_freq = max(config.ARSG_MIN_LINE_FREQ_MIN, min(config.ARSG_MIN_LINE_FREQ_MAX, self.min_line_freq + increment * direction))
        elif self.page == 1:
            increment = 1
            self.max_line_freq = max(config.ARSG_MAX_LINE_FREQ_MIN, min(config.ARSG_MAX_LINE_FREQ_MAX, self.max_line_freq + increment * direction))
        elif self.page == 2:
            increment = 0.1
            self.max_duty = max(config.ARSG_MAX_DUTY_MIN, min(config.ARSG_MAX_DUTY_MAX, self.max_duty + increment * direction))

        self.save_config()
        self.draw()

    def rotary_2(self, direction):
        """
        Respond to encoder 2 rotation to adjust the second value on the current page.

        Parameters:
        ----------
        direction : int
            The direction of rotation (1 for clockwise, -1 for counterclockwise).
        """
        if self.page == 0:
            increment = 1
            self.min_on_time = max(config.ARSG_MIN_ON_TIME_MIN, min(config.ARSG_MIN_ON_TIME_MAX, self.min_on_time + increment * direction))
        elif self.page == 1:
            increment = 10
            self.max_on_time = max(config.ARSG_MAX_ON_TIME_MIN, min(config.ARSG_MAX_ON_TIME_MAX, self.max_on_time + increment * direction))

        self.save_config()
        self.draw()

    def rotary_3(self, direction):
        """
        Respond to encoder 3 rotation to adjust the third value on the current page.

        Parameters:
        ----------
        direction : int
            The direction of rotation (1 for clockwise, -1 for counterclockwise).
        """
        if self.page == 0:
            increment = 10
            self.min_freq = max(config.ARSG_MIN_FREQ_MIN, min(config.ARSG_MIN_FREQ_MAX, self.min_freq + increment * direction))
        elif self.page == 1:
            increment = 10
            self.max_freq = max(config.ARSG_MAX_FREQ_MIN, min(config.ARSG_MAX_FREQ_MAX, self.max_freq + increment * direction))

        self.save_config()
        self.draw()

    def switch_2(self):
        """
        Respond to encoder 2 presses to return to the configuration menu.
        """
        self.page = 0
        parent_screen = self.parent
        if parent_screen:
            self.init.menu.set_screen(parent_screen)
            self.init.menu.draw()

    def switch_3(self):
        """
        Respond to encoder 3 presses to move to the prior page.
        """
        self.page = (self.page - 1) % 3
        self.draw()

    def switch_4(self):
        """
        Respond to encoder 4 presses to move to the next page.
        """
        self.page = (self.page + 1) % 3
        self.draw()
