"""
MicroPython Tesla Coil Controller (MPTCC)
by Cameron Prince
teslauniverse.com

config.py
Provides default configuration values.
"""

from mptcc.hardware.init import init
import ujson

class Config:

    # Default minimum on time for the interrupter in microseconds
    DEF_INTERRUPTER_MIN_ON_TIME = 20

    # Default minimum frequency for the interrupter in Hz
    DEF_INTERRUPTER_MIN_FREQ = 100

    # Default maximum on time for the interrupter in microseconds
    DEF_INTERRUPTER_MAX_ON_TIME = 300

    # Default maximum frequency for the interrupter in Hz
    DEF_INTERRUPTER_MAX_FREQ = 1000

    # Default maximum duty cycle for the interrupter in percent
    DEF_INTERRUPTER_MAX_DUTY = 5.0

    def read_config():
        """
        Reads configuration data from internal flash memory.

        Returns:
        -------
        dict
            The configuration data read from the flash memory. If the file does not exist or contains invalid data, an empty dictionary is returned.
        """
        try:
            with open(init.CONFIG_PATH, "r") as f:
                config_data = ujson.load(f)
        except (OSError, ValueError):
            config_data = {}
        return config_data

    def write_config(config_data):
        """
        Writes configuration data to internal flash memory.

        Parameters:
        ----------
        config_data : dict
            The configuration data to be written to the flash memory.
        """
        with open(init.CONFIG_PATH, "w") as f:
            ujson.dump(config_data, f)
