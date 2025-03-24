"""
MicroPython Tesla Coil Controller (MPTCC)
by Cameron Prince
teslauniverse.com

hardware/input/switch_mcp23017.py
A switch driver for using generic switches connected to a MCP23017 GPIO expander.
"""

import time
import uasyncio as asyncio
from machine import Pin, I2C
from ...hardware.init import init
from ..input.input import Input

# MCP23017 Registers.
IODIRA = 0x00  # I/O Direction Register for PORTA
IODIRB = 0x01  # I/O Direction Register for PORTB
GPPUA = 0x0C  # Pull-Up Resistor Register for PORTA
GPPUB = 0x0D  # Pull-Up Resistor Register for PORTB
GPINTENA = 0x04  # Interrupt-on-Change Enable Register for PORTA
GPINTENB = 0x05  # Interrupt-on-Change Enable Register for PORTB
INTCONA = 0x08  # Interrupt Control Register for PORTA
INTCONB = 0x09  # Interrupt Control Register for PORTB
GPIOA = 0x12  # GPIO Register for PORTA
GPIOB = 0x13  # GPIO Register for PORTB
INTCAPA = 0x10  # Interrupt Capture Register for PORTA
INTCAPB = 0x11  # Interrupt Capture Register for PORTB


class Switch_MCP23017(Input):
    """
    A class to handle switches connected to an MCP23017 GPIO expander.
    """

    def __init__(self, i2c_instance, i2c_addr, port, pins, pull_up, host_interrupt_pin, host_interrupt_pin_pull_up=True):
        """
        Initialize the MCP23017 switch driver.

        Args:
            i2c_instance (int): The I2C instance to use (1 or 2).
            i2c_addr (int): The I2C address of the MCP23017.
            port (str): The port to use ("A" or "B").
            pins (list): A list of pin numbers to use as switches.
            pull_up (bool): Whether to enable internal pull-up resistors.
            host_interrupt_pin (int): The GPIO pin to use for interrupts.
            host_interrupt_pin_pull_up (bool): Whether to enable the pull-up resistor on the host interrupt pin.
        """
        super().__init__()
        self.init = init
        self.i2c_instance = i2c_instance
        self.i2c_addr = i2c_addr
        self.port = port
        self.pins = pins
        self.pull_up = pull_up
        self.host_interrupt_pin = host_interrupt_pin
        self.host_interrupt_pin_pull_up = host_interrupt_pin_pull_up

        # Initialize I2C bus.
        if self.i2c_instance == 2:
            self.init.init_i2c_2()
            self.i2c = self.init.i2c_2
            self.mutex = self.init.i2c_2_mutex
        else:
            self.init.init_i2c_1()
            self.i2c = self.init.i2c_1
            self.mutex = self.init.i2c_1_mutex

        # Configure MCP23017.
        self._setup_mcp23017()

        # Set up the host interrupt pin with optional pull-up resistor.
        pull_up_mode = Pin.PULL_UP if self.host_interrupt_pin_pull_up else Pin.PULL_NONE
        self.interrupt_pin = Pin(self.host_interrupt_pin, Pin.IN, pull_up_mode)
        self.interrupt_pin.irq(trigger=Pin.IRQ_FALLING, handler=self._interrupt_handler)

        # Track switch states and last click times.
        self.switch_states = [1] * len(self.pins)  # 1 = released, 0 = pressed.
        self.last_switch_click_time = [0] * len(self.pins)
        self.active_interrupt = False
        self.debounce_delay = 50  # Debounce delay in milliseconds.
        self.last_interrupt_time = time.ticks_ms()  # Initialize last interrupt time.

        # Debugging: Print initialization details.
        print(f"MCP23017 switch driver initialized on I2C instance {self.i2c_instance} at address 0x{self.i2c_addr:02X}")
        print(f"- Port: {self.port}, Switch pin pull up: {self.pull_up}")
        for i, pin in enumerate(self.pins):
            print(f"  - Switch {i + 1}: Pin {pin}")
        print(f"- Interrupt pin: {self.host_interrupt_pin}, Pull up: {self.host_interrupt_pin_pull_up}")

        # Start the interrupt processing task.
        asyncio.create_task(self._process_interrupt())

    def _setup_mcp23017(self):
        """
        Configure the MCP23017 for interrupts.
        """
        # Set pins as inputs.
        pin_mask = self._create_pin_mask(self.pins)
        if self.port == "A":
            self._write_register(IODIRA, pin_mask)
        else:
            self._write_register(IODIRB, pin_mask)

        # Enable pull-up resistors if required.
        if self.pull_up:
            if self.port == "A":
                self._write_register(GPPUA, pin_mask)
            else:
                self._write_register(GPPUB, pin_mask)

        # Enable interrupt-on-change for the specified pins.
        if self.port == "A":
            self._write_register(GPINTENA, pin_mask)
            self._write_register(INTCONA, 0x00)  # Interrupt on any change.
        else:
            self._write_register(GPINTENB, pin_mask)
            self._write_register(INTCONB, 0x00)  # Interrupt on any change.

        # Clear any pending interrupts by reading INTCAP.
        if self.port == "A":
            intcap = self._read_register(INTCAPA)
        else:
            intcap = self._read_register(INTCAPB)

    def _create_pin_mask(self, pins):
        """
        Create a pin mask for the given list of pins.

        Args:
            pins (list): List of pin numbers.

        Returns:
            int: Pin mask.
        """
        mask = 0
        for pin in pins:
            mask |= 1 << pin
        return mask

    def _write_register(self, reg, value):
        """
        Write a value to a MCP23017 register.

        Args:
            reg (int): The register address.
            value (int): The value to write.
        """
        self.init.mutex_acquire(self.mutex, "Switch_MCP23017:_write_register")
        try:
            self.i2c.writeto_mem(self.i2c_addr, reg, bytearray([value]))
        except Exception as e:
            print(f"Error writing to register 0x{reg:02X}: {e}")
        finally:
            self.init.mutex_release(self.mutex, "Switch_MCP23017:_write_register")

    def _read_register(self, reg):
        """
        Read a value from a MCP23017 register.

        Args:
            reg (int): The register address.

        Returns:
            int: The value read from the register.
        """
        self.init.mutex_acquire(self.mutex, "Switch_MCP23017:_read_register")
        try:
            value = self.i2c.readfrom_mem(self.i2c_addr, reg, 1)[0]
            return value
        except Exception as e:
            print(f"Error reading from register 0x{reg:02X}: {e}")
            return 0
        finally:
            self.init.mutex_release(self.mutex, "Switch_MCP23017:_read_register")

    def _interrupt_handler(self, pin):
        """
        Minimal interrupt handler. Sets the active_interrupt flag after debouncing.
        """
        current_time = time.ticks_ms()
        if time.ticks_diff(current_time, self.last_interrupt_time) > self.debounce_delay:
            self.last_interrupt_time = current_time
            self.active_interrupt = True

    async def _process_interrupt(self):
        """
        Asyncio task to process switch interrupts.
        """
        while True:
            if self.active_interrupt:
                self.active_interrupt = False

                # Read the interrupt capture register to determine which switch was pressed.
                intcap = self._read_register(INTCAPA if self.port == "A" else INTCAPB)

                # If INTCAP is 00000000, skip processing.
                if intcap == 0:
                    continue

                # Check each switch.
                for i, pin in enumerate(self.pins):
                    current_state = (intcap >> pin) & 1  # Read the state of the switch (0 = pressed, 1 = released).
                    if current_state != self.switch_states[i]:  # State changed.
                        self.switch_states[i] = current_state
                        if current_state == 0:  # Switch pressed.
                            self.switch_click(i + 1)  # Switch indices are 1-based.

                # Clear the interrupt condition by reading GPIO.
                self._read_register(GPIOA if self.port == "A" else GPIOB)

            await asyncio.sleep(0.01)  # Small delay to prevent busy-waiting.

    def switch_click(self, switch):
        """
        Handle a switch click event.

        Args:
            switch (int): The switch number (1-based index).
        """
        current_time = time.ticks_ms()
        if time.ticks_diff(current_time, self.last_switch_click_time[switch - 1]) > self.debounce_delay:
            self.last_switch_click_time[switch - 1] = current_time

            if switch <= 4:
                # Switches 1-4: Call the parent class's switch_click method.
                super().switch_click(switch)
            else:
                # Switches 5-6: Simulate encoder 1 rotation.
                direction = 1 if switch == 6 else -1  # Switch 5 = Previous, Switch 6 = Next.
                super().encoder_change(0, direction)  # Encoder 1 is index 0.
