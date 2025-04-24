"""
MicroPython Tesla Coil Controller (MPTCC)
by Cameron Prince
teslauniverse.com

hardware/rgb_led/pca9685.py
RGB LED device utilizing the PCA9685 external PWM board.
"""

from machine import Pin, I2C
import ustruct
import time
from ..rgb_led.rgb_led import RGBLED, RGB
from ...hardware.init import init


class PCA9685(RGBLED):
    """
    A class to control RGB LED devices using the PCA9685 external PWM board.
    """

    def __init__(self, config):
        """Constructs all the necessary attributes for the PCA9685_RGBLED object."""
        super().__init__()
        self.init = init

        self.i2c_instance = config.get("i2c_instance", 1)
        self.i2c_addr = config.get("i2c_addr", 0x40)
        self.freq = config.get("freq", 1000)
        self.pins = config.get("pins", [])

        if self.i2c_instance == 2:
            self.init.init_i2c_2()
            self.i2c = self.init.i2c_2
            self.mutex = self.init.i2c_2_mutex
        else:
            self.init.init_i2c_1()
            self.i2c = self.init.i2c_1
            self.mutex = self.init.i2c_1_mutex

        # Initialize the PCA9685 driver.
        self.init.mutex_acquire(self.mutex, "pca9685_rgb_led:init")
        self.driver = PCA9685_Driver(self.i2c, address=self.i2c_addr)
        self.driver.freq(self.freq)
        self.init.mutex_release(self.mutex, "pca9685_rgb_led:init")

        # Generate a unique key for this instance.
        instance_key = len(self.init.rgb_led_instances["pca9685"])

        # Initialize the LEDs based on the pins configuration.
        self.instances = []
        for led_pins in self.pins:
            red_pin, green_pin, blue_pin = led_pins
            led = RGB_PCA9685(
                driver=self.driver,
                red_channel=red_pin,
                green_channel=green_pin,
                blue_channel=blue_pin,
                mutex=self.mutex
            )
            self.instances.append(led)

        # Print initialization details.
        print(f"PCA9685 RGB LED driver {instance_key} initialized on I2C_{self.i2c_instance} at address: 0x{self.i2c_addr:02X}")
        for i, led in enumerate(self.instances):
            print(f"- LED {i + 1}: R={led.red_channel}, G={led.green_channel}, B={led.blue_channel}")


class PCA9685_Driver:
    """
    A class providing low-level functions for communicating with the PCA9685.
    """
    def __init__(self, i2c, address):
        self.i2c = i2c
        self.address = address
        self._write(0x00, 0x00)

    def _write(self, address, value):
        self.i2c.writeto_mem(self.address, address, bytearray([value]))

    def _read(self, address):
        return self.i2c.readfrom_mem(self.address, address, 1)[0]

    def freq(self, freq=None):
        if freq is None:
            return int(25000000.0 / 4096 / (self._read(0xfe) - 0.5))
        prescale = int(25000000.0 / 4096.0 / freq + 0.5)
        old_mode = self._read(0x00)
        self._write(0x00, (old_mode & 0x7F) | 0x10)
        self._write(0xfe, prescale)
        self._write(0x00, old_mode)
        time.sleep_us(5)
        self._write(0x00, old_mode | 0xa1)

    def duty(self, index, value=None, invert=False):
        if value is None:
            data = self.i2c.readfrom_mem(self.address, 0x06 + 4 * index, 4)
            on, off = ustruct.unpack('<HH', data)
            if (on, off) == (0, 4096):
                return 0
            elif (on, off) == (4096, 0):
                return 4095
            return 4095 - off if invert else off
        if not 0 <= value <= 4095:
            raise ValueError("Out of range")
        if invert:
            value = 4095 - value
        self.i2c.writeto_mem(self.address, 0x06 + 4 * index, ustruct.pack('<HH', 0, value))


class RGB_PCA9685(RGB):
    """
    A class for handling RGB LEDs with a PCA9685 driver.
    """
    def __init__(self, driver, red_channel, green_channel, blue_channel, mutex):
        super().__init__()
        self.driver = driver
        self.red_channel = red_channel
        self.green_channel = green_channel
        self.blue_channel = blue_channel
        self.mutex = mutex
        self.init = init
        self.set_color(0, 0, 0)

    def set_color(self, r, g, b):
        """
        Sets the color of the RGB LED using the PCA9685 driver.
        If any channel (red, green, or blue) is None, it will be skipped.

        Parameters:
        ----------
        r : int
            Red value (0-255).
        g : int
            Green value (0-255).
        b : int
            Blue value (0-255).
        """
        self.init.mutex_acquire(self.mutex, "rgb_pca9685:set_color")
        try:
            if self.red_channel is not None:
                self.driver.duty(self.red_channel, r * 16)
            if self.green_channel is not None:
                self.driver.duty(self.green_channel, g * 16)
            if self.blue_channel is not None:
                self.driver.duty(self.blue_channel, b * 16)
        finally:
            self.init.mutex_release(self.mutex, "rgb_pca9685:set_color")
