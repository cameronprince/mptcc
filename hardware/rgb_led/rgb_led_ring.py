"""
MicroPython Tesla Coil Controller (MPTCC)
by Cameron Prince
teslauniverse.com

hardware/rgb_led/rgb_led_ring.py
RGB LED Ring driver with batch updates for IS31FL3745, supporting 48 LEDs.
"""

import time
from ...lib.utils import calculate_percent, status_color, hex_to_rgb, rgb_to_hex, scale_rgb
from ..rgb_led.rgb_led import RGB, RGBLED
from ...hardware.init import init

# CONSTANTS for IS31FL3745.
CONSTANTS = {
    "ISSI3745_PAGE0": 0x00,
    "ISSI3745_PAGE1": 0x01,
    "ISSI3745_PAGE2": 0x02,
    "ISSI3745_COMMANDREGISTER": 0xFD,
    "ISSI3745_COMMANDREGISTER_LOCK": 0xFE,
    "ISSI3745_ULOCK_CODE": 0xC5,
    "ISSI3745_CONFIGURATION": 0x00,
    "ISSI3745_GLOBALCURRENT": 0x01,
    "ISSI3745_SPREADSPECTRUM": 0x25,
    "ISSI3745_RESET_REG": 0x2F,
    "ISSI_LED_MAP": [
        [0x12, 0x24, 0x36, 0x48, 0x5A, 0x6C, 0x7E, 0x90, 0x0F, 0x21, 0x33, 0x45, 0x57, 0x69, 0x7B, 0x8D, 0x0C, 0x1E, 0x30, 0x42, 0x54, 0x66, 0x78, 0x8A, 0x09, 0x1B, 0x2D, 0x3F, 0x51, 0x63, 0x75, 0x87, 0x06, 0x18, 0x2A, 0x3C, 0x4E, 0x60, 0x72, 0x84, 0x03, 0x15, 0x27, 0x39, 0x4B, 0x5D, 0x6F, 0x81],  # Red
        [0x11, 0x23, 0x35, 0x47, 0x59, 0x6B, 0x7D, 0x8F, 0x0E, 0x20, 0x32, 0x44, 0x56, 0x68, 0x7A, 0x8C, 0x0B, 0x1D, 0x2F, 0x41, 0x53, 0x65, 0x77, 0x89, 0x08, 0x1A, 0x2C, 0x3E, 0x50, 0x62, 0x74, 0x86, 0x05, 0x17, 0x29, 0x3B, 0x4D, 0x5F, 0x71, 0x83, 0x02, 0x14, 0x26, 0x38, 0x4A, 0x5C, 0x6E, 0x80],  # Green
        [0x10, 0x22, 0x34, 0x46, 0x58, 0x6A, 0x7C, 0x8E, 0x0D, 0x1F, 0x31, 0x43, 0x55, 0x67, 0x79, 0x8B, 0x0A, 0x1C, 0x2E, 0x40, 0x52, 0x64, 0x76, 0x88, 0x07, 0x19, 0x2B, 0x3D, 0x4F, 0x61, 0x73, 0x85, 0x04, 0x16, 0x28, 0x3A, 0x4C, 0x5E, 0x70, 0x82, 0x01, 0x13, 0x25, 0x37, 0x49, 0x5B, 0x6D, 0x7F]   # Blue
    ]
}


class RGBLEDRing(RGBLED):
    def __init__(self, config):
        super().__init__()
        self.init = init
        self.instances = []

        self.i2c_instance = config.get("i2c_instance", 1)
        self.i2c_addrs = config.get("i2c_addrs", [0x20])
        self.master = config.get("master", False)

        if self.i2c_instance == 2:
            self.init.init_i2c_2()
            self.i2c = self.init.i2c_2
            self.mutex = self.init.i2c_2_mutex
        else:
            self.init.init_i2c_1()
            self.i2c = self.init.i2c_1
            self.mutex = self.init.i2c_1_mutex

        instance_key = len(self.init.rgb_led_instances["rgb_led_ring"])
        for i, addr in enumerate(self.i2c_addrs):
            led_instance = RGB_RGBLEDRing(
                i2c=self.i2c,
                i2c_addr=addr,
                mutex=self.mutex,
                config=config
            )
            self.instances.append(led_instance)

        print(f"RGB LED Ring {instance_key} initialized on I2C_{self.i2c_instance}")
        for i, addr in enumerate(self.i2c_addrs):
            print(f"- {i + 1}: I2C address 0x{addr:02X}{' (master)' if self.master else ''}")
        print(f"- Offset: {config.get('offset', 0)}")
        print(f"- Reverse: {config.get('reverse', False)}")
        print(f"- Mode: {config.get('mode', None)}")


class RGB_RGBLEDRing(RGB):
    def __init__(
        self,
        i2c,
        i2c_addr,
        mutex,
        config,
    ):
        super().__init__()
        self.i2c = i2c
        self.i2c_addr = i2c_addr
        self.mutex = mutex
        self.init = init
        self.num_leds = 48
        self.threshold_brightness = config.get("threshold_brightness", 2)
        self.full_brightness = config.get("full_brightness", 40)
        self.default_color = self._get_default_color(config.get("default_color", "vu_meter"))
        self.step_delay = config.get("delay_between_steps", 0)
        self.offset = config.get("offset", 0)
        self.reverse = config.get("reverse", False)
        self.mode = config.get("mode", "vu_meter")
        self.vu_meter_sensitivity = config.get("vu_meter_sensitivity", 1)
        self.vu_meter_colors = config.get("vu_meter_colors", [])
        self.led_ring = None
        self.master = config.get("master", False)
        self.class_name = self.__class__.__name__

        self._initialize_led_ring()

    def _get_default_color(self, default_color):
        if default_color == "vu_meter":
            return None
        return hex_to_rgb(default_color)

    def _initialize_led_ring(self):
        self.Reset()
        time.sleep(0.02)
        self.ClearAll()
        self.Configuration(0x01) # Normal operation
        self.SpreadSpectrum(0b0010110)
        self.GlobalCurrent(0xFf) # maximum current output
        self.SetScalingAll(0xFF)
        self.PWM_MODE()
        self.ClearAll()
        self.off()

    def off(self, output=None):
        colors = [self.default_color if self.default_color else self.vu_meter_colors[i] for i in range(self.num_leds)]
        self._set_rgb_batch(colors, [self.threshold_brightness] * self.num_leds)

    def set_status(self, output, freq, on_time, max_duty=None, max_on_time=None):
        if self.mode == "status":
            color = status_color(freq, on_time, max_duty, max_on_time)
            colors = [color] * self.num_leds
            self._set_rgb_batch(colors, [self.threshold_brightness] * self.num_leds)
        else:
            level = calculate_percent(freq, on_time, max_duty, max_on_time) / 100.0
            num_bright_leds = min(max(int(self.num_leds * level + self.vu_meter_sensitivity), 0), self.num_leds)
            self.show_level(num_bright_leds)

    def set_level(self, level):
        """
        Sets the LED level based on a percentage value (0-100).

        Parameters:
        ----------
        level : float or int
            The percentage level (0 to 100) to set the LEDs.
        """
        if level == 0:
            self.off()
            return
        # Calculate number of bright LEDs based on percentage.
        num_bright_leds = round((level / 100) * self.num_leds)
        
        # Ensure num_bright_leds is within valid range.
        num_bright_leds = max(0, min(self.num_leds, num_bright_leds))
        
        # Call show_level to update the LEDs.
        self.show_level(num_bright_leds)

    def show_level(self, num_bright_leds):
        colors = []
        brightness_values = []
        for i in range(self.num_leds):
            if i < num_bright_leds:
                colors.append(self.vu_meter_colors[i])
                brightness_values.append(self.full_brightness)
            else:
                colors.append(self.default_color if self.default_color else self.vu_meter_colors[i])
                brightness_values.append(self.threshold_brightness)
        self._set_rgb_batch(colors, brightness_values)

    # Functions from:
    # https://github.com/Fattoresaimon/ArduinoDuPPaLib/blob/master/src/LEDRing.cpp
    def PWM_MODE(self):
        self.selectBank(CONSTANTS["ISSI3745_PAGE0"])

    def Configuration(self, conf):
        self.selectBank(CONSTANTS["ISSI3745_PAGE2"])
        self.writeRegister8(CONSTANTS["ISSI3745_CONFIGURATION"], conf)

    def SetScalingAll(self, scal):
        self.selectBank(CONSTANTS["ISSI3745_PAGE1"])
        for i in range(1, 145):
            self.writeRegister8(i, scal)

    def GlobalCurrent(self, curr):
        self.selectBank(CONSTANTS["ISSI3745_PAGE2"])
        self.writeRegister8(CONSTANTS["ISSI3745_GLOBALCURRENT"], curr)

    def SpreadSpectrum(self, spread):
        self.selectBank(CONSTANTS["ISSI3745_PAGE2"])
        self.writeRegister8(CONSTANTS["ISSI3745_SPREADSPECTRUM"], spread)

    def Reset(self):
        self.selectBank(CONSTANTS["ISSI3745_PAGE2"]);
        self.writeRegister8(CONSTANTS["ISSI3745_RESET_REG"], 0xAE);

    def ClearAll(self):
        self.PWM_MODE()
        data = [0] * 144
        self.writeBuff(1, data, 144)

    def selectBank(self, b):
        self.writeRegister8(CONSTANTS["ISSI3745_COMMANDREGISTER_LOCK"], CONSTANTS["ISSI3745_ULOCK_CODE"])
        self.writeRegister8(CONSTANTS["ISSI3745_COMMANDREGISTER"], b)

    def writeRegister8(self, reg, data):
        self.init.mutex_acquire(self.mutex, f"{self.class_name}:writeRegister8")
        try:
            self.i2c.writeto_mem(self.i2c_addr, reg, bytes([data]))
        finally:
            self.init.mutex_release(self.mutex, f"{self.class_name}:writeRegister8")

    def writeBuff(self, reg, data, dim):
        if isinstance(data, (bytes, bytearray)):
            buffer = data[:dim]
        else:
            buffer = bytes(data[:dim])
        self.init.mutex_acquire(self.mutex, f"{self.class_name}:writeBuff")
        try:
            self.i2c.writeto_mem(self.i2c_addr, reg, buffer)
        finally:
            self.init.mutex_release(self.mutex, f"{self.class_name}:writeBuff")

    def Set_RGB(self, led_n, color, brightness=255):
        if not 0 <= led_n < 48:
            raise ValueError("LED index must be 0-47")
        if not 0 <= color <= 0xFFFFFF:
            raise ValueError("Color must be 0-0xFFFFFF")
        if brightness is not None and not 0 <= brightness <= 255:
            raise ValueError("Brightness must be 0-255 or None")
        self.selectBank(CONSTANTS["ISSI3745_PAGE0"])
        r = (color >> 16) & 0xFF
        g = (color >> 8) & 0xFF
        b = color & 0xFF
        scaled_r, scaled_g, scaled_b = scale_rgb(r, g, b, brightness)
        physical_led = (led_n - self.offset) % self.num_leds
        if self.reverse:
            physical_led = self.num_leds - 1 - physical_led
        data = [scaled_b, scaled_g, scaled_r]  # Blue, green, red order
        start_reg = CONSTANTS["ISSI_LED_MAP"][2][physical_led]  # Start at blue
        self.writeBuff(start_reg, data, 3)

    def SetAll_RGB(self, color, brightness=255):
        if not 0 <= color <= 0xFFFFFF:
            raise ValueError("Color must be 0-0xFFFFFF")
        if brightness is not None and not 0 <= brightness <= 255:
            raise ValueError("Brightness must be 0-255 or None")
        self.selectBank(CONSTANTS["ISSI3745_PAGE0"])
        r = (color >> 16) & 0xFF
        g = (color >> 8) & 0xFF
        b = color & 0xFF
        scaled_r, scaled_g, scaled_b = scale_rgb(r, g, b, brightness)
        data = [0] * 144
        for i in range(48):
            data[CONSTANTS["ISSI_LED_MAP"][0][i] - 1] = scaled_r  # Red
            data[CONSTANTS["ISSI_LED_MAP"][1][i] - 1] = scaled_g  # Green
            data[CONSTANTS["ISSI_LED_MAP"][2][i] - 1] = scaled_b  # Blue
        writeBuff(1, data, 144)

    def _set_rgb_batch(self, colors, brightness_values):
        self.selectBank(CONSTANTS["ISSI3745_PAGE0"])
        data = [0] * 144
        for i in range(min(len(colors), self.num_leds)):
            color = colors[i]
            if isinstance(color, (tuple, list)):
                r, g, b = color  # Unpack RGB tuple or list
            else:
                r = (color >> 16) & 0xFF
                g = (color >> 8) & 0xFF
                b = color & 0xFF
            scaled_r, scaled_g, scaled_b = scale_rgb(r, g, b, brightness_values[i])
            physical_led = (i - self.offset) % self.num_leds
            if self.reverse:
                physical_led = self.num_leds - 1 - physical_led
            data[CONSTANTS["ISSI_LED_MAP"][0][physical_led] - 1] = scaled_r
            data[CONSTANTS["ISSI_LED_MAP"][1][physical_led] - 1] = scaled_g
            data[CONSTANTS["ISSI_LED_MAP"][2][physical_led] - 1] = scaled_b
        self.writeBuff(1, data, 144)
