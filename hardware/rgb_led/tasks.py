"""
MicroPython Tesla Coil Controller (MPTCC)
by Cameron Prince
teslauniverse.com

When init.RGB_LED_ASYNCIO_POLLING = True, the start task is called from
screens which activate outputs. The output drivers also check for this
constant which causes them to update self.init.rgb_led_color rather than
attempting to communicate with the hardware drivers directly. The task
below detects the changes to rgb_led_color and makes the driver calls.
This ensures that only the main thread is communicating with the hardware.

hardware/rgb_led/tasks.py
Asyncio tasks for RGB LED control.
"""

import uasyncio as asyncio
from ...hardware.init import init
from ...hardware.manager import RGBLEDManager

# Global state for tracking LED colors.
rgb_led_states = {}

# Track the tasks we create.
rgb_led_tasks = []

# Create an instance of RGBLEDManager
rgb_led_manager = RGBLEDManager(init)

# Create storage for the colors.
init.rgb_led_color = {}

async def update_rgb_leds():
    """
    Continuously update the RGB LEDs based on the color changes in rgb_led_color.
    """
    while True:
        for output, color in init.rgb_led_color.items():
            if color:
                r, g, b = color
                if rgb_led_states.get(output, (0, 0, 0)) != (r, g, b):
                    rgb_led_states[output] = (r, g, b)
                    rgb_led_manager.set_color(output, r, g, b)
                init.rgb_led_color[output] = None
        await asyncio.sleep(0.1)

async def monitor_rgb_leds(active_flag):
    """
    Monitor the active flag and clean up the LEDs when the flag is inactive.

    Parameters:
    ----------
    active_flag : function
        A function that returns a boolean indicating whether the LEDs should be active.
    """
    cleaned = False
    while True:
        if not active_flag() and not cleaned:
            await clean_rgb_leds()
            cleaned = True
        elif active_flag() and cleaned:
            cleaned = False
        await asyncio.sleep(0.1)

async def clean_rgb_leds():
    """
    Clean up the RGB LEDs by turning them off and clearing the color state.
    """
    init.rgb_led_color.clear()
    await turn_off_all_rgb_leds()

async def turn_off_all_rgb_leds():
    """
    Turn off all RGB LEDs.
    """
    # print("turn_off_all_rgb_leds")
    rgb_led_manager.disable_all_leds()
    for index in rgb_led_states:
        rgb_led_states[index] = (0, 0, 0)

def start_rgb_led_task(active_flag):
    """
    Start the RGB LED tasks (update and monitor).

    Parameters:
    ----------
    active_flag : function
        A function that returns a boolean indicating whether the LEDs should be active.
    """
    stop_rgb_led_task()
    # Create and track the tasks.
    rgb_led_tasks.append(asyncio.create_task(update_rgb_leds()))
    rgb_led_tasks.append(asyncio.create_task(monitor_rgb_leds(active_flag)))

def stop_rgb_led_task():
    """
    Stop all RGB LED tasks and turn off all LEDs.
    """
    # Cancel all tracked tasks.
    for task in rgb_led_tasks:
        task.cancel()
    # Clear the task list.
    rgb_led_tasks.clear()
    # Clear the state.
    rgb_led_states.clear()
    # Turn off all LEDs.
    asyncio.create_task(turn_off_all_rgb_leds())
