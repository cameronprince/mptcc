"""
MicroPython Tesla Coil Controller (MPTCC)
by Cameron Prince
teslauniverse.com

hardware/output/gpio_timer.py
Class for driving outputs with timers.
"""

from machine import Pin, Timer
from ...lib import utils
from ...hardware.init import init
from ..output.output import Output

class GPIO_Timer(Output):
    def __init__(self):
        super().__init__()
        self.init = init

        # Define outputs as GPIO pins and initialize timers.
        self.output = [
            {'pin': Pin(self.init.PIN_OUTPUT_1, Pin.OUT), 'timer': Timer(), 'running': False},
            {'pin': Pin(self.init.PIN_OUTPUT_2, Pin.OUT), 'timer': Timer(), 'running': False},
            {'pin': Pin(self.init.PIN_OUTPUT_3, Pin.OUT), 'timer': Timer(), 'running': False},
            {'pin': Pin(self.init.PIN_OUTPUT_4, Pin.OUT), 'timer': Timer(), 'running': False}
        ]

    def _set_output_timer(self, output, frequency, on_time):
        """
        Configures a hardware timer to generate a PWM signal on the specified output.

        Parameters:
        ----------
        output : dict
            The output dictionary containing the pin and timer.
        frequency : int
            The frequency of the PWM signal in Hz.
        on_time : int
            The on time of the PWM signal in microseconds.
        """
        period = 1_000_000 // frequency  # Period in microseconds.
        off_time = period - on_time      # Off time in microseconds.

        def toggle_pin(timer):
            output['pin'].toggle()

        # Calculate the timer period and duty cycle.
        timer_period = period    # Timer period in microseconds.
        timer_duty = on_time     # Timer duty cycle in microseconds.

        # Initialize the timer.
        output['timer'].init(
            freq=frequency,      # Set the timer frequency.
            mode=Timer.PERIODIC, # Run the timer in periodic mode.
            callback=toggle_pin  # Callback to toggle the pin.
        )

    def set_output(self, output_index, active, frequency=None, on_time=None, max_duty=None, max_on_time=None):
        """
        Sets the output based on the provided parameters.

        Parameters:
        ----------
        output_index : int
            The index of the output to be set.
        active : bool
            Whether the output should be active.
        frequency : int, optional
            The frequency of the output signal in Hz.
        on_time : int, optional
            The on time of the output signal in microseconds.
        max_duty : int, optional
            The maximum duty cycle allowed.
        max_on_time : int, optional
            The maximum on time allowed in microseconds.

        Raises:
        -------
        ValueError
            If frequency or on_time is not provided when activating the output.
        """
        output = self.output[output_index]

        if active:
            if frequency is None or on_time is None:
                raise ValueError("Frequency and on_time must be provided when activating the output.")

            frequency = int(frequency)
            on_time = int(on_time)

            # Stop the timer if it's already running.
            if output['running']:
                output['timer'].deinit()

            # Configure the timer for PWM generation.
            self._set_output_timer(output, frequency, on_time)
            output['running'] = True

            # Handle LED updates.
            self.init.rgb_led[output].status_color(frequency, on_time, max_duty, max_on_time)
        else:
            # Stop the timer and deactivate the output.
            output['running'] = False
            output['timer'].deinit()
            # Set the pin low.
            output['pin'].value(0)
            # Extinguish the LED.
            self.init.rgb_led[output_index].off()
