"""
MicroPython Tesla Coil Controller (MPTCC)
by Cameron Prince
teslauniverse.com

hardware/rgb_led/neopixel.py
RGB LED device utilizing the WS2812/NeoPixel on a GPIO pin.
"""

from machine import Pin
from neopixel import NeoPixel as NeoPixelDriver
from ...lib.utils import status_color, hex_to_rgb, calculate_percent, scale_rgb
from ..rgb_led.rgb_led import RGBLED, RGB
from ...hardware.init import init


class GPIO_NeoPixel_Matrix(RGBLED):
    def __init__(self, config):
        super().__init__()
        self.init = init
        self.instances = []

        self.matrix = config.get("matrix", "8x8")
        self.pin = config.get("pin", None)
        self.default_color = config.get("default_color", "#000000")

        if self.pin is None:
            return

        self.rows, self.cols = map(int, self.matrix.split('x'))
        self.segments = self.rows * self.cols

        self.np = NeoPixelDriver(Pin(self.pin), self.segments)
        if isinstance(self.default_color, str):
            self.default_color = hex_to_rgb(self.default_color) if self.default_color.upper() != "VU_METER" else "VU_METER"

        for i in range(self.cols):
            self.instances.append(RGB_NeoPixel_Matrix(self.np, i, self.segments, self.default_color, self.rows, self.cols, config))

        instance_key = len(self.init.rgb_led_instances["neopixel_matrix"])
        print(f"GPIO NeoPixel Matrix {instance_key} ({self.matrix}) initialized on pin {self.pin}")
        print(f"- Reverse: {config.get('reverse', False)}")
        print(f"- Rotation: {config.get('rotation', 0)} degrees")
        print(f"- Invert: {config.get('invert', 0)}")
        print(f"- Mode: {config.get('mode', 0)}")
        print(f"- Default color: {self.default_color}")
        print(f"- Threshold brightness: {config.get('threshold_brightness', 0)}")
        print(f"- Full brightness: {config.get('full_brightness', 0)}")
        print(f"- VU meter sensitivity: {config.get('vu_meter_sensitivity', 1)}")
        print(f"- VU meter colors: {config.get('vu_meter_colors', [])}")


class RGB_NeoPixel_Matrix(RGB):
    def __init__(self, driver, instance_index, num_segments, default_color, rows=None, cols=None, config=[]):
        super().__init__()
        self.driver = driver
        self.instance_index = instance_index
        self.num_segments = num_segments
        self.default_color = default_color
        self.rows = rows
        self.cols = cols
        self.init = init

        self.mode = config.get("mode", "status").upper()
        self.reverse = config.get("reverse", False)
        self.threshold_brightness = config.get("threshold_brightness", 0)
        self.full_brightness = config.get("full_brightness", 0)
        self.rotation = config.get("rotation", False)
        self.invert = config.get("invert", False)
        self.vu_meter_sensitivity = config.get("vu_meter_sensitivity", 1)
        self.vu_meter_colors = config.get("vu_meter_colors", [])

        self.rotated_index = self._get_index(self.instance_index)
        self.off()

    def off(self, index=None):
        """Turn off LEDs or set default color (if defined and not #000000)."""
        col = self.instance_index % self.cols
        if self.default_color == "VU_METER":
            self._set_column(col, self.vu_meter_colors, self.threshold_brightness)
        else:
            r, g, b = scale_rgb(*self.default_color, self.threshold_brightness)
            self._set_column(col, [(r, g, b)] * self.rows)
        self.driver.write()

    def _get_index(self, index):
        """Calculate rotated and inverted index for matrix LEDs only."""
        row, col = divmod(index, self.cols)
        if self.rotation == 90:
            row, col = col, self.rows - 1 - row
        elif self.rotation == 180:
            row, col = self.rows - 1 - row, self.cols - 1 - col
        elif self.rotation == 270:
            row, col = self.cols - 1 - col, row
        if self.invert:
            if self.rotation in [0, 180]:
                col = self.cols - 1 - col
            else:
                row = self.rows - 1 - row
        actual_index = row * self.cols + col
        return (self.num_segments - 1 - actual_index if self.reverse else actual_index)

    def _set_column(self, col, colors, brightness=None):
        """Set all LEDs in a column to given colors with optional brightness."""
        for row, (r, g, b) in enumerate(colors):
            index = row * self.cols + col
            self.driver[self._get_index(index)] = scale_rgb(r, g, b, brightness)

    def set_color(self, r, g, b):
        """
        Sets the color of the RGB LEDs in the instance's column.
        If color is (0, 0, 0), uses default_color or VU colors based on mode setting.
        """
        col = self.instance_index % self.cols
        if r == 0 and g == 0 and b == 0:
            if isinstance(self.default_color, tuple):
                r, g, b = scale_rgb(*self.default_color, self.threshold_brightness)
                self._set_column(col, [(r, g, b)] * self.rows)
            elif self.mode == "VU_METER":
                self._set_column(col, self.vu_meter_colors, self.threshold_brightness)
        else:
            self._set_column(col, [(r, g, b)] * self.rows)
        self.driver.write()

    def set_status(self, output, freq, on_time, max_duty=None, max_on_time=None):
        """Set the LED status based on coil parameters (called by the output manager)."""
        if self.mode == "STATUS":
            color = status_color(freq, on_time, max_duty, max_on_time)
            if self.full_brightness != 255:
                color = scale_rgb(*color, self.full_brightness)
            self.set_color(*color)
        else:
            level = calculate_percent(freq, on_time, max_duty, max_on_time) / 100.0
            leds_to_light = min(max(int(self.rows * level + self.vu_meter_sensitivity), 0), self.rows)
            col = self.instance_index % self.cols
            if self.default_color == "VU_METER":
                for row in range(self.rows):
                    brightness = self.full_brightness if row < leds_to_light else self.threshold_brightness
                    color = scale_rgb(*self.vu_meter_colors[row], brightness)
                    self.driver[self._get_index(row * self.cols + col)] = color
            else:
                r, g, b = scale_rgb(*self.default_color, self.threshold_brightness)
                for row in range(self.rows):
                    if row < leds_to_light:
                        color = scale_rgb(*self.vu_meter_colors[row], self.full_brightness)
                    else:
                        color = (r, g, b)
                    self.driver[self._get_index(row * self.cols + col)] = color
            self.driver.write()
