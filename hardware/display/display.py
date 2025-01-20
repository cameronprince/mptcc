"""
MicroPython Tesla Coil Controller (MPTCC)
by Cameron Prince
teslauniverse.com

hardware/display/display.py
Parent class for displays - provides shared display-related functions.
"""
from ..hardware import Hardware
from ... import init
from machine import I2C

class Display(Hardware):
    def __init__(self):
        super().__init__()
        self.init = init

        # Make sure the I2C bus is ready.
        if not isinstance(self.init.init.i2c, I2C) or not self.init.init.i2c.is_ready():
            self.init.init.init_i2c()

    """
    Display functions.
    """
    def header(self, text):
        self.center_text(str.upper(text), 0)
        self.hline(0, self.DISPLAY_HEADER_HEIGHT, self.width, 1)

    def loading_screen(self):
        """
        Helper to display a loading message.
        """
        # Clear the display.
        init.display.fill(0)
        # Add the loading text.
        center_text("Loading...", 20)
        init.display.show()

    def alert_screen(self, text):
        """
        Display an alert message on the display and wait for 2 seconds.

        Parameters:
        ----------
        text : str
            The alert message to display.
        """
        message_screen(text)
        time.sleep(2)

    def message_screen(self, text):
        """
        Display an alert message on the display and wait for 2 seconds.

        Parameters:
        ----------
        text : str
            The alert message to display.
        """
        init.display.fill(0)

        # Wrap the text if it's too wide for the display.
        font_width = init.DISPLAY_FONT_WIDTH
        # Add a small amount of padding.
        max_width = init.display.width - (font_width * 2)
        wrapped_lines = wrap_text(text, max_width)

        # Calculate the starting y position to center the text vertically.
        total_text_height = len(wrapped_lines) * init.DISPLAY_LINE_HEIGHT
        y_start = (init.display.height - total_text_height) // 2

        # Display each line of the wrapped text
        y = y_start
        for line in wrapped_lines:
            # Only center text if it is at least 3 font widths less than the screen width
            if len(line) * font_width <= max_width - 3 * font_width:
                center_text(line, y)
            else:
                init.display.text(line.strip(), 0, y, 1)  # Left-align the text
            y += init.DISPLAY_LINE_HEIGHT  # Use line height from init

        init.display.show()

    def center_text(self, text, y):
        """
        Helper function to center text on the display.

        Parameters:
        ----------
        display : Display
            The display object to show the text on.
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
        max_chars = init.display.width // 8
        if len(text) > max_chars:
            text = text[:max_chars - 3] + "..."
        if center:
            x = (init.display.width - len(text) * 8) // 2
        else:
            x = 0
        init.display.text(text, x, y, 1)

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
            # Calculate the width of the current line if the word is added
            new_line = current_line + ("" if not current_line else " ") + word
            new_line_width = len(new_line) * init.DISPLAY_FONT_WIDTH

            # Check if adding the next word exceeds the max width
            if new_line_width <= max_width:
                # Add the word to the current line
                current_line = new_line
            else:
                # Add the current line to lines and start a new line
                if current_line:
                    lines.append(current_line)
                current_line = word

        # Add the last line
        if current_line:
            lines.append(current_line)

        return lines

    """
    Scrolling functions.
    """

    scroll_thread = None
    scroll_flag = False
    scroll_text = None
    scroll_y_position = None

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
        global scroll_thread, scroll_flag, scroll_text, scroll_y_position
        time.sleep(0.2)
        stop_scroll_task()
        if scroll_text != text:
            scroll_flag = True
            scroll_text = text
            scroll_y_position = y_position
            scroll_thread = _thread.start_new_thread(scroll_task, (text, y_position))

    def stop_scroll_task(self):
        """
        Helper to stop scrolling text and end the thread.
        """
        global scroll_thread, scroll_flag, scroll_text, scroll_y_position
        if scroll_thread:
            scroll_flag = False
            # Small delay to ensure the thread has stopped.
            time.sleep(0.2)
            scroll_thread = None
            scroll_text = None
            scroll_y_position = None

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
        global scroll_flag
        delay_seconds = 1
        delay_interval = 0.1
        elapsed_time = 0
        while scroll_flag and elapsed_time < delay_seconds:
            time.sleep(delay_interval)
            elapsed_time += delay_interval
        if not scroll_flag:
            return
        v_padding = int((init.DISPLAY_LINE_HEIGHT - init.DISPLAY_FONT_HEIGHT) / 2)
        while scroll_flag:
            for i in range(len(text) + init.DISPLAY_ITEMS_PER_PAGE):
                if not scroll_flag:
                    return
                scroll_text = (text + "    ")[i:] + (text + "    ")[:i]
                init.display.fill_rect(0, y_position, init.display.width, init.DISPLAY_LINE_HEIGHT, 1)
                init.display.text(scroll_text[:20], 0, y_position + v_padding, 0)
                init.display.show()
                time.sleep(0.2)

