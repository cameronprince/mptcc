"""
MicroPython Tesla Coil Controller (MPTCC)
by Cameron Prince
teslauniverse.com

lib/asyncio.py
Class which integrates asyncio with the MPTCC project.
"""

import uasyncio as asyncio
from machine import Pin, Timer
import _thread
from ..hardware.init import init
from ..hardware.rgb_led.tasks import RGBLEDTasks

class AsyncIOLoop:
    def __init__(self):
        self.loop_running = False
        self.loop = asyncio.get_event_loop()
        self.tasks = []

    async def _keep_alive(self):
        """
        Coroutine to keep the asyncio loop running.
        """
        while True:
            await asyncio.sleep(3600)

    def start_loop(self):
        """
        Start the asyncio event loop and keep it running.
        """
        if not self.loop_running:
            self.loop_running = True
            self.tasks.append(asyncio.create_task(self._keep_alive()))
            try:
                self.loop.run_forever()
            except KeyboardInterrupt:
                pass
            finally:
                self.loop_running = False
                self.loop.close()

    def stop_all_tasks(self):
        """
        Stop all tasks managed by the asyncio loop.
        """
        for task in self.tasks:
            task.cancel()
        self.tasks.clear()

# Create an instance of AsyncIOLoop and put it in the init object.
init.asyncio_loop = AsyncIOLoop()

# Instantiate RGBLEDTasks and add it to the init object.
init.rgb_led_tasks = RGBLEDTasks()
