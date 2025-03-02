"""
MicroPython Tesla Coil Controller (MPTCC)
by Cameron Prince
teslauniverse.com

hardware/output/pca9685.py
Class for driving outputs with PCA9685 external PWM.
"""

import _thread
import time
from machine import Pin, I2C
from pca9685 import PCA9685 as driver
from ...lib import utils
from ...hardware.init import init
from ..output.output import Output

class PCA9685(Output):

    def __init__(self):
        """
        Constructs all the necessary attributes for the PCA9685 object.
        """
        super().__init__()
        self.init = init

        # Prepare the I2C bus.
        if self.init.OUTPUT_PCA9685_I2C_INSTANCE == 2:
            self.init.init_i2c_2()
            self.i2c = self.init.i2c_2
            self.mutex = self.init.i2c_2_mutex
        else:
            self.init.init_i2c_1()
            self.i2c = self.init.i2c_1
            self.mutex = self.init.i2c_1_mutex

        # Dynamically initialize Output_PCA9685 instances based on NUMBER_OF_COILS
        self.output = []
        for i in range(1, self.init.NUMBER_OF_COILS + 1):
            # Dynamically get the address and channel for the current coil
            addr_attr = f"OUTPUT_PCA9685_{i}_ADDR"
            chan_attr = f"OUTPUT_PCA9685_{i}_CHAN"

            if not hasattr(self.init, addr_attr) or not hasattr(self.init, chan_attr):
                raise ValueError(
                    f"Configuration for PCA9685 output driver {i} is missing. "
                    f"Please ensure {addr_attr} and {chan_attr} are defined in main."
                )

            addr = getattr(self.init, addr_attr)
            chan = getattr(self.init, chan_attr)

            # Initialize the Output_PCA9685 instance
            self.output.append(Output_PCA9685(
                driver(self.i2c, address=addr),
                chan,
                self.mutex,
            ))
            time.sleep(self.init.OUTPUT_PCA9685_INIT_DELAY)

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
        output = self.output[output]

        if active:
            if freq is None or on_time is None:
                raise ValueError("Frequency and on_time must be provided when activating the output.")

            freq = int(freq)
            on_time = int(on_time)

            output.enable(freq, on_time)

            self.init.rgb_led[output].status_color(freq, on_time, max_duty, max_on_time)
        else:
            output.off()
            self.init.rgb_led[output].off()


class Output_PCA9685:
    """
    A class for handling outputs with a PCA9685 driver.
    """
    def __init__(self, driver, channel, mutex):
        super().__init__()
        self.driver = driver
        self.channel = channel
        self.mutex = mutex

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
        self.driver.freq(freq)
        pass

    def off(self):
        pass
