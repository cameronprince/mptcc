"""
MicroPython Tesla Coil Controller (MPTCC)
by Cameron Prince
teslauniverse.com

hardware/rgb_led/rgb_led_ring_small.py
RGB LED Ring Small driver with batch updates.
"""

import time
import _thread
from ...lib.duppa import DuPPa
from ...lib.utils import calculate_percent, status_color, hex_to_rgb
from ..rgb_led.rgb_led import RGB, RGBLED
from ...hardware.init import init


# Constants and register definitions.
CONSTANTS = {
    # ISSI3746-specific registers
    "ISSI3746_PAGE0": 0x00,
    "ISSI3746_PAGE1": 0x01,

    "ISSI3746_COMMANDREGISTER": 0xFD,
    "ISSI3746_COMMANDREGISTER_LOCK": 0xFE,
    "ISSI3746_ID_REGISTER": 0xFC,
    "ISSI3746_ULOCK_CODE": 0xC5,

    "ISSI3746_CONFIGURATION": 0x50,
    "ISSI3746_GLOBALCURRENT": 0x51,
    "ISSI3746_PULLUPDOWM": 0x52,
    "ISSI3746_OPENSHORT": 0x53,
    "ISSI3746_TEMPERATURE": 0x5F,
    "ISSI3746_SPREADSPECTRUM": 0x60,
    "ISSI3746_RESET_REG": 0x8F,
    "ISSI3746_PWM_FREQUENCY_ENABLE": 0xE0,
    "ISSI3746_PWM_FREQUENCY_SET": 0xE2,
}


class RGBLEDRingSmall(RGBLED):
    """
    A class to control the RGB LED Ring Small device with batch updates.
    """

    def __init__(self, i2c_instance, addresses, default_color, threshold_brightness, full_brightness, rotation, delay_between_steps, mode):
        super().__init__()
        self.init = init
        self.i2c_instance = i2c_instance
        self.addresses = addresses
        self.default_color = default_color
        self.threshold_brightness = threshold_brightness
        self.full_brightness = full_brightness
        self.rotation = rotation
        self.delay_between_steps = delay_between_steps
        self.mode = mode
        self.instances = []

        # Validate that the number of addresses matches NUMBER_OF_COILS.
        if len(self.addresses) != self.init.NUMBER_OF_COILS:
            raise ValueError(
                f"The number of RGB LED Ring Small addresses ({len(self.addresses)}) "
                f"must match NUMBER_OF_COILS ({self.init.NUMBER_OF_COILS}). The program will now exit."
            )

        # Prepare the I2C bus.
        if self.i2c_instance == 2:
            self.init.init_i2c_2()
            self.i2c = self.init.i2c_2
            self.mutex = self.init.i2c_2_mutex
        else:
            self.init.init_i2c_1()
            self.i2c = self.init.i2c_1
            self.mutex = self.init.i2c_1_mutex

        # Generate a unique key for this instance.
        instance_key = len(self.init.rgb_led_instances["rgb_led_ring_small"])

        for i, address in enumerate(self.addresses):
            led_instance = RGB_RGBLEDRingSmall(
                i2c=self.i2c,
                address=address,
                mutex=self.mutex,
                default_color=self.default_color,
                threshold_brightness=self.threshold_brightness,
                full_brightness=self.full_brightness,
                rotation=self.rotation,
                delay_between_steps=self.delay_between_steps,
                mode=self.mode
            )
            self.instances.append(led_instance)

        # Print initialization details.
        print(f"RGBLEDRingSmall {instance_key} initialized on I2C_{self.i2c_instance} with {self.init.NUMBER_OF_COILS} objects:")
        for i, addr in enumerate(self.addresses):
            print(f"- RGBLEDRingSmall {i + 1}: I2C address 0x{addr:02X}")
        print(f"- Asyncio polling: {self.init.RGB_LED_ASYNCIO_POLLING}")


class RGB_RGBLEDRingSmall(RGB):
    """
    A class for handling the RGB LED Ring Small device with batch updates.
    """
    def __init__(self, i2c, address, mutex, default_color, threshold_brightness, full_brightness, rotation, delay_between_steps, mode):
        super().__init__()
        self.i2c = i2c
        self.address = address
        self.mutex = mutex
        self.init = init
        self.num_leds = 24
        self.threshold_brightness = threshold_brightness
        self.full_brightness = full_brightness
        self.default_color = self._get_default_color(default_color)
        self.step_delay = delay_between_steps
        self.rotation = rotation
        self.mode = mode
        self.led_ring = None

        # Define the base logical-to-physical index mapping.
        base_logical_to_physical_index = [23, 17, 11, 5, 22, 16, 10, 4, 21, 15, 9, 3, 20, 14, 8, 2, 19, 13, 7, 1, 18, 12, 6, 0]

        # Define the logical order of LEDs.
        logical_order = list(range(self.num_leds))

        # Apply rotation to the logical order.
        rotation_leds = int((self.rotation / 360) * self.num_leds)
        rotated_logical_order = logical_order[-rotation_leds:] + logical_order[:-rotation_leds]
        reversed_logical_order = rotated_logical_order[::-1]

        offset = 1
        offset_logical_order = reversed_logical_order[-offset:] + reversed_logical_order[:-offset]

        # Map the offset logical order to physical indices.
        self.logical_to_physical_index = [base_logical_to_physical_index[i] for i in offset_logical_order]

        self.vu_colors = self._generate_vu_colors()
        self._initialize_led_ring()

    def _get_default_color(self, default_color):
        """
        Get the default color or handle the "vu_meter" case.
        """
        if default_color == "vu_meter":
            return None
        else:
            return hex_to_rgb(default_color)

    def _generate_vu_colors(self):
        """
        Generate the VU meter colors for the LED ring, accounting for rotation.
        """
        # Define the base VU meter colors.
        vu_colors = [
            (0, 255, 0),   # Green
            (85, 255, 0),  # Yellow-green
            (170, 255, 0), # Yellow
            (255, 170, 0), # Yellow-orange
            (255, 85, 0),  # Orange
            (255, 0, 0)    # Red
        ]

        # Generate smooth color transitions.
        vu_meter_colors = []
        for i in range(len(vu_colors) - 1):
            steps = self.num_leds // (len(vu_colors) - 1)
            gradient = self._get_color_gradient(vu_colors[i], vu_colors[i + 1], steps)
            vu_meter_colors.extend(gradient)

        # Ensure the list has exactly 24 colors.
        if len(vu_meter_colors) < self.num_leds:
            vu_meter_colors.extend([vu_colors[-1]] * (self.num_leds - len(vu_meter_colors)))

        return vu_meter_colors

    def _get_color_gradient(self, color1, color2, steps):
        """
        Generate a color gradient between two colors.
        """
        gradient = []
        for i in range(steps):
            ratio = i / float(steps)
            red = int(color1[0] * (1 - ratio) + color2[0] * ratio)
            green = int(color1[1] * (1 - ratio) + color2[1] * ratio)
            blue = int(color1[2] * (1 - ratio) + color2[2] * ratio)
            gradient.append((red, green, blue))
        return gradient

    def _initialize_led_ring(self):
        """
        Initialize the LED ring with default settings.
        """
        self.init.mutex_acquire(self.mutex, "rgb_led_ring_small:_initialize_led_ring")
        try:
            self.led_ring = DuPPa(self.i2c, self.address, CONSTANTS)
            self.led_ring.reset()
            time.sleep(0.01)
            self.led_ring.configuration(0x01)
            self.led_ring.pwm_frequency_enable(1)
            self.led_ring.spread_spectrum(0b0010110)
            self.led_ring.global_current(0xFF)
            self.led_ring.set_scaling_all(0xFF)
            self.led_ring.pwm_mode()
        finally:
            self.init.mutex_release(self.mutex, "rgb_led_ring_small:_initialize_led_ring")
            self.off()

    def off(self, output=None):
        """
        Set all LEDs to the threshold brightness (default off state).
        """
        colors = []
        for i in range(self.num_leds):
            if self.default_color is None:
                colors.append(self.vu_colors[i])
            else:
                colors.append(self.default_color)
        self._set_rgb_batch(colors, self.threshold_brightness)

    def set_status(self, output, frequency, on_time, max_duty=None, max_on_time=None):
        """
        Calculates the RGB color based on frequency, on_time, and optional constraints.
        """
        if self.mode == "status":
            # Use status_color to determine the color for all LEDs.
            color = status_color(frequency, on_time, max_duty, max_on_time)
            colors = [color] * self.num_leds
            brightness = self.full_brightness
            self._set_rgb_batch(colors, brightness)
        else:
            # Use calculate_percent to determine the number of LEDs to brighten.
            value = calculate_percent(frequency, on_time, max_duty, max_on_time)
            num_bright_leds = int(self.num_leds * value / 100)

            # Prepare the colors and brightness values.
            colors = []
            brightness_values = []
            for i in range(self.num_leds):
                if i < num_bright_leds:
                    # Use the VU meter color and full brightness.
                    colors.append(self.vu_colors[i])
                    brightness_values.append(self.full_brightness)
                else:
                    # Use the default color and threshold brightness.
                    if self.default_color is None:
                        colors.append(self.vu_colors[i])
                    else:
                        colors.append(self.default_color)
                    brightness_values.append(self.threshold_brightness)

            # Set the colors and brightness values.
            self._set_rgb_batch_with_brightness(colors, brightness_values)

    def _set_rgb_batch_with_brightness(self, colors, brightness_values):
        """
        Set the color and brightness of all LEDs in a batch update, with individual brightness values.
        """
        self.init.mutex_acquire(self.mutex, "rgb_led_ring_small:_set_rgb_batch_with_brightness")
        try:
            buffer = bytearray(72)  # 24 LEDs * 3 channels
            for i, (physical_index, brightness) in enumerate(zip(self.logical_to_physical_index, brightness_values)):
                dimmed_color = (
                    colors[i][0] * brightness // 0xFF,  # Red
                    colors[i][1] * brightness // 0xFF,  # Green
                    colors[i][2] * brightness // 0xFF   # Blue
                )
                buffer[3 * physical_index] = dimmed_color[2]  # Blue
                buffer[3 * physical_index + 1] = dimmed_color[1]  # Green
                buffer[3 * physical_index + 2] = dimmed_color[0]  # Red
            self.led_ring.set_rgb_batch(buffer)
        finally:
            self.init.mutex_release(self.mutex, "rgb_led_ring_small:_set_rgb_batch_with_brightness")

    def _set_rgb_batch(self, colors, brightness):
        """
        Set the color and brightness of all LEDs in a batch update.
        """
        self.init.mutex_acquire(self.mutex, "rgb_led_ring_small:_set_rgb_batch")
        try:
            buffer = bytearray(72)  # 24 LEDs * 3 channels.
            for i, physical_index in enumerate(self.logical_to_physical_index):
                dimmed_color = (
                    colors[i][0] * brightness // 0xFF,  # Red
                    colors[i][1] * brightness // 0xFF,  # Green
                    colors[i][2] * brightness // 0xFF   # Blue
                )
                buffer[3 * physical_index] = dimmed_color[2]      # Blue
                buffer[3 * physical_index + 1] = dimmed_color[1]  # Green
                buffer[3 * physical_index + 2] = dimmed_color[0]  # Red
            self.led_ring.set_rgb_batch(buffer)
        finally:
            self.init.mutex_release(self.mutex, "rgb_led_ring_small:_set_rgb_batch")
