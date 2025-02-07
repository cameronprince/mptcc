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
import _thread

class GPIO_BitBang(Output):
    def __init__(self):
        super().__init__()
        self.init = init

        # Define outputs as GPIO pins.
        self.output = [
            Pin(self.init.PIN_OUTPUT_1, Pin.OUT),
            Pin(self.init.PIN_OUTPUT_2, Pin.OUT),
            Pin(self.init.PIN_OUTPUT_3, Pin.OUT),
            Pin(self.init.PIN_OUTPUT_4, Pin.OUT)
        ]

        # Initialize flags and tasks for each output.
        self.running = [False] * 4
        self.tasks = [None] * 4
        self.lock = _thread.allocate_lock()

    def disable_outputs(self):
        # Shutdown each output.
        for output_idx in range(4):
            self.running[output_idx] = False
            if self.tasks[output_idx] is not None:
                self.tasks[output_idx].cancel()  # Cancel the running task.
                self.tasks[output_idx] = None
            self.output[output_idx].value(0)  # Set the pin low.

        # Extinguish each LED.
        for led in self.init.rgb_led:
            led.off()

    async def _bitbang_pwm(self, output, frequency):
        # Generates a PWM signal using bit banging.
        half_period = 1_000_000 // (2 * frequency)  # Half period in microseconds for 50% duty cycle.

        while self.running[output]:
            self.output[output].value(1)     # Set pin high.
            await asyncio.sleep_ms(half_period // 1000)  # Wait for half the period.
            self.output[output].value(0)     # Set pin low.
            await asyncio.sleep_ms(half_period // 1000)  # Wait for the other half of the period.

    def _schedule_task(self, coro):
        # Schedule a coroutine to run in the asyncio event loop from
        # another thread.
        self.init.task_queue.put(coro)

    def set_output(self, output, active, frequency=None, on_time=None, triggering_class=None):
        # Sets the output based on the provided parameters.
        if active:
            if frequency is None:
                raise ValueError("Frequency must be provided when activating the output.")

            frequency = int(frequency)

            # Stop any existing task for this output.
            if self.tasks[output] is not None:
                self.tasks[output].cancel()

            # Start a new task for the PWM generation.
            self.running[output] = True
            self.tasks[output] = self._schedule_task(self._bitbang_pwm(output, frequency))

            # Handle triggering class and LED updates.
            if triggering_class:
                percent = utils.calculate_percent(frequency, 50, triggering_class)  # Assuming 50% duty cycle.
                self.init.rgb_led[output].status_color(percent)
            else:
                percent = utils.calculate_midi_percent(frequency, 50)  # Assuming 50% duty cycle.
                self.init.rgb_led[output].status_color(percent)
        else:
            # Stop the PWM generation for this output.
            self.running[output] = False
            if self.tasks[output] is not None:
                self.tasks[output].cancel()  # Cancel the running task.
                self.tasks[output] = None
            self.output[output].value(0)     # Set the pin low.
            self.init.rgb_led[output].off()  # Extinguish the LED.
