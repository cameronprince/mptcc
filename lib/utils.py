"""
MicroPython Tesla Coil Controller (MPTCC)
by Cameron Prince
teslauniverse.com

utils.py
Shared utility functions.
"""

def calculate_percent(frequency, on_time, triggering_class):
    """
    Calculates the percentage value based on frequency, on_time, and the provided class instance.

    Parameters:
    ----------
    frequency : int
        The frequency of the signal.
    on_time : int
        The on time of the signal in microseconds.
    triggering_class : object
        The class instance containing max_duty, min_on_time, and max_on_time attributes.

    Returns:
    -------
    int
        The calculated percentage value.
    """
    max_duty = triggering_class.max_duty
    max_on_time = triggering_class.max_on_time

    # Ensure the on_time does not exceed the maximum allowed on_time
    on_time = min(on_time, max_on_time)

    # Calculate the maximum on_time based on the max_duty
    max_on_time_based_on_duty = (max_duty / 100) * (1000000 / frequency)

    # Calculate the percentage based on the on_time
    percent = (on_time / max_on_time_based_on_duty) * 100

    # Ensure the percentage is within the range of 0 to 100
    percent = int(round(max(0, min(100, percent))))

    return percent

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
