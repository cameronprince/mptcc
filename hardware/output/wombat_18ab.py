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

class Wombat_18AB(Output):

    def __init__(self):
        """
        Constructs all the necessary attributes for the Wombat_18AB object.
        """
        super().__init__()
        self.init = init

        # Prepare the I2C bus.
        if self.init.OUTPUT_WOMBAT_18AB_I2C_INSTANCE == 2:
            self.init.init_i2c_2()
            self.i2c = self.init.i2c_2
            self.mutex = self.init.i2c_2_mutex
        else:
            self.init.init_i2c_1()
            self.i2c = self.init.i2c_1
            self.mutex = self.init.i2c_1_mutex

        # Instantiate each Output_PCA9685 with a delay between each one.
        self.output = []
        self.output.append(Wombat_18AB(
        ))
        time.sleep(self.init.OUTPUT_WOMBAT_18AB_INIT_DELAY)
        self.output.append(Wombat_18AB(
        ))
        time.sleep(self.init.OUTPUT_PCA9685_INIT_DELAY)
        self.output.append(Wombat_18AB(
        ))
        time.sleep(self.init.OUTPUT_WOMBAT_18AB_INIT_DELAY)
        self.output.append(Wombat_18AB(
        ))
        time.sleep(self.init.OUTPUT_WOMBAT_18AB_INIT_DELAY)

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

            self.init.rgb_led[output].status_color(frequency, on_time, max_duty, max_on_time)
        else:
            output.off()
            self.init.rgb_led[output].off()


class Output_Wombat_18AB:
    """
    A class for handling outputs with a PCA9685 driver.
    """
    def __init__(self):
        super().__init__()

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
        pass

    def off(self):
        pass
