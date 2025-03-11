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
        self.clear()
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

        font_width = self.DISPLAY_FONT_WIDTH
        max_width = self.width - (font_width * 2)
        wrapped_lines = self.wrap_text(text, max_width)

        total_text_height = len(wrapped_lines) * self.DISPLAY_LINE_HEIGHT
        y_start = (self.height - total_text_height) // 2

        y = y_start
        for line in wrapped_lines:
            if len(line) * font_width <= max_width:
                self.center_text(line, y)
            else:
                self.text(line.strip(), 0, y, 1)
            y += self.DISPLAY_LINE_HEIGHT

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
            new_line = current_line + ("" if not current_line else " ") + word
            new_line_width = len(new_line) * self.DISPLAY_FONT_WIDTH

            if new_line_width <= max_width:
                current_line = new_line
            else:
                if current_line:
                    lines.append(current_line)
                current_line = word

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
        self.stop_scroll_task()

        text_width = len(text) * self.DISPLAY_FONT_WIDTH
        if text_width > self.width:
            self.scroll_flag = identifier
            self.scroll_text = text
            self.scroll_y_position = y_position

            self.fill_rect(0, y_position, self.width, self.DISPLAY_LINE_HEIGHT, background_color)
            v_padding = int((self.DISPLAY_LINE_HEIGHT - self.DISPLAY_FONT_HEIGHT) / 2)
            self.text(text, 0, y_position + v_padding, not background_color)
            self.show()

            self.scroll_task = asyncio.create_task(self._scroll_task(text, y_position, identifier, background_color))

    def stop_scroll_task(self):
        """
        Helper to stop scrolling text and reset the scroll state.
        """
        if self.scroll_task:
            self.scroll_flag = None
            task_to_cancel = self.scroll_task
            self.scroll_task = None

            try:
                task_to_cancel.cancel()
            except Exception as e:
                if "can't cancel self" not in str(e):
                    print(f"[ERROR] Failed to cancel scroll task: {e}")

            if self.scroll_text and self.scroll_y_position is not None:
                self.fill_rect(0, self.scroll_y_position, self.width, self.DISPLAY_LINE_HEIGHT, 0)
                v_padding = int((self.DISPLAY_LINE_HEIGHT - self.DISPLAY_FONT_HEIGHT) / 2)
                self.text(self.scroll_text, 0, self.scroll_y_position + v_padding, 1)
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

        while self.scroll_flag == identifier and elapsed_time < delay_seconds:
            await asyncio.sleep(delay_interval)
            elapsed_time += delay_interval

        v_padding = int((self.DISPLAY_LINE_HEIGHT - self.DISPLAY_FONT_HEIGHT) / 2)

        while self.scroll_flag == identifier:
            for i in range(len(text) + self.DISPLAY_ITEMS_PER_PAGE):
                if self.scroll_flag != identifier:
                    return

                scroll_text = (text + "    ")[i:] + (text + "    ")[:i]
                self.fill_rect(0, y_position, self.width, self.DISPLAY_LINE_HEIGHT, background_color)
                self.text(scroll_text[:20], 0, y_position + v_padding, not background_color)
                self.show()
                await asyncio.sleep(0.2)

        return
