"""
MicroPython Tesla Coil Controller (MPTCC)
by Cameron Prince
teslauniverse.com

utils.py
Shared utility functions.
"""

def calculate_midi_percent(frequency, on_time):
    """
    Calculates the percentage value based on frequency and on_time.

    Parameters:
    ----------
    frequency : int
        The frequency of the signal.
    on_time : int
        The on time of the signal in microseconds.

    Returns:
    -------
    int
        The calculated percentage value.
    """
    # Max velocity is 127 per MIDI spec.
    MAX_VELOCITY = 127
    
    # Calculate the period of the wave in microseconds.
    period = 1_000_000 / frequency 
    
    # Calculate max_on_time using MAX_VELOCITY.
    max_on_time = velocity_to_ontime(MAX_VELOCITY)
    
    # Calculate the max duty cycle.
    max_duty_cycle = max_on_time / period
    
    # Calculate the current duty cycle.
    current_duty_cycle = on_time / period
    
    # Calculate the percentage.
    percent = (current_duty_cycle / max_duty_cycle) * 100

    # Constrain the percentage to be between 0 and 100.
    percent = min(max(int(percent), 0), 100)

    return percent

def calculate_percent(frequency, on_time, max_duty, max_on_time):
    """
    Calculates the percentage value based on frequency, on_time,
    and the provided class instance.

    Parameters:
    ----------
    frequency : int
        The frequency of the signal.
    on_time : int
        The on time of the signal in microseconds.

    Returns:
    -------
    int
        The calculated percentage value.
    """

    # Ensure the on_time does not exceed the maximum allowed on_time.
    on_time = min(on_time, max_on_time)

    # Calculate the maximum on_time based on the max_duty.
    max_on_time_based_on_duty = (max_duty / 100) * (1000000 / frequency)

    # Calculate the percentage based on the on_time.
    percent = (on_time / max_on_time_based_on_duty) * 100

    # Ensure the percentage is within the range of 0 to 100.
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

def calculate_max_on_time(frequency, max_duty, max_on_time):
    """
    Calculates the maximum on time based on the frequency, max duty cycle, and max on time.

    Parameters:
    ----------
    frequency : int
        The frequency to use for the calculation.
    max_duty : float
        The maximum duty cycle (as a percentage).
    max_on_time : int
        The maximum on time in microseconds.

    Returns:
    -------
    int
        The calculated maximum on time in microseconds.
    """
    max_on_time_based_on_duty = (max_duty / 100) * (1000000 / frequency)
    return min(max_on_time, int(max_on_time_based_on_duty))

def calculate_duty_cycle(on_time, frequency):
    """
    Calculates the duty cycle based on the on time and frequency.

    Parameters:
    ----------
    on_time : int
        The on time of the signal in microseconds.
    frequency : int
        The frequency of the signal in Hz.

    Returns:
    -------
    float
        The calculated duty cycle as a percentage.
    """
    period = 1000000 / frequency  # Period in microseconds
    duty_cycle = (on_time / period) * 100
    return duty_cycle

def calculate_on_time(on_time, frequency, max_duty, max_on_time):
    """
    Calculates the on time to ensure the duty cycle does not exceed the
    maximum allowed duty cycle.

    Parameters:
    ----------
    on_time : int
        The current on time in microseconds.
    frequency : int
        The frequency of the signal in Hz.
    max_duty : float
        The maximum allowed duty cycle (as a percentage).
    max_on_time : int
        The maximum allowed on time in microseconds.

    Returns:
    -------
    int
        The updated on time in microseconds.
    """
    max_on_time_allowed = calculate_max_on_time(frequency, max_duty, max_on_time)
    current_duty_cycle = calculate_duty_cycle(on_time, frequency)
    
    if current_duty_cycle > max_duty:
        return max_on_time_allowed
    return on_time
