"""
MicroPython Tesla Coil Controller (MPTCC)
by Cameron Prince
teslauniverse.com

hardware/output/mcp23017.py
Class for driving outputs with the MCP23017 GPIO expander using direct register access.
"""

from machine import I2C, Pin
from ...lib import utils
from ...hardware.init import init
from ..output.output import Output
import uasyncio as asyncio
import time
import _thread

class MCP23017(Output):
    
    MCP23017_ADDR = 0x27  # Default I2C address for MCP23017.
    
    # MCP23017 register addresses.
    IODIRA = 0x00  # I/O Direction Register for Port A.
    GPIOA = 0x12   # GPIO Port A Register.
    OLATA = 0x14   # Output Latch Register for Port A.
    
    # Pins to control (PA0-PA3).
    MCP23017_OUTPUT_1_PIN = 0  # Pin 0 on Port A.
    MCP23017_OUTPUT_2_PIN = 1  # Pin 1 on Port A.
    MCP23017_OUTPUT_3_PIN = 2  # Pin 2 on Port A.
    MCP23017_OUTPUT_4_PIN = 3  # Pin 3 on Port A.
    
    def __init__(self):
        """
        Initializes the MCP23017 output driver.
        """
        super().__init__()
        self.init = init

        # Prepare the I2C bus.
        self.init.init_i2c_1()
        self.i2c = self.init.i2c_1

        # Reset the MCP23017 to its default state.
        self._reset_mcp23017()
        print("MCP23017 reset to default state.")

        # Add a mutex for I2C communication to the init object.
        if not hasattr(self.init, 'i2c_mutex'):
            self.init.i2c_mutex = _thread.allocate_lock()

        # Instantiate each Output_MCP23017.
        self.output = [
            Output_MCP23017(self.i2c, self.MCP23017_ADDR, self.MCP23017_OUTPUT_1_PIN, self.init.i2c_mutex),
            Output_MCP23017(self.i2c, self.MCP23017_ADDR, self.MCP23017_OUTPUT_2_PIN, self.init.i2c_mutex),
            Output_MCP23017(self.i2c, self.MCP23017_ADDR, self.MCP23017_OUTPUT_3_PIN, self.init.i2c_mutex),
            Output_MCP23017(self.i2c, self.MCP23017_ADDR, self.MCP23017_OUTPUT_4_PIN, self.init.i2c_mutex),
        ]

    def _reset_mcp23017(self):
        """
        Resets the MCP23017 to its default state.
        """
        # Reset IODIRA and IODIRB to default (0xFF, all pins as inputs).
        self._write_register(self.IODIRA, 0xFF)
        self._write_register(0x01, 0xFF)  # IODIRB register.

        # Reset GPIOA and GPIOB to default (0x00, all pins low).
        self._write_register(self.GPIOA, 0x00)
        self._write_register(0x13, 0x00)  # GPIOB register.

    def _write_register(self, reg, value):
        """
        Writes a value to a register on the MCP23017.
        """
        print(f"Writing value {hex(value)} to register {hex(reg)}...")
        self.init.i2c_mutex.acquire()
        try:
            self.i2c.writeto_mem(self.MCP23017_ADDR, reg, bytes([value]))
        finally:
            self.init.i2c_mutex.release()

    def set_output(self, output, active, frequency=None, on_time=None, max_duty=None, max_on_time=None):
        """
        Sets the output based on the provided parameters.

        Parameters:
        ----------
        output : int
            The index of the output to be set.
        active : bool
            Whether the output should be active.
        frequency : int, optional
            The frequency of the output signal in Hz.
        on_time : int, optional
            The on time of the output signal in microseconds.
        max_duty : int, optional
            The maximum duty cycle allowed.
        max_on_time : int, optional
            The maximum on time allowed in microseconds.

        Raises:
        -------
        ValueError
            If frequency or on_time is not provided when activating the output.
        """
        if active:
            if frequency is None or on_time is None:
                raise ValueError("Frequency and on_time must be provided when activating the output.")

            frequency = int(frequency)
            on_time = int(on_time)

            # Enable the output.
            self.output[output].enable(frequency, on_time)

            # Handle LED updates.
            self.init.rgb_led[output].status_color(frequency, on_time, max_duty, max_on_time)
        else:
            # Disable the output.
            self.output[output].off()
            self.init.rgb_led[output].off()


class Output_MCP23017:
    def __init__(self, i2c, address, pin, i2c_mutex):
        self.i2c = i2c
        self.address = address
        self.pin = pin
        self.i2c_mutex = i2c_mutex
        self.running = False
        self.task = None
        self.task_mutex = _thread.allocate_lock()  # Mutex for task operations
        self.gpio_state = 0x00  # Cache the GPIOA register state.

        # Configure the pin as an output.
        self._write_register(0x00, 0xF0)  # Set PA0-PA3 as outputs (0 = output, 1 = input).
        self._write_register(0x12, 0x00)  # Set PA0-PA3 low initially.

    def _write_register(self, reg, value):
        """
        Writes a value to a register on the MCP23017.
        """
        self.i2c_mutex.acquire()
        try:
            self.i2c.writeto_mem(self.address, reg, bytes([value]))
        except OSError as e:
            print(f"I2C write error: {e}")
            self._reset_i2c()  # Reset the I2C bus on error.
        finally:
            self.i2c_mutex.release()

    def _read_register(self, reg):
        """
        Reads a value from a register on the MCP23017.
        """
        self.i2c_mutex.acquire()
        try:
            return self.i2c.readfrom_mem(self.address, reg, 1)[0]
        except OSError as e:
            print(f"I2C read error: {e}")
            self._reset_i2c()  # Reset the I2C bus on error.
            return 0  # Return a default value.
        finally:
            self.i2c_mutex.release()

    def _reset_i2c(self):
        """
        Resets the I2C bus to recover from errors.
        """
        print("Resetting I2C bus...")
        self.i2c.init()  # Reinitialize the I2C bus.

    def _set_pin_value(self, value):
        """
        Sets the value of the pin (high or low) and updates the cached GPIO state.
        """
        if value:
            self.gpio_state |= (1 << self.pin)  # Set pin high.
        else:
            self.gpio_state &= ~(1 << self.pin)  # Set pin low.
        self._write_register(0x12, self.gpio_state)  # Write GPIOA register.

    async def _sleep_us(self, us):
        """
        Custom sleep function for microseconds.
        """
        start = time.ticks_us()
        while time.ticks_diff(time.ticks_us(), start) < us:
            await asyncio.sleep_ms(0)  # Yield control to the event loop.

    async def _bitbang_pwm(self, frequency, on_time):
        """
        Generates a PWM signal using bit banging.
        """
        period = 1_000_000 // frequency  # Period in microseconds.
        off_time = period - on_time      # Off time in microseconds.

        while self.running:
            try:
                self._set_pin_value(1)  # Set pin high.
                await self._sleep_us(on_time)  # Use custom sleep_us function.
                self._set_pin_value(0)  # Set pin low.
                await self._sleep_us(off_time)
            except OSError as e:
                print(f"I2C error in _bitbang_pwm: {e}")
                break  # Exit the loop on I2C errors.

    def enable(self, frequency, on_time):
        """
        Enables the output with the specified frequency and on time.
        """
        with self.task_mutex:
            if self.task is not None:
                # Schedule the task cancellation in the asyncio event loop.
                init.task_queue.put(self._cancel_task())
                self.task = None

            self.running = True
            # Schedule the PWM task in the asyncio event loop.
            init.task_queue.put(self._start_pwm(frequency, on_time))

    async def _start_pwm(self, frequency, on_time):
        """
        Coroutine to start the PWM task.
        """
        self.task = asyncio.create_task(self._bitbang_pwm(frequency, on_time))

    async def _cancel_task(self):
        """
        Coroutine to cancel the current task.
        """
        if self.task is not None:
            self.task.cancel()
            try:
                await self.task
            except asyncio.CancelledError:
                pass
            self.task = None

    def off(self):
        """
        Disables the output by stopping the timer and setting the pin low.
        """
        with self.task_mutex:
            self.running = False
            if self.task is not None:
                # Schedule the task cancellation in the asyncio event loop.
                init.task_queue.put(self._cancel_task())
                self.task = None
            # Schedule setting the pin low in the asyncio event loop.
            init.task_queue.put(self._set_pin_low())

    async def _set_pin_low(self):
        """
        Coroutine to set the pin low.
        """
        self._set_pin_value(0)
