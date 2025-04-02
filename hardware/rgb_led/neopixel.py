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


class GPIO_NeoPixel(RGBLED):
    def __init__(
        self,
        pin,
        segments,
        reverse=False,
        default_color=None,
        threshold_brightness=16,
        full_brightness=255,
        rotation=0,
        invert=False,
        mode="status",
        matrix=None,
    ):
        super().__init__()
        self.init = init
        self.instances = []

        if segments < self.init.NUMBER_OF_COILS:
            raise ValueError(
                f"Number of NeoPixel segments ({segments}) "
                f"is less than the number of coils ({self.init.NUMBER_OF_COILS})."
            )

        self.np = NeoPixelDriver(Pin(pin), segments)
        if isinstance(default_color, str):
            default_color = hex_to_rgb(default_color) if default_color.lower() != "vu_meter" else "vu_meter"

        self.rows = self.cols = None
        if matrix:
            self.rows, self.cols = map(int, matrix.split('x'))
            if self.rows * self.cols != segments:
                raise ValueError("Matrix dimensions don't match segment count.")
        elif mode.upper() == "VU_METER":
            raise ValueError("VU meter mode is only valid for LED matrices.")

        num_instances = self.cols if matrix else self.init.NUMBER_OF_COILS
        for i in range(num_instances):
            kwargs = {
                "driver": self.np,
                "instance_index": i,
                "reverse": reverse,
                "num_segments": segments,
                "default_color": default_color,
                "threshold_brightness": threshold_brightness,
                "full_brightness": full_brightness,
            }
            if matrix:
                kwargs.update({
                    "rotation": rotation,
                    "invert": invert,
                    "mode": mode,
                    "rows": self.rows,
                    "cols": self.cols
                })
            self.instances.append(RGB_NeoPixel(**kwargs))

        instance_key = len(self.init.rgb_led_instances["neopixel"])
        print(f"GPIO NeoPixel {instance_key} initialized on pin {pin} ({segments} segments).")
        print(f"- Matrix: {matrix}.")
        print(f"- Reverse: {reverse}.")
        print(f"- Rotation: {rotation} degrees.")
        print(f"- Invert: {invert}.")
        print(f"- Mode: {mode}.")
        print(f"- Default color: {default_color}.")
        print(f"- Threshold brightness: {threshold_brightness}.")
        print(f"- Full brightness: {full_brightness}.")
        print(f"- Asyncio polling: {self.init.RGB_LED_ASYNCIO_POLLING}.")


class RGB_NeoPixel(RGB):
    _BASE_VU_COLORS = [
        (0, 255, 0),    # Green.
        (85, 255, 0),   # Yellow-green.
        (170, 255, 0),  # Yellow.
        (255, 170, 0),  # Yellow-orange.
        (255, 85, 0),   # Orange.
        (255, 0, 0)     # Red.
    ]

    def __init__(
        self,
        driver,
        instance_index,
        reverse,
        num_segments,
        default_color,
        threshold_brightness=16,
        full_brightness=255,
        rotation=0,
        invert=False,
        mode="STATUS",
        rows=None,
        cols=None,
    ):
        super().__init__()
        self.driver = driver
        self.instance_index = instance_index
        self.reverse = reverse
        self.num_segments = num_segments
        self.default_color = default_color
        self.threshold_brightness = threshold_brightness
        self.full_brightness = full_brightness
        self.rotation = rotation
        self.invert = invert
        self.mode = mode.upper()
        self.rows = rows
        self.cols = cols
        self.init = init

        self.is_matrix = bool(rows and cols)
        self.rotated_index = (self._get_index(self.instance_index) if self.is_matrix
                             else self.instance_index)
        if self.is_matrix and (self.mode == "VU_METER" or self.default_color == "vu_meter"):
            self.vu_colors = self._generate_vu_colors()

        self.off()

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

    def off(self, output=None):
        """
        Turns off the LED or sets it to default state.
        For matrices, resets all LEDs to the appropriate default.
        """
        if self.is_matrix:
            if self.default_color == "vu_meter":
                for col in range(self.cols):
                    self._set_column(col, self.vu_colors, self.threshold_brightness)
            else:
                r, g, b = self._scale_rgb(*self.default_color, self.threshold_brightness)
                for col in range(self.cols):
                    self._set_column(col, [(r, g, b)] * self.rows)
            self.driver.write()
        else:
            self.set_color(0, 0, 0)

    def set_color(self, r, g, b):
        """
        Sets the color of the RGB LED using the NeoPixel driver.
        If color is (0, 0, 0), uses default_color or VU colors for matrices.
        """
        if r == 0 and g == 0 and b == 0:
            if self.is_matrix and self.default_color == "vu_meter":
                self._set_column(self.instance_index % self.cols, self.vu_colors,
                                self.threshold_brightness)
            else:
                r, g, b = self._scale_rgb(*self.default_color, self.threshold_brightness)
                if self.is_matrix and self.mode == "STATUS":
                    self._set_column(self.instance_index % self.cols,
                                    [(r, g, b)] * self.rows)
                else:
                    actual_index = (self.num_segments - 1 - self.rotated_index
                                   if self.reverse else self.rotated_index)
                    self.driver[actual_index] = (r, g, b)
        else:
            if self.is_matrix and self.mode == "STATUS":
                self._set_column(self.instance_index % self.cols, [(r, g, b)] * self.rows)
            else:
                actual_index = (self.num_segments - 1 - self.rotated_index
                               if self.reverse else self.rotated_index)
                self.driver[actual_index] = (r, g, b)
        self.driver.write()

    def set_status(self, output, freq, on_time, max_duty=None, max_on_time=None):
        """Set the LED status based on coil parameters."""
        if not self.is_matrix or self.mode == "STATUS":
            color = status_color(freq, on_time, max_duty, max_on_time)
            if self.full_brightness != 255:
                color = self._scale_rgb(*color, self.full_brightness)
            self.set_color(*color)
        else:
            level = calculate_percent(freq, on_time, max_duty, max_on_time) / 100.0
            leds_to_light = min(max(int(self.rows * level + 0.5), 0), self.rows)
            col = self.instance_index % self.cols
            # Use VU colors for "off" LEDs if default_color is "vu_meter".
            if self.default_color == "vu_meter":
                for row in range(self.rows):
                    brightness = self.full_brightness if row < leds_to_light else self.threshold_brightness
                    color = self._scale_rgb(*self.vu_colors[row], brightness)
                    self.driver[self._get_index(row * self.cols + col)] = color
            else:
                r, g, b = self._scale_rgb(*self.default_color, self.threshold_brightness)
                for row in range(self.rows):
                    if row < leds_to_light:
                        color = self._scale_rgb(*self.vu_colors[row], self.full_brightness)
                    else:
                        color = (r, g, b)
                    self.driver[self._get_index(row * self.cols + col)] = color
            self.driver.write()

    def _generate_vu_colors(self):
        """Generate VU meter colors for the LED matrix."""
        colors = []
        base_len = len(self._BASE_VU_COLORS)
        for i in range(self.rows):
            segment = min(i * base_len // self.rows, base_len - 1)
            next_segment = min(segment + 1, base_len - 1)
            ratio = (i % (self.rows // base_len)) / (self.rows / base_len) if base_len < self.rows else 0
            r = int(self._BASE_VU_COLORS[segment][0] * (1 - ratio) + self._BASE_VU_COLORS[next_segment][0] * ratio)
            g = int(self._BASE_VU_COLORS[segment][1] * (1 - ratio) + self._BASE_VU_COLORS[next_segment][1] * ratio)
            b = int(self._BASE_VU_COLORS[segment][2] * (1 - ratio) + self._BASE_VU_COLORS[next_segment][2] * ratio)
            colors.append((r, g, b))
        return colors
