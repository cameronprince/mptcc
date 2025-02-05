"""
MicroPython Tesla Coil Controller (MPTCC)
by Cameron Prince
teslauniverse.com

hardware/output/pio.py
Class for driving outputs with PIO PWM.
"""

from machine import Pin
from rp2 import PIO, StateMachine, asm_pio
from ...lib import utils
from ...hardware.init import init
from ..output.output import Output

@asm_pio(sideset_init=PIO.OUT_LOW)
def pwm_program():
    pull()              # Pull the high cycle count from the TX FIFO
    mov(x, osr)         # Move the high cycle count to the X register
    pull()              # Pull the low cycle count from the TX FIFO
    mov(y, osr)         # Move the low cycle count to the Y register

    label("high")       # High state loop
    jmp(x_dec, "high")  # Decrement X and loop if X > 0
    set(pins, 1)        # Set the pin high

    label("low")        # Low state loop
    jmp(y_dec, "low")   # Decrement Y and loop if Y > 0
    set(pins, 0)        # Set the pin low

class PIO(Output):
    def __init__(self):
        super().__init__()
        self.init = init

        # Set up PIO and state machines for each output pin
        pio_freq = 125_000_000  # PIO state machine clock frequency (125 MHz)

        # Initialize state machines but keep them inactive
        self.output = [
            StateMachine(0, pwm_program, freq=pio_freq, sideset_base=Pin(self.init.PIN_OUTPUT_1)),
            StateMachine(1, pwm_program, freq=pio_freq, sideset_base=Pin(self.init.PIN_OUTPUT_2)),
            StateMachine(2, pwm_program, freq=pio_freq, sideset_base=Pin(self.init.PIN_OUTPUT_3)),
            StateMachine(3, pwm_program, freq=pio_freq, sideset_base=Pin(self.init.PIN_OUTPUT_4))
        ]

        for sm in self.output:
            sm.active(0)  # Ensure state machines are initially inactive

    def disable_outputs(self):
        """
        Disables all outputs by stopping the state machines and turning off the associated LEDs.
        """
        for sm in self.output:
            sm.active(0)  # Stop the state machines
        for led in self.init.rgb_led:
            led.off()

    def set_output(self, output, active, frequency=None, on_time=None, triggering_class=None):
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
        triggering_class : object, optional
            The class instance containing max_duty, min_on_time, and max_on_time attributes.

        Raises:
        -------
        ValueError
            If frequency or on_time is not provided when activating the output.
        """
        if active:
            if frequency is None or on_time is None:
                raise ValueError("Frequency and on_time must be provided when activating the output.")

            frequency = int(frequency)
            on_time = int(on_time)

            # Calculate the number of cycles for the high and low states
            cycles_per_period = 125_000_000 // frequency  # Total cycles for one period
            high_cycles = int((on_time / 1_000_000) * 125_000_000)  # High time in cycles
            low_cycles = cycles_per_period - high_cycles  # Low time in cycles

            sm = self.output[output]
            sm.active(0)  # Deactivate the state machine to change configuration

            # Load the high and low cycles into the PIO state machine
            sm.put(high_cycles)
            sm.put(low_cycles)

            sm.active(1)  # Start the state machine

            # The triggering class is passed for any screen which allows
            # variable signal constraints. The constraints are then used to
            # determine the output percentage level of the current signal.
            if triggering_class:
                percent = utils.calculate_percent(frequency, on_time, triggering_class)
                self.init.rgb_led[output].status_color(percent)
            else:
                # MIDI signal constraints are fixed at 0-127 by the standard.
                percent = utils.calculate_midi_percent(frequency, on_time)
                self.init.rgb_led[output].status_color(percent)
        else:
            sm = self.output[output]
            sm.active(0)  # Stop the state machine
            self.init.rgb_led[output].off()
