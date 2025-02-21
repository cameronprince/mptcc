"""
MicroPython Tesla Coil Controller (MPTCC)
by Cameron Prince
teslauniverse.com

hardware/output/mcp23017_timer.py
Class for driving outputs with the MCP23017 GPIO expander using hardware timers.
"""

import time
from machine import I2C, Pin, Timer
from ...lib import utils
from ...hardware.init import init
from ..output.output import Output
import _thread

class MCP23017_Timer(Output):
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
            Output_MCP23017_Timer(self.i2c, self.MCP23017_ADDR, self.MCP23017_OUTPUT_1_PIN, self.init.i2c_mutex),
            Output_MCP23017_Timer(self.i2c, self.MCP23017_ADDR, self.MCP23017_OUTPUT_2_PIN, self.init.i2c_mutex),
            Output_MCP23017_Timer(self.i2c, self.MCP23017_ADDR, self.MCP23017_OUTPUT_3_PIN, self.init.i2c_mutex),
            Output_MCP23017_Timer(self.i2c, self.MCP23017_ADDR, self.MCP23017_OUTPUT_4_PIN, self.init.i2c_mutex),
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
        """
        if active:
            if frequency is None or on_time is None:
                raise ValueError("Frequency and on_time must be provided when activating the output.")

            frequency = int(frequency)
            on_time = int(on_time)

            # Enable the output.
            self.output[output].enable(frequency, on_time)

            # Handle LED updates.
            if max_duty and max_on_time:
                percent = utils.calculate_percent(frequency, on_time, max_duty, max_on_time)
                self.init.rgb_led[output].status_color(percent)
            else:
                percent = utils.calculate_midi_percent(frequency, on_time)
                self.init.rgb_led[output].status_color(percent)
        else:
            # Disable the output.
            self.output[output].off()
            self.init.rgb_led[output].off()


class Output_MCP23017_Timer:
    """
    A class for handling outputs with the MCP23017 GPIO expander using timers.
    """
    def __init__(self, i2c, address, pin, i2c_mutex):
        """
        Initializes the Output_MCP23017 object.
        """
        self.i2c = i2c
        self.address = address
        self.pin = pin
        self.i2c_mutex = i2c_mutex
        self.timer = Timer()
        self.running = False

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
            self._reset_mcp23017()  # Reset the MCP23017 on error.
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
            self._reset_mcp23017()  # Reset the MCP23017 on error.
            return 0  # Return a default value.
        finally:
            self.i2c_mutex.release()

    def _set_pin_value(self, value):
        """
        Sets the value of the pin (high or low).
        """
        current_state = self._read_register(0x12)  # Read GPIOA register.
        if value:
            new_state = current_state | (1 << self.pin)  # Set pin high.
        else:
            new_state = current_state & ~(1 << self.pin)  # Set pin low.
        self._write_register(0x12, new_state)  # Write GPIOA register.

    def _toggle_pin(self, timer):
        """
        Timer callback to toggle the pin state.
        """
        try:
            current_state = self._read_register(0x12)  # Read GPIOA register.
            new_state = current_state ^ (1 << self.pin)  # Toggle the pin.
            self._write_register(0x12, new_state)  # Write GPIOA register.
        except Exception as e:
            print(f"Error in _toggle_pin: {e}")
            self.timer.deinit()  # Stop the timer on error.

    def _reset_mcp23017(self):
        """
        Resets the MCP23017 to its default state.
        """
        print("Resetting MCP23017...")
        self._write_register(0x00, 0xFF)  # Set all pins as inputs.
        self._write_register(0x01, 0xFF)  # Set all pins as inputs.
        self._write_register(0x12, 0x00)  # Set all pins low.
        self._write_register(0x13, 0x00)  # Set all pins low.

    def enable(self, frequency, on_time):
        """
        Enables the output with the specified frequency and on time.
        """
        if self.running:
            self.timer.deinit()  # Stop the timer if it's already running.

        self.running = True
        period = 1_000_000 // frequency  # Period in microseconds.
        duty_cycle = int((on_time / period) * 1023)  # Scale to 10-bit PWM.

        # Initialize the timer.
        self.timer.init(
            freq=frequency,      # Set the timer frequency.
            mode=Timer.PERIODIC, # Run the timer in periodic mode.
            callback=self._toggle_pin  # Callback to toggle the pin.
        )

    def off(self):
        """
        Disables the output by stopping the timer and setting the pin low.
        """
        self.running = False
        self.timer.deinit()  # Stop the timer.
        time.sleep_ms(10)  # Small delay to ensure the timer is fully stopped.
        self._set_pin_value(0)  # Set the pin low.