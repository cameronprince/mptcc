"""
MicroPython Tesla Coil Controller (MPTCC)
by Cameron Prince
teslauniverse.com

hardware/output/pca9685.py
Class for driving outputs with PCA9685 external PWM.
"""

from machine import Pin
from pca9685 import PCA9685 as driver
from ...lib import utils
from ...hardware.init import init
from ..output.output import Output
import time  # Import the time module for delays

class PCA9685(Output):

    I2C_BUS    = 1
    PCA_1_ADDR = 0x60
    PCA_1_CHAN = 0
    PCA_2_ADDR = 0x50
    PCA_2_CHAN = 0
    PCA_3_ADDR = 0x48
    PCA_3_CHAN = 0
    PCA_4_ADDR = 0x44
    PCA_4_CHAN = 0
    INIT_DELAY = 0.2

    def __init__(self):
        """
        Constructs all the necessary attributes for the PCA9685 object.
        """
        super().__init__()
        self.init = init

        # Prepare the I2C bus.
        if (self.I2C_BUS == 1):
            self.init.init_i2c_1()
            self.i2c = self.init.i2c_1
        else:
            self.init.init_i2c_2()
            self.i2c = self.init.i2c_2

        # Instantiate each Output_PCA9685 with a delay between each one
        self.output = []
        self.output.append(Output_PCA9685(driver(self.i2c, address=self.PCA_1_ADDR), channel=self.PCA_1_CHAN))
        time.sleep(self.INIT_DELAY)
        self.output.append(Output_PCA9685(driver(self.i2c, address=self.PCA_2_ADDR), channel=self.PCA_2_CHAN))
        time.sleep(self.INIT_DELAY)
        self.output.append(Output_PCA9685(driver(self.i2c, address=self.PCA_3_ADDR), channel=self.PCA_3_CHAN))
        time.sleep(self.INIT_DELAY)
        self.output.append(Output_PCA9685(driver(self.i2c, address=self.PCA_4_ADDR), channel=self.PCA_4_CHAN))
        time.sleep(self.INIT_DELAY)

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
        # Get the state machine for the current output.
        driver = self.output[output]

        if active:
            if freq is None or on_time is None:
                raise ValueError("Frequency and on_time must be provided when activating the output.")

            freq = int(freq)
            on_time = int(on_time)

            driver.enable(freq, on_time)

            if max_duty and max_on_time:
                percent = utils.calculate_percent(freq, on_time, max_duty, max_on_time)
                self.init.rgb_led[output].status_color(percent)
            else:
                percent = utils.calculate_midi_percent(freq, on_time)
                self.init.rgb_led[output].status_color(percent)
        else:
            driver.off()
            self.init.rgb_led[output].off()


class Output_PCA9685():
    """
    A class for handling outputs with a PCA9685 driver.
    """
    def __init__(self, pca, channel):
        super().__init__()
        self.pca = pca
        self.channel = channel

    def off(self):
        """
        Turn off the channel's PWM.
        """
        self.pca.duty(self.channel, 0)

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
        # Calculate the period in microseconds.
        period = 1_000_000 / freq
        
        # Calculate the duty cycle as a percentage.
        duty_cycle = (on_time / period) * 100
        
        # Convert the duty cycle to a 12-bit value (0-4095).
        duty_value = int((duty_cycle / 100) * 4095)
        
        # Set the frequency (this affects all channels on the PCA9685).
        self.pca.freq(freq)
        
        # Set the duty cycle for the specific channel.
        self.pca.duty(self.channel, duty_value)