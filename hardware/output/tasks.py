"""
MicroPython Tesla Coil Controller (MPTCC)
by Cameron Prince
teslauniverse.com

hardware/output/tasks.py
Output-related asyncio tasks.
"""

import uasyncio as asyncio
from ..rgb_led.tasks import start_rgb_led_task, stop_rgb_led_task
from ...hardware.init import init

def start_output_tasks(active_flag):
    """
    Starts all output-related tasks, such as potentiometer polling and RGB LED tasks.

    Parameters:
    ----------
    active_flag : function
        A function that returns a boolean indicating whether the outputs should be active.
    """
    # Start potentiometer polling if a pot driver is initialized.
    """
    if hasattr(init, "pot") and hasattr(init.pot, "start_polling"):
        init.pot.start_polling()
        print("Potentiometer polling started")
    """

    # Start the global RGB LED tasks if RGB LED asynchronous polling is enabled.
    if init.RGB_LED_ASYNCIO_POLLING:
        start_rgb_led_task(active_flag)
        # print("RGB LED tasks started")

def stop_output_tasks():
    """
    Stops all output-related tasks, such as potentiometer polling and RGB LED tasks.
    """
    # Stop potentiometer polling if a pot driver is initialized.
    """
    if hasattr(init, "pot") and hasattr(init.pot, "stop_polling"):
        init.pot.stop_polling()
        print("Potentiometer polling stopped")
    """

    # Stop the global RGB LED tasks if RGB LED asynchronous polling is enabled.
    if init.RGB_LED_ASYNCIO_POLLING:
        stop_rgb_led_task()
        # print("RGB LED tasks stopped")
