"""
MicroPython Tesla Coil Controller (MPTCC)
by Cameron Prince
teslauniverse.com

hardware/output/gpio_bitbang.py
Class for driving outputs with software PWM (bit banging).
"""

from machine import Pin
from ..output.output import Output
import uasyncio as asyncio
import time


class Output_GPIO_BitBang:
    """
    A class to wrap a single bit-banged PWM output and provide output control.
    """
    def __init__(self, pin):
        """
        Initialize the Output_GPIO_BitBang instance.

        Parameters:
        ----------
        pin : int
            The GPIO pin number for the bit-banged PWM output.
        """
        self.pin = pin
        self.output = Pin(pin, Pin.OUT) if pin is not None else None
        self.running = False  # Flag to control task execution.
        self.task = None      # Stores the asyncio task.

    async def _bitbang_pwm(self, frequency, on_time, max_duty=None, max_on_time=None):
        """
        Generates a PWM signal using bit banging.
        """
        period = 1_000_000 // frequency  # Period in microseconds.
        off_time = period - on_time       # Off time in microseconds.

        while self.running:  # Loop until self.running is False.
            self.output.value(1)  # Set pin high.
            await self._sleep_us(on_time)
            self.output.value(0)  # Set pin low.
            await self._sleep_us(off_time)

        # Clean up after the loop ends.
        self.output.value(0)  # Ensure the pin is low.
        self.task = None     # Clear the task reference.

    async def _sleep_us(self, us):
        """
        Busy-wait for the specified number of microseconds.
        """
        start = time.ticks_us()
        while time.ticks_diff(time.ticks_us(), start) < us:
            await asyncio.sleep_ms(0)

    def set_output(self, active=False, freq=None, on_time=None):
        """
        Sets the output based on the provided parameters.

        Parameters:
        ----------
        active : bool, optional
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
        if self.output is None:
            return  # Skip if the pin is not configured.

        if active:
            if freq is None or on_time is None:
                raise ValueError("Frequency and on_time must be provided when activating the output.")

            freq = int(freq)
            on_time = int(on_time)

            # Stop any existing task for this output.
            if self.task is not None:
                self._cancel_task()

            # Start a new task for the PWM generation.
            self.running = True
            self._start_task(freq, on_time)
        else:
            # Stop the PWM generation for this output.
            self.running = False
            if self.task is not None:
                self._cancel_task()
            self.output.value(0)  # Set the pin low.

    def _start_task(self, frequency, on_time):
        """
        Starts the PWM task for this output.
        """
        self.task = asyncio.create_task(self._bitbang_pwm(frequency, on_time))

    def _cancel_task(self):
        """
        Cancels the PWM task for this output.
        """
        if self.task is not None:
            # Signal the task to stop by setting self.running to False.
            self.running = False
            # Wait for the task to clean up and exit.
            while self.task is not None:
                asyncio.sleep_ms(10)  # Yield control to allow the task to exit.


class GPIO_BitBang(Output):
    def __init__(self, pins):
        """
        Initialize the GPIO_BitBang driver.

        Parameters:
        ----------
        pins : list of int
            A list of GPIO pin numbers for bit-banged PWM outputs.
        """
        super().__init__()

        # Initialize Output_GPIO_BitBang instances for the provided pins.
        self.instances = [Output_GPIO_BitBang(pin) for pin in pins]

        # Print initialization details.
        print(f"GPIO_BitBang driver initialized")
        for i, pin in enumerate(pins):
            if pin is not None:
                print(f"- Output {i}: GPIO {pin}")
