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
    # Ensure the pin is low when the state machine starts or stops.
    set(pins, 0)                    # Set the pin to low voltage.

    # Rest until a new tone is received.
    label("rest")
    pull(block)                     # Wait for a new high duration, keep it in osr.
    mov(x, osr)                     # Copy the high duration into X.
    jmp(not_x, "rest")              # If high duration is zero, keep resting.

    pull(block)                     # Wait for a new low duration, keep it in osr.
    mov(y, osr)                     # Copy the low duration into Y.

    # Play the tone until a new delay is received.
    wrap_target()                   # Start of the main loop.

    set(pins, 1)                    # Set the pin to high voltage.
    label("high_loop")
    jmp(x_dec, "high_loop")         # Delay for the high state.

    set(pins, 0)                    # Set the pin to low voltage.
    label("low_loop")
    jmp(y_dec, "low_loop")          # Delay for the low state.

    # Read any new high duration. If none, keep the current duration.
    mov(x, osr)                     # Set x, the default value for "pull(noblock)".
    pull(noblock)                   # Read a new high duration or use the default.

    # If the new high duration is zero, rest. Otherwise, continue playing the tone.
    mov(x, osr)                     # Copy the high duration into X.
    jmp(not_x, "rest")              # If X is zero, rest.

    # Read any new low duration. If none, keep the current duration.
    mov(y, osr)                     # Set y, the default value for "pull(noblock)".
    pull(noblock)                   # Read a new low duration or use the default.

    wrap()                          # Continue playing the tone.

class GPIO_PIO(Output):
    def __init__(self):
        super().__init__()
        self.init = init

        # PIO state machine clock frequency (determined dynamically using freq()).
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
        """
        # Get the state machine for the current output.
        sm = self.output[output]

        if active:
            if frequency is None or on_time is None:
                raise ValueError("Frequency and on_time must be provided when activating the output.")

            frequency = int(frequency)
            on_time = int(on_time)

            # Calculate the total period and low state duration.
            state_machine_frequency = self.state_machine_frequency

            period_cycles = int(state_machine_frequency / frequency)  # Total cycles per period.
            high_cycles = int(state_machine_frequency * on_time / 1_000_000)  # Convert on_time to cycles.
            low_cycles = period_cycles - high_cycles  # Remaining cycles for low state.

            # Deactivate the state machine to change configuration.
            sm.active(0)

            # Load the high and low state durations into the PIO state machine.
            sm.put(high_cycles)  # High state duration.
            sm.put(low_cycles)   # Low state duration.

            # Start the state machine.
            sm.active(1)

            # self.init.rgb_led[output].set_status(output, frequency, on_time, max_duty, max_on_time)
        else:
            # Stop the state machine.
            sm.active(0)

            # Explicitly set the pin low.
            sm.exec("set(pins, 0)")

            # Turn off the RGB LED.
            self.init.rgb_led[output].off(output)
