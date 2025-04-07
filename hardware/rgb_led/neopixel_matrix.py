"""
MicroPython Tesla Coil Controller (MPTCC)
by Cameron Prince
teslauniverse.com

hardware/rgb_led/neopixel.py
RGB LED device utilizing the WS2812/NeoPixel on a GPIO pin.
"""

from machine import Pin
from neopixel import NeoPixel as NeoPixelDriver
from ...lib.utils import status_color, hex_to_rgb, calculate_percent
from ..rgb_led.rgb_led import RGBLED, RGB
from ...hardware.init import init


class GPIO_NeoPixel_Matrix(RGBLED):
    def __init__(
        self,
        pin,
        reverse=False,
        default_color=None,
        threshold_brightness=16,
        full_brightness=255,
        rotation=0,
        invert=False,
        mode="status",
        matrix=None,
        vu_meter_sensitivity=0.5,
        vu_meter_colors=[]
    ):
        super().__init__()
        self.init = init
        self.instances = []

        self.rows, self.cols = map(int, matrix.split('x'))
        segments = self.rows * self.cols

        self.np = NeoPixelDriver(Pin(pin), segments)
        if isinstance(default_color, str):
            self.default_color = hex_to_rgb(default_color) if default_color.upper() != "VU_METER" else "VU_METER"

        for i in range(self.cols):
            kwargs = {
                "driver": self.np,
                "instance_index": i,
                "mode": mode.upper(),
                "reverse": reverse,
                "num_segments": segments,
                "default_color": self.default_color,
                "threshold_brightness": threshold_brightness,
                "full_brightness": full_brightness,
                "rotation": rotation,
                "invert": invert,
                "vu_meter_sensitivity": vu_meter_sensitivity,
                "vu_meter_colors": vu_meter_colors,
                "rows": self.rows,
                "cols": self.cols
            }
            self.instances.append(RGB_NeoPixel_Matrix(**kwargs))

        instance_key = len(self.init.rgb_led_instances["neopixel_matrix"])
        print(f"GPIO NeoPixel Matrix {instance_key} ({matrix}) initialized on pin {pin}")
        print(f"- Reverse: {reverse}")
        print(f"- Rotation: {rotation} degrees")
        print(f"- Invert: {invert}")
        print(f"- Mode: {mode}")
        print(f"- Default color: {default_color}")
        print(f"- Threshold brightness: {threshold_brightness}")
        print(f"- Full brightness: {full_brightness}")
        print(f"- VU meter sensitivity: {vu_meter_sensitivity}")
        print(f"- VU meter colors: {vu_meter_colors}")
        print(f"- Asyncio polling: {self.init.RGB_LED_ASYNCIO_POLLING}")


class RGB_NeoPixel_Matrix(RGB):
    def __init__(
        self,
        driver,
        instance_index,
        mode,
        reverse,
        num_segments,
        default_color,
        vu_meter_sensitivity,
        vu_meter_colors,
        threshold_brightness=16,
        full_brightness=255,
        rotation=0,
        invert=False,
        rows=None,
        cols=None,
    ):
        super().__init__()
        self.driver = driver
        self.instance_index = instance_index
        self.mode = mode
        self.reverse = reverse
        self.num_segments = num_segments
        self.default_color = default_color
        self.threshold_brightness = threshold_brightness
        self.full_brightness = full_brightness
        self.rotation = rotation
        self.invert = invert
        self.vu_meter_sensitivity = vu_meter_sensitivity
        self.vu_meter_colors = vu_meter_colors
        self.rows = rows
        self.cols = cols
        self.init = init

        self.rotated_index = self._get_index(self.instance_index)
        self.off()

    def off(self, index=None):
        """Turn off LEDs or set default color (if defined and not #000000)."""
        col = self.instance_index % self.cols
        if self.default_color == "VU_METER":
            self._set_column(col, self.vu_meter_colors, self.threshold_brightness)
        else:
            r, g, b = self._scale_rgb(*self.default_color, self.threshold_brightness)
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

    def _scale_rgb(self, r, g, b, brightness):
        """Scale RGB values by brightness (0-255)."""
        return ((r, g, b) if brightness is None else
                (r * brightness // 255, g * brightness // 255, b * brightness // 255))

    def _set_column(self, col, colors, brightness=None):
        """Set all LEDs in a column to given colors with optional brightness."""
        for row, (r, g, b) in enumerate(colors):
            index = row * self.cols + col
            self.driver[self._get_index(index)] = self._scale_rgb(r, g, b, brightness)

    def set_color(self, r, g, b):
        """
        Sets the color of the RGB LEDs in the instance's column.
        If color is (0, 0, 0), uses default_color or VU colors based on mode setting.
        """
        col = self.instance_index % self.cols
        if r == 0 and g == 0 and b == 0:
            if isinstance(self.default_color, tuple):
                r, g, b = self._scale_rgb(*self.default_color, self.threshold_brightness)
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
                color = self._scale_rgb(*color, self.full_brightness)
            self.set_color(*color)
        else:
            level = calculate_percent(freq, on_time, max_duty, max_on_time) / 100.0
            leds_to_light = min(max(int(self.rows * level + self.vu_meter_sensitivity), 0), self.rows)
            col = self.instance_index % self.cols
            if self.default_color == "VU_METER":
                for row in range(self.rows):
                    brightness = self.full_brightness if row < leds_to_light else self.threshold_brightness
                    color = self._scale_rgb(*self.vu_meter_colors[row], brightness)
                    self.driver[self._get_index(row * self.cols + col)] = color
            else:
                r, g, b = self._scale_rgb(*self.default_color, self.threshold_brightness)
                for row in range(self.rows):
                    if row < leds_to_light:
                        color = self._scale_rgb(*self.vu_meter_colors[row], self.full_brightness)
                    else:
                        color = (r, g, b)
                    self.driver[self._get_index(row * self.cols + col)] = color
            self.driver.write()
