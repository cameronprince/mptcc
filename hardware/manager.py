"""
MicroPython Tesla Coil Controller (MPTCC)
by Cameron Prince
teslauniverse.com

hardware/manager.py
Provides the manager classes for controlling the hardware.
"""

import time


class HardwareManager:
    def __init__(self, init, hardware_type):
        """
        Initialize the HardwareManager with the init object and hardware type.

        Parameters:
        ----------
        init : Init
            The global init object containing hardware instances.
        hardware_type : str
            The type of hardware (e.g., "display", "input", "output").
        """
        self.init = init
        self.hardware_type = hardware_type
        self.instances = getattr(self.init, f"{hardware_type}_instances")


class DisplayManager(HardwareManager):

    def __init__(self, init):
        super().__init__(init, "display")

        self.width = self.init.PRIMARY_DISPLAY_WIDTH
        self.height = self.init.PRIMARY_DISPLAY_HEIGHT
        self.line_height = self.init.PRIMARY_DISPLAY_LINE_HEIGHT
        self.font_width = self.init.PRIMARY_DISPLAY_FONT_WIDTH
        self.font_height = self.init.PRIMARY_DISPLAY_FONT_HEIGHT
        self.header_height = self.init.PRIMARY_DISPLAY_HEADER_HEIGHT
        self.items_per_page = self.init.PRIMARY_DISPLAY_ITEMS_PER_PAGE

        self.scroll_task = None        # Holds the asyncio task for scrolling.
        self.scroll_flag = None        # Stores the unique identifier of the currently scrolling item.
        self.scroll_text = None        # The text to be scrolled.
        self.scroll_y_position = None  # The y-coordinate position of the scrolling text.

    def _call_driver_method(self, method_name, *args, **kwargs):
        """
        Helper method to call a driver method for each instance of each driver.

        Parameters:
        ----------
        method_name : str
            The name of the method to call (e.g., "_clear", "_show").
        *args : tuple
            Positional arguments to pass to the method.
        **kwargs : dict
            Keyword arguments to pass to the method.
        """
        for driver_type, driver_instances in self.instances.items():
            for index, driver_instance in enumerate(driver_instances):  # Track instance index
                method = getattr(driver_instance, method_name)
                if method:
                    if hasattr(driver_instance, 'mutex'):
                        self.init.mutex_acquire(
                            driver_instance.mutex,
                            f"{driver_type}:{index}:{method_name}"  # Include instance index
                        )
                    method(*args, **kwargs)
                    if hasattr(driver_instance, 'mutex'):
                        self.init.mutex_release(
                            driver_instance.mutex,
                            f"{driver_type}:{index}:{method_name}"  # Include instance index
                        )

    def header(self, text):
        """
        Displays a header with a horizontal line below the text.

        Parameters:
        ----------
        text : str
            The header text to display.
        """
        self.center_text(str.upper(text), 0)
        self.hline(0, self.header_height, self.width, 1)

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

        font_width = self.font_width
        max_width = self.width - (font_width * 2)
        wrapped_lines = self.wrap_text(text, max_width)

        total_text_height = len(wrapped_lines) * self.line_height
        y_start = (self.height - total_text_height) // 2

        y = y_start
        for line in wrapped_lines:
            if len(line) * font_width <= max_width:
                self.center_text(line, y)
            else:
                self.text(line.strip(), 0, y, 1)
            y += self.line_height

        self.show()

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
        text_width = len(text) * self.font_width
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
            new_line_width = len(new_line) * self.font_width

            if new_line_width <= max_width:
                current_line = new_line
            else:
                if current_line:
                    lines.append(current_line)
                current_line = word

        if current_line:
            lines.append(current_line)

        return lines

    def show(self, all=True):
        """
        Update the display with the current frame buffer content.
        """
        self._call_driver_method("_show")

    def clear(self, all=True):
        """
        Clear the display.
        """
        self._call_driver_method("_clear")

    def text(self, text, x, y, color=1, all=True):
        """
        Display text on the screen.
        """
        self._call_driver_method("_text", text, x, y, color)

    def hline(self, x, y, w, color, all=True):
        """
        Draw a horizontal line on the screen.
        """
        self._call_driver_method("_hline", x, y, w, color)

    def fill_rect(self, x, y, w, h, color, all=True):
        """
        Draw a filled rectangle on the screen.
        """
        self._call_driver_method("_fill_rect", x, y, w, h, color)


class OutputManager(HardwareManager):
    def __init__(self, init):
        super().__init__(init, "output")
        self.rgb_led_manager = RGBLEDManager(init)

    def set_output(self, index, active=False, freq=None, on_time=None, max_duty=None, max_on_time=None):
        """
        Sets the specified output across all registered output drivers.

        Parameters:
        ----------
        index : int
            The index of the output to be set.
        active : bool, optional
            Whether the outputs should be active. Defaults to False.
        freq : int, optional
            The frequency of the output signal in Hz. Required if active is True.
        on_time : int, optional
            The on time of the output signal in microseconds. Required if active is True.
        max_duty : int, optional
            The maximum duty cycle allowed.
        max_on_time : int, optional
            The maximum on time allowed in microseconds.
        """
        for driver_key, driver_instances in self.instances.items():
            # Iterate over each group of Output_GPIO_PWM objects.
            for output_group in driver_instances:
                # Check if the index is within the range of this group.
                if index < len(output_group):
                    # Call set_output on the specific Output_GPIO_PWM object.
                    output_group[index].set_output(active, freq, on_time)
                else:
                    print(f"Warning: Output index {index} is out of range for {driver_key}.")

        # Control the RGB LED for this output.
        if active:
            self.rgb_led_manager.enable_led(index, freq, on_time, max_duty, max_on_time)
        else:
            self.rgb_led_manager.disable_led(index)

    def set_all_outputs(self, active=False, freq=None, on_time=None, max_duty=None, max_on_time=None):
        """
        Sets all outputs across all registered output drivers.

        Parameters:
        ----------
        active : bool, optional
            Whether the outputs should be active. Defaults to False.
        freq : int, optional
            The frequency of the output signal in Hz. Required if active is True.
        on_time : int, optional
            The on time of the output signal in microseconds. Required if active is True.
        max_duty : int, optional
            The maximum duty cycle allowed.
        max_on_time : int, optional
            The maximum on time allowed in microseconds.
        """
        for index in range(self.init.NUMBER_OF_COILS):
            self.set_output(index, active, freq, on_time, max_duty, max_on_time)


class RGBLEDManager(HardwareManager):
    def __init__(self, init):
        super().__init__(init, "rgb_led")

    def enable_led(self, index, freq, on_time, max_duty=None, max_on_time=None):
        """
        Enables the specified LED on all RGB LED drivers.
        """
        for driver_key, driver_instances in self.instances.items():
            # print(f"Debug: driver_key = {driver_key}")  # Debug: Print driver key
            # print(f"Debug: driver_instances = {driver_instances}")  # Debug: Print driver instances
            for led_group in driver_instances:
                if index < len(led_group):
                    led_instance = led_group[index]
                    # print(f"Debug: Processing LED instance {led_instance} at index {index}")  # Debug: Print LED instance
                    if hasattr(led_instance, 'set_status'):
                        # print(f"Debug: Calling set_status on {led_instance}")  # Debug: Print method call
                        led_instance.set_status(index, freq, on_time, max_duty, max_on_time)
                    else:
                        # print(f"Warning: LED instance {driver_key} does not have a set_status method.")
                        pass
                else:
                    # print(f"Warning: LED index {index} is out of range for {driver_key}.")
                    pass

    def disable_led(self, index):
        """
        Disables the specified LED on all RGB LED drivers.
        """
        for driver_key, driver_instances in self.instances.items():
            for led_group in driver_instances:
                if index < len(led_group):
                    led_instance = led_group[index]
                    # print(f"Debug: Processing LED instance {led_instance} at index {index}")  # Debug: Print LED instance
                    if hasattr(led_instance, 'off'):
                        # print(f"Debug: Calling off on {led_instance}")  # Debug: Print method call
                        led_instance.off(index)
                    else:
                        # print(f"Warning: LED instance {driver_key} does not have an off method.")
                        pass
                else:
                    # print(f"Warning: LED index {index} is out of range for {driver_key}.")
                    pass

    def set_color(self, index, r, g, b):
        """
        Sets the color of the specified LED on all RGB LED drivers.
        """
        # print("set_color")
        for driver_key, driver_instances in self.instances.items():
            for led_group in driver_instances:
                if index < len(led_group):
                    led_instance = led_group[index]
                    # print(f"Debug: Processing LED instance {led_instance} at index {index}")  # Debug: Print LED instance
                    if hasattr(led_instance, 'set_color'):
                        # print(f"Debug: Calling set_color on {led_instance}")  # Debug: Print method call
                        led_instance.set_color(r, g, b)
                    else:
                        # print(f"Warning: LED instance {driver_key} does not have a set_color method.")
                        pass
                else:
                    # print(f"Warning: LED index {index} is out of range for {driver_key}.")
                    pass

    def disable_all_leds(self):
        """
        Disables all RGB LEDs across all registered drivers.
        """
        # print("disable_all_leds")
        for index in range(self.init.NUMBER_OF_COILS):
            self.set_color(index, 0, 0, 0)
