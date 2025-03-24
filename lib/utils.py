"""
MicroPython Tesla Coil Controller (MPTCC)
by Cameron Prince
teslauniverse.com

lib/utils.py
Shared utility functions.
"""

def calculate_duty_cycle(on_time, freq):
    """
    Calculate the duty cycle for a given on_time and frequency.

    Parameters:
    ----------
    on_time : int
        The on time of the output signal in microseconds.
    freq : int
        The frequency of the output signal in Hz.

    Returns:
    -------
    int
        The duty cycle value.
    """
    return int((on_time / (1_000_000 / freq)) * 65535)

def calculate_percent(freq, on_time, max_duty=None, max_on_time=None):
    """
    Calculates the percentage value based on frequency, on_time,
    and optional constraints. If max_duty and max_on_time are not provided,
    it defaults to MIDI constraints (max_duty=5%, max_on_time based on MIDI velocity).

    Parameters:
    ----------
    freq : int
        The frequency of the signal.
    on_time : int
        The on time of the signal in microseconds.
    max_duty : float, optional
        The maximum allowed duty cycle (as a percentage). Defaults to 5% for MIDI.
    max_on_time : int, optional
        The maximum allowed on time in microseconds. Defaults to MIDI-based max_on_time.

    Returns:
    -------
    int
        The calculated percentage value (1–100).
    """
    # If max_duty and max_on_time are not provided, use MIDI constraints.
    if max_duty is None or max_on_time is None:
        # Max velocity is 127 per MIDI spec.
        MAX_VELOCITY = 127
        max_on_time = velocity_to_ontime(MAX_VELOCITY)
        max_duty = 5  # Adjusted from 100 to 5 for MIDI playback

    # Ensure the on_time does not exceed the maximum allowed on_time.
    on_time = min(on_time, max_on_time)

    # Calculate the maximum on_time based on the max_duty.
    max_on_time_based_on_duty = calculate_max_on_time_based_on_duty(freq, max_duty)

    # Calculate the percentage based on the on_time.
    percent = (on_time / max_on_time_based_on_duty) * 100

    # Ensure the percentage is within the range of 1 to 100.
    percent = constrain(percent, 1, 100)

    # Debugging: Print inputs and outputs
    # print(f"[DEBUG] calculate_percent: freq={freq}, on_time={on_time}, max_duty={max_duty}, max_on_time={max_on_time}, percent={percent}")

    return int(percent)

def calculate_max_on_time_based_on_duty(freq, max_duty):
    """
    Calculates the maximum allowed on-time based on the duty cycle and frequency.

    Parameters:
    ----------
    freq : int
        The frequency of the signal.
    max_duty : float
        The maximum allowed duty cycle (as a percentage).

    Returns:
    -------
    float
        The maximum allowed on-time in microseconds.
    """
    # Calculate the period in microseconds.
    period = 1_000_000 / freq
    
    # Calculate the maximum on-time based on the max_duty.
    return (max_duty / 100) * period

def calculate_on_time(on_time, freq, max_duty, max_on_time):
    """
    Calculates the on time to ensure the duty cycle does not exceed the
    maximum allowed duty cycle and on-time.
    
    This function is used by the interrupter and ARSG screens.

    Parameters:
    ----------
    on_time : int
        The current on time in microseconds.
    freq : int
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
    # Calculate the maximum allowed on-time based on the duty cycle.
    max_on_time_based_on_duty = calculate_max_on_time_based_on_duty(freq, max_duty)
    
    # Constrain the on-time to the smaller of the two limits.
    max_on_time_allowed = min(max_on_time, max_on_time_based_on_duty)
    
    # Ensure the on-time does not exceed the maximum allowed value.
    return int(min(on_time, max_on_time_allowed))

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
    freq = int(440 * 2 ** ((note - 69) / 12))
    return freq

def velocity_to_ontime(velocity):
    """
    Converts MIDI velocity to on-time in microseconds.

    Parameters:
    ----------
    velocity : int
        The MIDI velocity (0–127).

    Returns:
    -------
    int
        The calculated on-time in microseconds (0–100).
    """
    return int((velocity / 127) * 100)

def constrain(x, out_min, out_max):
    """
    Constrains a value to be within a specified range and returns it as an integer.

    Parameters:
    ----------
    x : int or float
        The value to be constrained.
    out_min : int
        The minimum value of the range.
    out_max : int
        The maximum value of the range.

    Returns:
    -------
    int
        The constrained value, cast to an integer.
    """
    return int(max(out_min, min(x, out_max)))

def status_color(freq, on_time, max_duty=None, max_on_time=None):
    """
    Calculates the RGB color based on frequency, on_time, and optional constraints.

    Parameters:
    ----------
    freq : int
        The frequency of the signal.
    on_time : int
        The on time of the signal in microseconds.
    max_duty : int, optional
        The maximum duty cycle.
    max_on_time : int, optional
        The maximum on time.

    Returns:
    -------
    tuple
        RGB values (red, green, blue).
    """
    value = calculate_percent(freq, on_time, max_duty, max_on_time)

    # Debugging: Print inputs and outputs
    # print(f"[DEBUG] status_color: freq={freq}, on_time={on_time}, max_duty={max_duty}, max_on_time={max_on_time}, value={value}")

    # Map value to a range of 0 to 1.
    normalized_value = value / 100.0

    # Transition from green to red at normalized_value = 0.5.
    if normalized_value < 0.5:
        red_value = int((normalized_value * 2) ** 2 * 255)
        green_value = 255
    else:
        green_value = 256 - int(((normalized_value - 0.5) * 2) ** 2 * 255)
        red_value = 255

    # Constrain the RGB values to be within 0-255.
    red = constrain(red_value, 0, 255)
    green = constrain(green_value, 0, 255)
    blue = 0

    # Debugging: Print final RGB values
    # print(f"[DEBUG] status_color: RGB=({red}, {green}, {blue})")

    return red, green, blue

def hex_to_rgb(hex_color):
    """
    Convert a hex color code to an RGB tuple.

    Parameters:
    ----------
    hex_color : str
        The hex color code (e.g., "#326400").

    Returns:
    -------
    tuple
        The RGB color as a tuple (R, G, B).
    """
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
