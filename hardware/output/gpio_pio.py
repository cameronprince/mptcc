"""
MicroPython Tesla Coil Controller (MPTCC)
by Cameron Prince
teslauniverse.com

hardware/output/gpio_pio.py
Class for driving outputs with PIO PWM.
"""

from machine import Pin, freq
from rp2 import PIO, StateMachine, asm_pio
from ...lib import utils
from ...hardware.init import init
from ..output.output import Output

@asm_pio(set_init=PIO.OUT_LOW)
def pwm_program():
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
    jmp(not_x, "rest")           # If X is zero, rest.
    wrap()                          # Continue playing the tone.

class GPIO_PIO(Output):
    def __init__(self):
        super().__init__()
        self.init = init

        # PIO state machine clock frequency (125 MHz).
        self.state_machine_frequency = freq()

        # Set up PIO and state machines for each output pin.
        self.output = [
            StateMachine(0, pwm_program, set_base=Pin(self.init.PIN_OUTPUT_1)),
            StateMachine(1, pwm_program, set_base=Pin(self.init.PIN_OUTPUT_2)),
            StateMachine(2, pwm_program, set_base=Pin(self.init.PIN_OUTPUT_3)),
            StateMachine(3, pwm_program, set_base=Pin(self.init.PIN_OUTPUT_4))
        ]

        # Ensure state machines are initially inactive.
        for sm in self.output:
            sm.active(0)

    def set_output(self, output, active, frequency=None, on_time=None, max_duty=None, max_on_time=None):
        """
        Sets the output based on the provided parameters.

        Parameters:
        ----------
        output : int
            The index of the output to be set.
        active : bool
            Whether the output should be active.
        frequency : int, optional
            The frequency of the output signal.
        on_time : int, optional
            The on time of the output signal in microseconds.

        Raises:
        -------
        ValueError
            If frequency or on_time is not provided when activating the output.
        """
        # Get the state machine for the current output.
        sm = self.output[output]

        if active:
            if frequency is None or on_time is None:
                raise ValueError("Frequency and on_time must be provided when activating the output.")

            frequency = int(frequency)
            on_time = int(on_time)

            # Calculate the half period.
            state_machine_frequency = self.state_machine_frequency
            half_period = int(state_machine_frequency / frequency / 2)

            # Deactivate the state machine to change configuration.
            sm.active(0)

            # Load the half period into the PIO state machine.
            sm.put(half_period)

            # Start the state machine.
            sm.active(1)

            # The triggering class is passed for any screen which allows
            # variable signal constraints. The constraints are then used to
            # determine the output percentage level of the current signal.
            if max_duty and max_on_time:
                percent = utils.calculate_percent(frequency, on_time, max_duty, max_on_time)
                self.init.rgb_led[output].status_color(percent)
            else:
                # MIDI signal constraints are fixed at 0-127 by the standard.
                percent = utils.calculate_midi_percent(frequency, on_time)
                self.init.rgb_led[output].status_color(percent)
        else:
            # Stop the state machine.
            sm.active(0)
            self.init.rgb_led[output].off()
