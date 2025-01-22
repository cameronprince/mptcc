"""
MicroPython Tesla Coil Controller (MPTCC)
by Cameron Prince
teslauniverse.com

screens/battery_status.py
Provides the battery status screen.
"""

from machine import ADC
from mptcc.hardware.init import init
from mptcc.lib.menu import CustomItem
import mptcc.lib.utils as utils

class BatteryStatus(CustomItem):
    """
    A class to represent and handle the battery status screen for the 
    MicroPython Tesla Coil Controller (MPTCC).

    Attributes:
    -----------
    name : str
        The name of the battery status screen.
    """

    def __init__(self, name):
        """
        Constructs all the necessary attributes for the BatteryStatus object.

        Parameters:
        ----------
        name : str
            The name of the battery status screen.
        """
        super().__init__(name)
        self.init = init
        self.display = self.init.display

    def draw(self):
        """
        Displays the current battery voltage on the screen.
        """
        self.display.clear()
        self.display.header('Battery Status')
        
        # Read the battery voltage.
        value = ADC(self.init.PIN_BATT_STATUS_ADC).read_u16()
        voltage = value * (3.3 / 65535) * self.init.VOLTAGE_DROP_FACTOR

        # Display the voltage.
        self.display.text(f"{voltage:.2f} VDC", 0, 20, 1)
        self.display.show()

    def switch_2(self):
        """
        Respond to encoder 2 presses to return to the main menu.
        """
        parent_screen = self.parent
        if parent_screen:
            self.init.menu.set_screen(parent_screen)
            self.init.menu.draw()
