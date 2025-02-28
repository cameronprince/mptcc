"""
MicroPython Tesla Coil Controller (MPTCC)
by Cameron Prince
teslauniverse.com

hardware/rgb_led/wombat_18ab.py
RGB LED device utilizing the Serial Wombat 18AB board via I2C.
"""

import _thread
from machine import Pin
from SerialWombat_mp_i2c import SerialWombatChip_mp_i2c as driver
from SerialWombatPWM import SerialWombatPWM_18AB as swpwm
from ..rgb_led.rgb_led import RGBLED, RGB
from ...hardware.init import init

class Wombat_18AB(RGBLED):
    """
    Attributes:
    -----------
    init : object
        The initialization object containing configuration and hardware settings.
    driver : SerialWombat_mp_i2c
        The SerialWombat_mp_i2c driver instance.
    """

    def __init__(self):
        """
        Constructs all the necessary attributes for the Wombat_18AB object.
        """
        super().__init__()
        self.init = init
        self.init_delay = self.init.RGB_WOMBAT_18AB_INIT_DELAY

        # Prepare the I2C bus.
        if self.init.RGB_WOMBAT_18AB_I2C_INSTANCE == 2:
            self.init.init_i2c_2()
            self.i2c = self.init.i2c_2
            self.mutex = self.init.i2c_2_mutex
        else:
            self.init.init_i2c_1()
            self.i2c = self.init.i2c_1
            self.mutex = self.init.i2c_1_mutex

        # Initialize the Wombat 18AB driver.
        self.driver = driver(self.i2c, address=self.init.RGB_WOMBAT_18AB_ADDR)

        # Initialize RGB LEDs.
        self.init.rgb_led = [
            RGB_Wombat_18AB(
                self.driver,
                red_pin=init.RGB_WOMBAT_18AB_LED1_RED,
                green_pin=init.RGB_WOMBAT_18AB_LED1_GREEN,
                blue_pin=init.RGB_WOMBAT_18AB_LED1_BLUE,
                mutex=self.mutex,
            ),
            RGB_Wombat_18AB(
                self.driver,
                red_pin=init.RGB_WOMBAT_18AB_LED2_RED,
                green_pin=init.RGB_WOMBAT_18AB_LED2_GREEN,
                blue_pin=init.RGB_WOMBAT_18AB_LED2_BLUE,
                mutex=self.mutex,
            ),
            RGB_Wombat_18AB(
                self.driver,
                red_pin=init.RGB_WOMBAT_18AB_LED3_RED,
                green_pin=init.RGB_WOMBAT_18AB_LED3_GREEN,
                blue_pin=init.RGB_WOMBAT_18AB_LED3_BLUE,
                mutex=self.mutex,
            ),
            RGB_Wombat_18AB(
                self.driver,
                red_pin=init.RGB_WOMBAT_18AB_LED4_RED,
                green_pin=init.RGB_WOMBAT_18AB_LED4_GREEN,
                blue_pin=init.RGB_WOMBAT_18AB_LED4_BLUE,
                mutex=self.mutex,
            ),
        ]

class RGB_Wombat_18AB(RGB):
    """
    A class for handling RGB LEDs with a Wombat 18AB driver.
    """
    def __init__(self, driver, red_pin, green_pin, blue_pin, mutex):
        super().__init__()
        self.init = init
        self.driver = driver
        self.red_pin = red_pin
        self.green_pin = green_pin
        self.blue_pin = blue_pin
        self.mutex = mutex

        # Initialize PWM outputs for the RGB LED.
        self.red_pwm = swpwm(self.driver)
        self.green_pwm = swpwm(self.driver)
        # self.blue_pwm = swpwm(self.driver)

        # Set up PWM outputs with a frequency of 1 kHz and 0% duty cycle (off).
        self.init.mutex_acquire(self.mutex, "rgb_wombat_18ab:init")
        try:
            self.red_pwm.begin(self.red_pin, 0)
            self.green_pwm.begin(self.green_pin, 0)
            # self.blue_pwm.begin(self.blue_pin, 0)

            # Set the frequency for all PWM outputs.
            self.red_pwm.writeFrequency_Hz(1000)  # 1 kHz
            self.green_pwm.writeFrequency_Hz(1000)
            # self.blue_pwm.writeFrequency_Hz(1000)
        finally:
            self.init.mutex_release(self.mutex, "rgb_wombat_18ab:init")

        # Initialize the LED to off.
        self.setColor(0, 0, 0)

    def setColor(self, r, g, b):
        """
        Sets the color of the RGB LED using the Wombat 18AB driver.

        Parameters:
        ----------
        r : int
            Red value (0-255).
        g : int
            Green value (0-255).
        b : int
            Blue value (0-255).
        """
        # Scale the 8-bit color values (0-255) to 16-bit duty cycles (0-65535).
        red_duty = int((r / 255) * 0xFFFF)
        green_duty = int((g / 255) * 0xFFFF)
        blue_duty = int((b / 255) * 0xFFFF)

        # Acquire the mutex to ensure thread-safe access to the PWM outputs.
        self.init.mutex_acquire(self.mutex, "rgb_wombat_18ab:set_color")
        try:
            # Set the duty cycles for the red, green, and blue channels.
            self.red_pwm.writeDutyCycle(red_duty)
            self.green_pwm.writeDutyCycle(green_duty)
            # self.blue_pwm.writeDutyCycle(blue_duty)
        finally:
            # Release the mutex.
            self.init.mutex_release(self.mutex, "rgb_wombat_18ab:set_color")
