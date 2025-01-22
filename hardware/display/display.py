"""
MicroPython Tesla Coil Controller (MPTCC)
by Cameron Prince
teslauniverse.com

hardware/display/display.py
Parent class for displays - provides shared display-related functions.
"""

import time
import _thread
from machine import I2C
from ..hardware import Hardware
from ...hardware.init import init

class Display(Hardware):
    """
    A parent class for displays, providing shared display-related functions for 
    the MicroPython Tesla Coil Controller (MPTCC).

    Attributes:
    -----------
    init : object
        The initialization object containing configuration and hardware settings.
    scroll_thread : _thread
        The thread object for handling scrolling text.
    scroll_flag : bool
        Flag to indicate if scrolling is active.
    scroll_text : str
        The text to be scrolled.
    scroll_y_position : int
        The y-coordinate position of the scrolling text.
    """

    def __init__(self):
        """
        Constructs all the necessary attributes for the Display object.
        """
        super().__init__()
        self.init = init

        # Prepare the I2C bus.
        self.init.init_i2c_1()

        self.scroll_thread = None
        self.scroll_flag = False
        self.scroll_text = None
        self.scroll_y_position = None

    """
    Display functions.
    """
    def header(self, text):
        """
        Displays a header with a horizontal line below the text.

        Parameters:
        ----------
        text : str
            The header text to display.
        """
        self.center_text(str.upper(text), 0)
        self.hline(0, self.DISPLAY_HEADER_HEIGHT, self.width, 1)

    def loading_screen(self):
        """
        Helper to display a loading message.
        """
        # Clear the display.
        self.clear()
        # Add the loading text.
        self.center_text("Loading...", 20)
        self.show()

    def alert_screen(self, text):
        """
        Display an alert message on the display and wait for 2 seconds.

        Parameters:
        ----------
        text : str
            The alert message to display.
        """
        self.message_screen(text)
        time.sleep(2)

    def message_screen(self, text):
        """
        Display an alert message on the display and wait for 2 seconds.

        Parameters:
        ----------
        text : str
            The alert message to display.
        """
        self.clear()

        # Wrap the text if it's too wide for the display.
        font_width = self.DISPLAY_FONT_WIDTH
        # Add a small amount of padding.
        max_width = self.width - (font_width * 2)
        wrapped_lines = self.wrap_text(text, max_width)

        # Calculate the starting y position to center the text vertically.
        total_text_height = len(wrapped_lines) * self.DISPLAY_LINE_HEIGHT
        y_start = (self.height - total_text_height) // 2

        # Display each line of the wrapped text.
        y = y_start
        for line in wrapped_lines:
            # Only center text if it is at least 3 font widths less than the screen width.
            if len(line) * font_width <= max_width - 3 * font_width:
                self.center_text(line, y)
            else:
                self.text(line.strip(), 0, y, 1)  # Left-align the text.
            y += self.DISPLAY_LINE_HEIGHT  # Use line height from init.

        init.display.show()

    def center_text(self, text, y):
        """
        Helper function to center text on the display.

        Parameters:
        ----------
        text : str
            The text to display.
        y : int
            The y-coordinate to display the text at.
        """
        text_width = len(text) * self.DISPLAY_FONT_WIDTH
        x = (self.width - text_width) // 2
        self.text(text.strip(), x, y, 1)

    def truncate_text(self, text, y, center=False):
        """
        Truncates text with ellipsis if it exceeds the display width.

        Parameters:
        ----------
        text : str
            The text to be truncated.
        y : int
            The y-coordinate where the text will be displayed.
        center : bool, optional
            If True, the text will be centered on the display (default is False).
        """
        max_chars = self.width // 8
        if len(text) > max_chars:
            text = text[:max_chars - 3] + "..."
        if center:
            x = (self.width - len(text) * 8) // 2
        else:
            x = 0
        self.text(text, x, y, 1)

    def wrap_text(self, text, max_width):
        """
        Wraps text on word boundaries to fit within the specified width.

        Parameters:
        ----------
        text : str
            The text to wrap.
        max_width : int
            The maximum width in pixels that the text can occupy.

        Returns:
        -------
        list
            A list of strings, each representing a line of wrapped text.
        """
        words = text.split()
        lines = []
        current_line = ""

        for word in words:
            # Calculate the width of the current line if the word is added.
            new_line = current_line + ("" if not current_line else " ") + word
            new_line_width = len(new_line) * self.DISPLAY_FONT_WIDTH

            # Check if adding the next word exceeds the max width.
            if new_line_width <= max_width:
                # Add the word to the current line.
                current_line = new_line
            else:
                # Add the current line to lines and start a new line.
                if current_line:
                    lines.append(current_line)
                current_line = word

        # Add the last line.
        if current_line:
            lines.append(current_line)

        return lines

    """
    Scrolling functions.
    """
    def start_scroll_task(self, text, y_position):
        """
        Helper to start scrolling text as a separate thread.

        Parameters:
        ----------
        text : str
            The text to be scrolled.
        y_position : int
            The y-coordinate position of the text on the display.
        """
        time.sleep(0.2)
        self.stop_scroll_task()
        if self.scroll_text != text:
            self.scroll_flag = True
            self.scroll_text = text
            self.scroll_y_position = y_position
            self.scroll_thread = _thread.start_new_thread(self.scroll_task, (text, y_position))

    def stop_scroll_task(self):
        """
        Helper to stop scrolling text and end the thread.
        """
        if self.scroll_thread:
            self.scroll_flag = False
            # Small delay to ensure the thread has stopped.
            time.sleep(0.2)
            self.scroll_thread = None
            self.scroll_text = None
            self.scroll_y_position = None

    def scroll_task(self, text, y_position):
        """
        The main function for handling text scrolling.

        Parameters:
        ----------
        text : str
            The text to be scrolled.
        y_position : int
            The y-coordinate position of the text on the display.
        """
        delay_seconds = 1
        delay_interval = 0.1
        elapsed_time = 0
        while self.scroll_flag and elapsed_time < delay_seconds:
            time.sleep(delay_interval)
            elapsed_time += delay_interval
        if not self.scroll_flag:
            return
        v_padding = int((self.DISPLAY_LINE_HEIGHT - self.DISPLAY_FONT_HEIGHT) / 2)
        while self.scroll_flag:
            for i in range(len(text) + self.DISPLAY_ITEMS_PER_PAGE):
                if not self.scroll_flag:
                    return
                scroll_text = (text + "    ")[i:] + (text + "    ")[:i]
                self.fill_rect(0, y_position, self.width, self.DISPLAY_LINE_HEIGHT, 1)
                self.text(scroll_text[:20], 0, y_position + v_padding, 0)
                self.show()
                time.sleep(0.2)
