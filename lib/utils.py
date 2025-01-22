"""
MicroPython Tesla Coil Controller (MPTCC)
by Cameron Prince
teslauniverse.com

utils.py
Shared utility functions.
"""

def calculate_percent(frequency, on_time, max_duty):
    """
    Calculates the percentage value based on frequency, on_time, and max_duty.

    Parameters:
    ----------
    frequency : int
        The frequency of the signal.
    on_time : int
        The on time of the signal in microseconds.
    max_duty : float
        The maximum duty cycle as a percentage.

    Returns:
    -------
    int
        The calculated percentage value.
    """
    max_on_time = (max_duty / 100) * (1000000 / frequency)
    percent = (on_time / max_on_time) * 100
    return int(max(0, min(100, percent)))

def midi_to_frequency(note):
    """
    Converts a MIDI note number to frequency.

    Parameters:
    ----------
    note : int
        The MIDI note number.

    Returns:
    -------
    float
        The frequency corresponding to the MIDI note number.
    """
    frequency = int(440 * 2 ** ((note - 69) / 12))
    return frequency

def velocity_to_ontime(velocity):
    """
    Calculates the pulse width based on velocity.

    Parameters:
    ----------
    velocity : int
        The velocity of the note.

    Returns:
    -------
    int
        The calculated pulse width.
    """
    ontime = int((velocity / 127) * 100)
    return ontime

