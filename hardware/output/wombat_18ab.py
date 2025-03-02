"""
MicroPython Tesla Coil Controller (MPTCC)
by Cameron Prince
teslauniverse.com

hardware/output/wombat_18ab.py
Class for driving outputs with Serial Wombat 18AB.
"""

import _thread
import time
from machine import Pin, I2C
from ...lib import utils
from ...hardware.init import init
from ..output.output import Output
from SerialWombat_mp_i2c import SerialWombatChip_mp_i2c as driver
from SerialWombatPWM import SerialWombatPWM_18AB as swpwm

class Wombat_18AB(Output):

    def __init__(self):
        """
        Constructs all the necessary attributes for the Wombat_18AB object.
        """
        super().__init__()
        self.init = init
        self.init_delay = self.init.OUTPUT_WOMBAT_18AB_INIT_DELAY

        # Prepare the I2C bus.
        if self.init.OUTPUT_WOMBAT_18AB_I2C_INSTANCE == 2:
            self.init.init_i2c_2()
            self.i2c = self.init.i2c_2
            self.mutex = self.init.i2c_2_mutex
        else:
            self.init.init_i2c_1()
            self.i2c = self.init.i2c_1
            self.mutex = self.init.i2c_1_mutex

        self.driver = driver(self.i2c, self.init.OUTPUT_WOMBAT_18AB_ADDR)

        # Dynamically initialize Output_Wombat_18AB instances based on NUMBER_OF_COILS.
        self.output = []
        for i in range(1, self.init.NUMBER_OF_COILS + 1):
            # Dynamically get the output pin for the current coil.
            pin_attr = f"OUTPUT_WOMBAT_18AB_{i}_PIN"
            if not hasattr(self.init, pin_attr):
                raise ValueError(
                    f"Pin configuration for WOMBAT_18AB output {i} is missing. "
                    f"Please ensure {pin_attr} is defined in main."
                )
            pin = getattr(self.init, pin_attr)

            # Initialize the Output_Wombat_18AB instance.
            self.output.append(Output_Wombat_18AB(
                self.driver,
                pin,
                self.mutex,
            ))
            time.sleep(self.init_delay)

    def set_output(self, output, active, freq=None, on_time=None, max_duty=None, max_on_time=None):
        """
        Sets the output based on the provided parameters.

        Parameters:
        ----------
        output : int
            The index of the output to be set.
        active : bool
            Whether the output should be active.
        freq : int, optional
            The frequency of the output signal.
        on_time : int, optional
            The on time of the output signal in microseconds.

        Raises:
        -------
        ValueError
            If frequency or on_time is not provided when activating the output.
        """
        out = self.output[output]

        if active:
            if freq is None or on_time is None:
                raise ValueError("Frequency and on_time must be provided when activating the output.")

            freq = int(freq)
            on_time = int(on_time)

            out.enable(freq, on_time)

            self.init.rgb_led[output].set_status(output, freq, on_time, max_duty, max_on_time)
        else:
            out.off()
            self.init.rgb_led[output].off(output)


class Output_Wombat_18AB:
    """
    A class for handling outputs with a Serial Wombat 18AB driver.
    """
    def __init__(self, driver, pin, mutex):
        """
        Constructs all the necessary attributes for the Output_Wombat_18AB object.

        Parameters:
        ----------
        driver : SerialWombatChip_mp_i2c
            The Serial Wombat driver instance.
        pin : int
            The pin number on the Serial Wombat chip where the output is connected.
        """
        super().__init__()
        self.driver = driver
        self.pin = pin
        self.mutex = mutex
        self.init = init

        # Initialize the PWM output on the specified pin with a duty cycle of 0 (off).
        self.pwm = swpwm(self.driver)
        self.init.mutex_acquire(self.mutex, "wombat_18ab:begin")
        self.pwm.begin(self.pin, 0)
        self.init.mutex_release(self.mutex, "wombat_18ab:begin")

    def enable(self, freq, on_time):
        """
        Turn on the channel's PWM.

        Parameters:
        ----------
        freq : int
            The frequency of the PWM signal in Hz.
        on_time : int
            The on time of the PWM signal in microseconds.
        """
        # Calculate the duty cycle based on the on_time and frequency.
        period = 1.0 / freq  # Period in seconds.
        period_us = period * 1e6  # Period in microseconds.
        duty_cycle = int((on_time / period_us) * 0xFFFF)  # Convert to 16-bit duty cycle value.

        # Acquire the mutex for both operations.
        self.init.mutex_acquire(self.mutex, "wombat_18ab:enable")

        try:
            # Set the frequency of the PWM signal.
            self.pwm.writeFrequency_Hz(freq)

            # Set the duty cycle.
            self.pwm.writeDutyCycle(duty_cycle)
        finally:
            # Release the mutex.
            self.init.mutex_release(self.mutex, "wombat_18ab:enable")

    def off(self):
        """
        Turn off the channel's PWM.
        """
        # Set the duty cycle to 0 to turn off the output.
        self.init.mutex_acquire(self.mutex, "wombat_18ab:writeDutyCycle")
        self.pwm.writeDutyCycle(0)
        self.init.mutex_release(self.mutex, "wombat_18ab:writeDutyCycle")
