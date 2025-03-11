"""
MicroPython Tesla Coil Controller (MPTCC)
by Cameron Prince
teslauniverse.com

hardware/input/switch_mcp23017.py
A switch driver for using generic switches connected to a MCP23017
GPIO expander. When using a switch driver with this project, six
switches must be provided. These are used as follows:

1: Corresponds with the switch_1 function, normally called by
the first encoder's switch action.
2. Corresponds with the switch_2 function, normally called by
the second encoder's switch action.
3. Corresponds with the switch_3 function, normally called by
the third encoder's switch action.
4. Corresponds with the switch_4 function, normally called by
the fourth encoder's switch action.
5. Acts as the button for up, or previous, in place of the first
encoder's CCW rotation.
6. Acts as the button for down, or next, in place of the first
encoder's CW rotation.
"""

import time
import uasyncio as asyncio
from machine import Pin
from ...hardware.init import init
from ..input.input import Input
from ...lib.menu import Screen
from ...lib.mcp23017 import MCP23017

class Switch_MCP23017(Input):
    # Configuration constants
    SWITCH_PINS_MASK = 0b00111111  # Mask for pins 0-5
    INTERRUPT_ENABLE = 0b00111111  # Enable interrupts on pins 0-5
    DEFAULT_VALUE = 0b00111111  # Default value for interrupt (active-low)
    INTERRUPT_ON_CHANGE = 0b00111111  # Interrupt on change from default value

    def __init__(self):
        super().__init__()

        print("Switch_MCP23017 init")

        # Initialize I2C bus
        if self.init.SWITCH_MCP23017_I2C_INSTANCE == 2:
            self.init.init_i2c_2()
            i2c = self.init.i2c_2
            mutex = self.init.i2c_2_mutex
        else:
            self.init.init_i2c_1()
            i2c = self.init.i2c_1
            mutex = self.init.i2c_1_mutex

        # Initialize MCP23017
        self.mcp = MCP23017(i2c, self.init.SWITCH_MCP23017_I2C_ADDR, mutex)

        # Scan the I2C bus to verify the MCP23017 is detected
        print("Scanning I2C bus...")
        devices = i2c.scan()
        print("I2C devices found:", [hex(device) for device in devices])
        if self.init.SWITCH_MCP23017_I2C_ADDR not in devices:
            raise ValueError(f"MCP23017 not found at address {hex(self.init.SWITCH_MCP23017_I2C_ADDR)}")

        # Continue with the rest of the initialization
        self.last_switch_click_time = [0] * 6  # Track last click time for debouncing
        self.switch_states = [1] * 6  # Track the state of each switch (1 = released, 0 = pressed)
        self.active_interrupt = False  # Flag to indicate an interrupt has occurred
        self.last_interrupt_time = 0  # Track the last interrupt time for debouncing
        self.debounce_delay = 50  # Debounce delay in milliseconds

        # Disable integrated switches in encoders
        self.init.integrated_switches = False

        # Configure MCP23017 pins as inputs with pull-up resistors and enable interrupts
        self._configure_mcp23017()

        # Add a delay to allow the MCP23017 to stabilize
        time.sleep(0.1)

        # Set up the interrupt pin (with pull-up)
        self.interrupt_pin = Pin(self.init.SWITCH_MCP23017_INTERRUPT_PIN, Pin.IN, Pin.PULL_UP)
        self.interrupt_pin.irq(trigger=Pin.IRQ_FALLING, handler=self._interrupt_handler)

        # Print initialization details
        self._print_initialization_details()

        # Start the interrupt processing task
        asyncio.create_task(self._process_interrupt())

    def _configure_mcp23017(self):
        """
        Configure the MCP23017 GPIO expander for switch inputs and interrupts.
        """
        print("Configuring MCP23017...")

        # Set all switch pins (0-5) as inputs with pull-ups and enable interrupts
        self.mcp.configure_pins('A', direction=0b00111111, pull_up=0b00111111, interrupt=0b00111111)

        # Clear any pending interrupts by reading INTCAPA
        self.mcp._read_register(self.mcp.INTCAPA)
        print(f"INTCAPA after read: {self.mcp._read_register(self.mcp.INTCAPA):08b}")

    def _print_initialization_details(self):
        """
        Print initialization details for the MCP23017 switch driver.
        """
        print(f"MCP23017 switch driver initialized on I2C_{self.init.SWITCH_MCP23017_I2C_INSTANCE} at address: 0x{self.init.SWITCH_MCP23017_I2C_ADDR:02X}")
        print(f"Interrupt pin: {self.init.SWITCH_MCP23017_INTERRUPT_PIN}")
        for i in range(6):
            pin_attr = f"SWITCH_MCP23017_PIN_SWITCH_{i + 1}"
            pin = getattr(self.init, pin_attr, None)
            if pin is not None:
                print(f"- Switch {i + 1}: Pin={pin}")
            else:
                print(f"- Switch {i + 1}: Pin not configured")

    def _interrupt_handler(self, pin):
        """
        Minimal interrupt handler. Sets the active_interrupt flag after debouncing.
        """
        current_time = time.ticks_ms()
        if time.ticks_diff(current_time, self.last_interrupt_time) > self.debounce_delay:
            self.last_interrupt_time = current_time
            print("Interrupt detected!")  # Debugging output
            self.active_interrupt = True

    async def _process_interrupt(self):
        """
        Asyncio task to process switch interrupts.
        """
        print("Starting interrupt processing task...")
        while True:
            if self.active_interrupt:
                print("Processing interrupt...")
                self.active_interrupt = False

                # Read the interrupt capture register to determine which switch was pressed
                intcap = self.mcp._read_register(self.mcp.INTCAPA)
                print(f"INTCAPA: {intcap:08b}")

                # If INTCAPA is 00000000, skip processing
                if intcap == 0:
                    print("No interrupt captured. Skipping...")
                    continue

                # Check each switch (PA0-PA5)
                for i in range(6):
                    current_state = (intcap >> i) & 1  # Read the state of the switch (0 = pressed, 1 = released)
                    if current_state != self.switch_states[i]:  # State changed
                        self.switch_states[i] = current_state
                        if current_state == 0:  # Switch pressed
                            print(f"Switch {i + 1} pressed")
                            self.switch_click(i + 1)  # Switch indices are 1-based
                        else:  # Switch released
                            print(f"Switch {i + 1} released")

                # Clear the interrupt condition by reading GPIOA
                self.mcp._read_register(self.mcp.GPIOA)
                print(f"GPIOA after read: {self.mcp._read_register(self.mcp.GPIOA):08b}")

            await asyncio.sleep(0.01)  # Small delay to prevent busy-waiting

    def switch_click(self, switch):
        """
        Handle a switch click event.
        """
        current_time = time.ticks_ms()
        if time.ticks_diff(current_time, self.last_switch_click_time[switch - 1]) > self.debounce_delay:
            self.last_switch_click_time[switch - 1] = current_time

            if switch <= 4:
                # Switches 1-4: Call the parent class's switch_click method
                super().switch_click(switch)
            else:
                # Switches 5-6: Simulate encoder 1 rotation
                direction = 1 if switch == 6 else -1  # Switch 5 = Previous, Switch 6 = Next
                super().encoder_change(0, direction)  # Encoder 1 is index 0
