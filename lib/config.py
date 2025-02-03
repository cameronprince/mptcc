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
    """
    A class to provide default configuration values and handle reading and writing
    configuration data for the MicroPython Tesla Coil Controller (MPTCC).

    Attributes:
    -----------
    DEF_INTERRUPTER_MIN_ON_TIME : int
        Default minimum on time for the interrupter in microseconds.
    DEF_INTERRUPTER_MIN_FREQ : int
        Default minimum frequency for the interrupter in Hz.
    DEF_INTERRUPTER_MAX_ON_TIME : int
        Default maximum on time for the interrupter in microseconds.
    DEF_INTERRUPTER_MAX_FREQ : int
        Default maximum frequency for the interrupter in Hz.
    DEF_INTERRUPTER_MAX_DUTY : float
        Default maximum duty cycle for the interrupter in percent.
    DEF_MIDI_FILE_OUTPUT_PERCENTAGE : int
        Default MIDI file output level in percent.
    DEF_MIDI_FILE_SAVE_LEVELS_ON_END: bool
        Save the current levels each time playback ends.
    """

    DEF_INTERRUPTER_MIN_ON_TIME = 20
    DEF_INTERRUPTER_MIN_FREQ = 100
    DEF_INTERRUPTER_MAX_ON_TIME = 300
    DEF_INTERRUPTER_MAX_FREQ = 1000
    DEF_INTERRUPTER_MAX_DUTY = 5.0
    DEF_MIDI_FILE_OUTPUT_PERCENTAGE = 20
    DEF_MIDI_FILE_SAVE_LEVELS_ON_END = False

    @staticmethod
    def read_config():
        """
        Reads configuration data from internal flash memory.

        Returns:
        -------
        dict
            The configuration data read from the flash memory. If the file does not exist 
            or contains invalid data, an empty dictionary is returned.
        """
        try:
            with open(init.CONFIG_PATH, "r") as f:
                config_data = ujson.load(f)
        except (OSError, ValueError):
            config_data = {}
        return config_data

    @staticmethod
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