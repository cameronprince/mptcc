"""
MicroPython Tesla Coil Controller (MPTCC)
by Cameron Prince
teslauniverse.com

hardware/output/gpio_timer.py
Class for driving outputs with timers.
"""

from machine import Pin, Timer
import uasyncio as asyncio
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

    def disable_outputs(self):
        # Clear the task queue.
        self.init.task_queue.clear()

        # Disables all outputs and stops all timers.
        for output in self.output:
            output['running'] = False
            output['timer'].deinit()  # Deinitialize the timer.
            output['pin'].value(0)    # Set the pin low.

        # Extinguish each LED.
        for led in self.init.rgb_led:
            led.off()

    def _set_output_timer(self, output, frequency, on_time):
        def toggle_pin(timer):
            output['pin'].toggle()
        output['timer'].init(freq=2 * frequency, mode=Timer.PERIODIC, callback=toggle_pin)

    def _schedule_task(self, coro):
        # Schedule a coroutine to run in the asyncio event loop from another thread.
        self.init.task_queue.put(coro)

    async def _set_output_async(self, output_index, active, frequency=None, on_time=None, triggering_class=None):
        # Asynchronous method to set the output based on the provided parameters.
        output = self.output[output_index]

        if active:
            if frequency is None or on_time is None:
                raise ValueError("Frequency and on_time must be provided when activating the output.")

            frequency = int(frequency)
            on_time = int(on_time)

            output['running'] = True

            self._set_output_timer(output, frequency, on_time)

            if triggering_class:
                percent = utils.calculate_percent(frequency, on_time, triggering_class)
                self.init.rgb_led[output_index].status_color(percent)
            else:
                percent = utils.calculate_midi_percent(frequency, on_time)
                self.init.rgb_led[output_index].status_color(percent)

        else:
            output['running'] = False
            output['timer'].deinit()
            output['pin'].value(0)
            self.init.rgb_led[output_index].off()

    def set_output(self, output_index, active, frequency=None, on_time=None, triggering_class=None):
        # Wrapper method to schedule the asyncio loop/task for setting the output.
        self.init.asyncio_loop.start_loop()
        self._schedule_task(self._set_output_async(output_index, active, frequency, on_time, triggering_class))
