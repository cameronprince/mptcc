"""
MicroPython Tesla Coil Controller (MPTCC)
by Cameron Prince
teslauniverse.com

screens/restore_defaults.py
Provides the screen for restoring default settings.

This screen utilizes switch instances directly rather than using the
class-based methods. This is due to the requirement of responding to
two inputs at once.
"""

from mptcc.hardware.init import init
from mptcc.lib.menu import CustomItem
import mptcc.lib.config as config
import mptcc.lib.utils as utils
import _thread
import os
import time
from machine import Pin

class RestoreDefaults(CustomItem):
    """
    A class to represent and handle the screen for restoring default settings
    in the MicroPython Tesla Coil Controller (MPTCC).

    Attributes:
    -----------
    name : str
        The name of the restore defaults screen.
    start_time : int
        The start time for detecting switch presses.
    running : bool
        Flag to indicate if switch monitoring is running.
    monitor_thread : _thread
        The thread object for monitoring switch presses.
    """

    def __init__(self, name):
        """
        Constructs all the necessary attributes for the RestoreDefaults object.

        Parameters:
        ----------
        name : str
            The name of the restore defaults screen.
        """
        super().__init__(name)
        self.start_time = 0
        self.running = False
        self.monitor_thread = None
        self.init = init

    def draw(self):
        """
        Displays the initial restore defaults screen with instructions.
        """
        self.init.display.clear()
        self.init.display.header("Restore Defaults")
        self.init.display.message_screen("Press and hold buttons 3 and 4 to restore.")
        self.start_monitoring()

    def start_monitoring(self):
        """
        Starts the monitoring thread to detect the dual switch press.
        """
        if not self.running:
            self.running = True
            self.monitor_thread = _thread.start_new_thread(self.monitor_switches, ())

    def stop_monitoring(self):
        """
        Stops the switch monitoring.
        """
        if self.running:
            self.running = False

    def monitor_switches(self):
        """
        The main monitoring function to detect dual switch presses.
        """
        while self.running:
            # We can't use the normal switch_ methods here because we
            # need to work with two inputs at once.
            if not self.init.switch_3.value() and not self.init.switch_4.value():
                if self.start_time == 0:
                    self.start_time = time.time()
                elif time.time() - self.start_time > 2:
                    self.restore_defaults()
                    break
            else:
                self.start_time = 0
            time.sleep(0.1)

    def restore_defaults(self):
        """
        Performs the default restoration which consists of removing the config file.
        """
        try:
            os.remove(init.CONFIG_PATH)
        except OSError:
            pass
        self.init.display.clear()
        # Display the success message for two seconds and return to the main menu.
        self.init.display.alert_screen("Defaults restored")

        # Return to the main menu.
        self.init.menu.reset()
        self.init.menu.draw()
        self.stop_monitoring()

    def switch_2(self):
        """
        Responds to encoder 2 presses to return to the configuration menu.
        """
        parent_screen = self.parent
        if parent_screen:
            self.init.menu.set_screen(parent_screen)
            self.init.menu.draw()
        self.stop_monitoring()