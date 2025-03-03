"""
MicroPython Tesla Coil Controller (MPTCC)
by Cameron Prince
teslauniverse.com

hardware/output/gpio_pio.py
Class for driving outputs with PIO PWM.
"""

from machine import Pin, freq
from rp2 import PIO, StateMachine, asm_pio
from ...hardware.init import init
from ..output.output import Output

@asm_pio(set_init=PIO.OUT_LOW)
def pwm_program():
    # Ensure the pin is low when the state machine starts or stops.
    set(pins, 0)                    # Set the pin to low voltage.

    # Rest until a new tone is received.
    label("rest")
    pull(block)                     # Wait for a new delay value, keep it in osr.
    mov(x, osr)                     # Copy the delay into X.
    jmp(not_x, "rest")              # If new delay is zero, keep resting.

    # Play the tone until a new delay is received.
    wrap_target()                   # Start of the main loop.

    set(pins, 1)                    # Set the pin to high voltage.
    label("high_loop")
    jmp(x_dec, "high_loop")         # Delay.

    set(pins, 0)                    # Set the pin to low voltage.
    mov(x, osr)                     # Load the half period into X.
    label("low_loop")
    jmp(x_dec, "low_loop")          # Delay.

    # Read any new delay value. If none, keep the current delay.
    mov(x, osr)                     # Set x, the default value for "pull(noblock)".
    pull(noblock)                   # Read a new delay value or use the default.

    # If the new delay is zero, rest. Otherwise, continue playing the tone.
    mov(x, osr)                     # Copy the delay into X.
    jmp(not_x, "rest")              # If X is zero, rest.
    wrap()                          # Continue playing the tone.

class GPIO_PIO(Output):
    def __init__(self):
        super().__init__()
        self.init = init

        # PIO state machine clock frequency (125 MHz).
        self.smf = freq()

        # Initialize outputs dynamically.
        self.output = []

        for i in range(1, self.init.NUMBER_OF_COILS + 1):
            # Dynamically get the output pin for the current coil.
            pin_attr = f"PIN_OUTPUT_{i}"
            if not hasattr(self.init, pin_attr):
                raise ValueError(
                    f"Pin configuration for output {i} is missing. "
                    f"Please ensure {pin_attr} is defined in main."
                )
            pin = getattr(self.init, pin_attr)

            # Initialize the state machine for the current output pin.
            sm = StateMachine(i - 1, pwm_program, set_base=Pin(pin))
            self.output.append(sm)

            # Ensure the state machine is initially inactive.
            sm.active(0)

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
            If freq or on_time is not provided when activating the output.
        """
        # Get the state machine for the current output.
        sm = self.output[output]

        if active:
            if freq is None or on_time is None:
                raise ValueError("Frequency and on_time must be provided when activating the output.")

            freq = int(freq)
            on_time = int(on_time)

            # Calculate the half period.
            smf = self.smf
            half_period = int(smf / freq / 2)

            # Deactivate the state machine to change configuration.
            sm.active(0)

            # Load the half period into the PIO state machine.
            sm.put(half_period)

            # Start the state machine.
            sm.active(1)
            self.init.rgb_led[output].set_status(output, freq, on_time, max_duty, max_on_time)     
        else:
            # Stop the state machine.
            sm.active(0)

            # Explicitly set the pin low.
            sm.exec("set(pins, 0)")

            # Turn off the RGB LED.
            self.init.rgb_led[output].off(output)
