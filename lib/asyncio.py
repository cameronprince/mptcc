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

"""
The project's output handlers run in a thread on the second core. Therefore,
we must use a thread-safe queue so that methods running on the second core can
start tasks in the asyncio loop running on the first core.
"""
class ThreadSafeQueue:
    def __init__(self):
        self.queue = []
        self.lock = _thread.allocate_lock()

    def put(self, item):
        # Add an item to the queue in a thread-safe manner.
        with self.lock:
            self.queue.append(item)

    def get(self):
        # Retrieve and remove an item from the queue in a thread-safe manner.
        # Returns None if the queue is empty.
        with self.lock:
            if self.queue:
                return self.queue.pop(0)
        return None

    def clear(self):
        # Clear all items from the queue in a thread-safe manner.
        with self.lock:
            self.queue.clear()

class AsyncIOLoop:
    def __init__(self):
        self.loop_running = False
        # Get the event loop.
        self.loop = asyncio.get_event_loop()

    async def _process_tasks(self):
        # Coroutine to process tasks from the thread-safe queue.
        while True:
            task = init.task_queue.get()
            if task:
                asyncio.create_task(task)
            # Poll the queue periodically. Adjust as needed for performance.
            await asyncio.sleep(0.1)

    async def _keep_alive(self):
        # Coroutine to keep the asyncio loop running.
        while True:
            # Sleep for a long time to keep the loop alive.
            await asyncio.sleep(3600)

    def start_loop(self):
        # Start the asyncio event loop and keep it running.
        if not self.loop_running:
            self.loop_running = True
            # Schedule the task processor and keep-alive coroutines.
            asyncio.create_task(self._process_tasks())
            asyncio.create_task(self._keep_alive())
            # Run the event loop forever.
            self.loop.run_forever()

# Create an instance of AsyncIOLoop and put it in the init object.
init.asyncio_loop = AsyncIOLoop()

# Create a thread-safe queue and put it in the init object.
init.task_queue = ThreadSafeQueue()
