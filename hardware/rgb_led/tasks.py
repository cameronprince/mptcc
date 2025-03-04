"""
MicroPython Tesla Coil Controller (MPTCC)
by Cameron Prince
teslauniverse.com

hardware/rgb_led/tasks.py
Asyncio tasks for RGB LED control.
"""

import uasyncio as asyncio
from ...hardware.init import init

class RGBLEDTasks:
    def __init__(self):
        self.rgb_tasks = []
        self.states = {}

    async def update(self):
        """
        Asyncio task to update all RGB LEDs during operation.
        """
        while True:
            if init.RGB_LED_ASYNCIO_POLLING:
                for output, color in init.rgb_led_color.items():
                    if output < len(init.rgb_led) and color:
                        r, g, b = color
                        try:
                            init.rgb_led[output].setColor(r, g, b)
                            self.states[output] = (r, g, b)
                        except Exception as e:
                            print(f"Error updating RGB LED {output}: {e}")
                        init.rgb_led_color[output] = None
            await asyncio.sleep(0.1)

    async def monitor(self, active_flag):
        """
        Asyncio task to monitor the active state and clean up all RGB LEDs when deactivated.
        """
        while True:
            if not active_flag():
                await self.clean()
            await asyncio.sleep(0.1)

    async def clean(self):
        """
        Cleans up all RGB LEDs by turning them off.
        """
        if init.RGB_LED_ASYNCIO_POLLING:
            init.rgb_led_color.clear()
            for output in range(len(init.rgb_led)):
                try:
                    if self.states.get(output, (0, 0, 0)) != (0, 0, 0):
                        init.rgb_led[output].setColor(0, 0, 0)
                        self.states[output] = (0, 0, 0)
                except Exception as e:
                    print(f"Error turning off RGB LED {output}: {e}")

    def start(self, active_flag):
        """
        Start the RGB LED update and monitoring tasks for all LEDs.
        """
        if init.RGB_LED_ASYNCIO_POLLING:
            self.stop()
            self.rgb_tasks.append(asyncio.create_task(self.update()))
            self.rgb_tasks.append(asyncio.create_task(self.monitor(active_flag)))

    def stop(self):
        """
        Stop all RGB LED tasks.
        """
        for task in self.rgb_tasks:
            task.cancel()
        self.rgb_tasks.clear()
        self.states.clear()
        for output in range(len(init.rgb_led)):
            try:
                init.rgb_led[output].setColor(0, 0, 0)
            except Exception as e:
                print(f"Error turning off RGB LED {output}: {e}")