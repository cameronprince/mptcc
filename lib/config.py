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
    """

    # Interrupter variables.
    INTERRUPTER_MIN_ON_TIME_MIN = 1
    INTERRUPTER_MIN_ON_TIME_DEF = 20        # Default minimum on time for the interrupter in microseconds.
    INTERRUPTER_MIN_ON_TIME_MAX = 100
    INTERRUPTER_MIN_FREQ_MIN = 100
    INTERRUPTER_MIN_FREQ_DEF = 100          # Default minimum frequency for the interrupter in Hz.
    INTERRUPTER_MIN_FREQ_MAX = 1000
    INTERRUPTER_MAX_ON_TIME_MIN = 1
    INTERRUPTER_MAX_ON_TIME_DEF = 300       # Default maximum on time for the interrupter in microseconds.
    INTERRUPTER_MAX_ON_TIME_MAX = 1000
    INTERRUPTER_MAX_FREQ_MIN = 100
    INTERRUPTER_MAX_FREQ_DEF = 1000         # Default maximum frequency for the interrupter in Hz.
    INTERRUPTER_MAX_FREQ_MAX = 2550
    INTERRUPTER_MAX_DUTY_MIN = 0.25
    INTERRUPTER_MAX_DUTY_DEF = 5.0          # Default maximum duty cycle for the interrupter in percent.
    INTERRUPTER_MAX_DUTY_MAX = 25.0

    # MIDI File variables.
    DEF_MIDI_FILE_OUTPUT_LEVEL = 20         # Default MIDI file output level in percent.
    DEF_MIDI_FILE_AUTO_SAVE_LEVELS = False  # Automatically save the current levels each time playback ends.

    # ASRG variables.
    ARSG_MIN_LINE_FREQ_MIN = 1
    ARSG_MIN_LINE_FREQ_DEF = 1
    ARSG_MIN_LINE_FREQ_MAX = 120
    ARSG_MIN_ON_TIME_MIN = 1
    ARSG_MIN_ON_TIME_DEF = 20
    ARSG_MIN_ON_TIME_MAX = 100
    ARSG_MIN_FREQ_MIN = 100
    ARSG_MIN_FREQ_DEF = 100
    ARSG_MIN_FREQ_MAX = 1000
    ARSG_MAX_LINE_FREQ_MIN = 1
    ARSG_MAX_LINE_FREQ_DEF = 120
    ARSG_MAX_LINE_FREQ_MAX = 400
    ARSG_MAX_ON_TIME_MIN = 1
    ARSG_MAX_ON_TIME_DEF = 300
    ARSG_MAX_ON_TIME_MAX = 1000
    ARSG_MAX_FREQ_MIN = 100
    ARSG_MAX_FREQ_DEF = 1000
    ARSG_MAX_FREQ_MAX = 2550
    ARSG_MAX_DUTY_MIN = 0.25
    ARSG_MAX_DUTY_DEF = 5.0
    ARSG_MAX_DUTY_MAX = 25.0

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
