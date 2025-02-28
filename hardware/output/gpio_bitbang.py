"""
MicroPython Tesla Coil Controller (MPTCC)
by Cameron Prince
teslauniverse.com

hardware/output/gpio_bitbang.py
Class for driving outputs with software PWM (bit banging).
"""

from machine import Pin
from ...lib import utils
from ...hardware.init import init
from ..output.output import Output
import uasyncio as asyncio
import time

class GPIO_BitBang(Output):
    def __init__(self):
        super().__init__()
        self.init = init

        # Define outputs as GPIO pins.
        self.output = [
            Pin(self.init.PIN_OUTPUT_1, Pin.OUT),
            Pin(self.init.PIN_OUTPUT_2, Pin.OUT),
            Pin(self.init.PIN_OUTPUT_3, Pin.OUT),
            Pin(self.init.PIN_OUTPUT_4, Pin.OUT),
        ]

        # Initialize flags and tasks for each output.
        self.running = [False] * 4
        self.tasks = [None] * 4

    async def _bitbang_pwm(self, output, frequency, on_time):
        """
        Generates a PWM signal using bit banging.
        """
        period = 1_000_000 // frequency  # Period in microseconds.
        off_time = period - on_time      # Off time in microseconds.

        while self.running[output]:
            self.output[output].value(1)  # Set pin high.
            await self._sleep_us(on_time)
            self.output[output].value(0)  # Set pin low.
            await self._sleep_us(off_time)

    async def _sleep_us(self, us):
        """
        Busy-wait for the specified number of microseconds.
        """
        start = time.ticks_us()
        while time.ticks_diff(time.ticks_us(), start) < us:
            await asyncio.sleep_ms(0)

    def set_output(self, output, active, frequency=None, on_time=None, max_duty=None, max_on_time=None):
        """
        Sets the output based on the provided parameters.
        """
        if active:
            if frequency is None or on_time is None:
                raise ValueError("Frequency and on_time must be provided when activating the output.")

            frequency = int(frequency)
            on_time = int(on_time)

            # Stop any existing task for this output.
            if self.tasks[output] is not None:
                self.init.task_queue.put(("func", self._cancel_task, (output,)))

            # Start a new task for the PWM generation.
            self.running[output] = True
            # Pass the coroutine itself to the queue.
            self.init.task_queue.put(("coro", self._start_task(output, frequency, on_time)))

            # Handle LED updates.
            self.init.rgb_led[output].set_status(output, frequency, on_time, max_duty, max_on_time)
        else:
            # Stop the PWM generation for this output.
            self.running[output] = False
            if self.tasks[output] is not None:
                self.init.task_queue.put(("func", self._cancel_task, (output,)))
            self.output[output].value(0)  # Set the pin low.
            self.init.rgb_led[output].off(output)  # Extinguish the LED.

    async def _start_task(self, output, frequency, on_time):
        """
        Starts the PWM task for the specified output.
        """
        self.tasks[output] = asyncio.create_task(self._bitbang_pwm(output, frequency, on_time))

    async def _cancel_task(self, output):
        """
        Cancels the PWM task for the specified output.
        """
        if self.tasks[output] is not None:
            self.tasks[output].cancel()
            try:
                await self.tasks[output]  # Await the task to ensure it is properly canceled.
            except asyncio.CancelledError:
                pass
            self.tasks[output] = None
