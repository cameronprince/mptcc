"""
MicroPython Tesla Coil Controller (MPTCC)
by Cameron Prince
teslauniverse.com

hardware/display/display.py
Parent class for displays - provides shared display-related functions.
"""

import time
import uasyncio as asyncio
from machine import I2C
from ..hardware import Hardware
from ...hardware.init import init

class Display(Hardware):
    def __init__(self):
        super().__init__()
        self.init = init

        self.scroll_task = None        # Holds the asyncio task for scrolling.
        self.scroll_flag = None        # Stores the unique identifier of the currently scrolling item.
        self.scroll_text = None        # The text to be scrolled.
        self.scroll_y_position = None  # The y-coordinate position of the scrolling text.

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
            # Center the text if it fits within the display width.
            if len(line) * font_width <= max_width:
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
    def start_scroll_task(self, text, y_position, identifier, background_color=1):
        """
        Helper to start scrolling text as an asyncio task.

        Parameters:
        ----------
        text : str
            The text to scroll.
        y_position : int
            The y-coordinate where the text will be displayed.
        identifier : int
            A unique identifier (e.g., file index) for the scrolling task.
        background_color : int, optional
            The background color for the text (0 for inactive, 1 for active). Defaults to 1 (active).
        """
        # Stop any existing scrolling task.
        self.stop_scroll_task()

        # Start a new scrolling task if the text requires scrolling.
        text_width = len(text) * self.DISPLAY_FONT_WIDTH
        if text_width > self.width:
            self.scroll_flag = identifier  # Set the unique identifier.
            self.scroll_text = text
            self.scroll_y_position = y_position

            # Immediately update the display with the new filename.
            self.fill_rect(0, y_position, self.width, self.DISPLAY_LINE_HEIGHT, background_color)  # Set background color.
            v_padding = int((self.DISPLAY_LINE_HEIGHT - self.DISPLAY_FONT_HEIGHT) / 2)
            self.text(text, 0, y_position + v_padding, not background_color)  # Set text color.
            self.show()

            # Create the scrolling task.
            self.scroll_task = asyncio.create_task(self._scroll_task(text, y_position, identifier, background_color))

    def stop_scroll_task(self):
        """
        Helper to stop scrolling text and reset the scroll state.
        """
        if self.scroll_task:
            self.scroll_flag = None  # Reset the unique identifier.
            task_to_cancel = self.scroll_task  # Store the task reference.
            self.scroll_task = None  # Reset the task reference immediately.

            try:
                if not task_to_cancel.done():
                    task_to_cancel.cancel()  # Cancel the task.
            except Exception as e:
                # Ignore the "can't cancel self" error.
                if "can't cancel self" not in str(e):
                    print(f"[ERROR] Failed to cancel scroll task: {e}")

            # Clear the previous scrolling text and redraw it in a non-scrolling state.
            if self.scroll_text and self.scroll_y_position is not None:
                self.fill_rect(0, self.scroll_y_position, self.width, self.DISPLAY_LINE_HEIGHT, 0)  # Clear the line.
                v_padding = int((self.DISPLAY_LINE_HEIGHT - self.DISPLAY_FONT_HEIGHT) / 2)
                self.text(self.scroll_text, 0, self.scroll_y_position + v_padding, 1)  # Redraw the text.
                self.show()
            self.scroll_text = None
            self.scroll_y_position = None

    async def _scroll_task(self, text, y_position, identifier, background_color=1):
        """
        The main coroutine for handling text scrolling.

        Parameters:
        ----------
        text : str
            The text to scroll.
        y_position : int
            The y-coordinate where the text will be displayed.
        identifier : int
            A unique identifier (e.g., file index) for the scrolling task.
        background_color : int, optional
            The background color for the text (0 for inactive, 1 for active). Defaults to 1 (active).
        """
        delay_seconds = 1
        delay_interval = 0.1
        elapsed_time = 0

        # Initial delay before scrolling starts.
        while self.scroll_flag == identifier and elapsed_time < delay_seconds:
            await asyncio.sleep(delay_interval)
            elapsed_time += delay_interval

        v_padding = int((self.DISPLAY_LINE_HEIGHT - self.DISPLAY_FONT_HEIGHT) / 2)

        # Main scrolling loop.
        while self.scroll_flag == identifier:
            for i in range(len(text) + self.DISPLAY_ITEMS_PER_PAGE):
                if self.scroll_flag != identifier:
                    return  # Exit if the identifier no longer matches.

                # Generate the scrolling text.
                scroll_text = (text + "    ")[i:] + (text + "    ")[:i]
                self.fill_rect(0, y_position, self.width, self.DISPLAY_LINE_HEIGHT, background_color)  # Set background color.
                self.text(scroll_text[:20], 0, y_position + v_padding, not background_color)  # Set text color.
                self.show()
                await asyncio.sleep(0.2)  # Adjust the scroll speed as needed.

        # Ensure the task exits cleanly.
        return
