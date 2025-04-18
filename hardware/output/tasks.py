"""
MicroPython Tesla Coil Controller (MPTCC)
by Cameron Prince
teslauniverse.com

hardware/output/tasks.py
Output-related asyncio tasks.
"""

from ...hardware.init import init

def start_output_tasks(active_flag):
    """
    Starts all output-related tasks.

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
