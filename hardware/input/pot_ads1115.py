"""
MicroPython Tesla Coil Controller (MPTCC)
by Cameron Prince
teslauniverse.com

hardware/input/pot_ads1115.py
A pot driver for using generic potentiometers connected to a ADS1115
16-bit precision ADC with 4 single-ended inputs. As with encoders, one
pot is expected for each coil to be driven.
"""

import time
import uasyncio as asyncio
from machine import I2C, Pin
from ...hardware.init import init
from ..input.input import Input
from ...lib.menu import Screen

class Logger:
    DEBUG = 10
    INFO = 20
    WARNING = 30
    ERROR = 40
    CRITICAL = 50

    def __init__(self, level=INFO):
        self.level = level

    def log(self, level, message):
        if level >= self.level:
            print(message)

    def debug(self, message):
        self.log(Logger.DEBUG, message)

    def info(self, message):
        self.log(Logger.INFO, message)

    def warning(self, message):
        self.log(Logger.WARNING, message)

    def error(self, message):
        self.log(Logger.ERROR, message)

logger = Logger(level=Logger.INFO)

class Pot_ADS1115(Input):
    # ADS1115 Register Definitions
    CONVERSION = 0x00  # Conversion register
    CONFIG = 0x01      # Config register
    ADC_MAX_VALUE = 65535  # Maximum value for a 16-bit ADC

    # Configuration settings
    OS = 0x8000  # Operational status/single-shot conversion start
    MUX_A0 = 0x4000  # Input multiplexer configuration (A0 vs GND)
    MUX_A1 = 0x5000  # Input multiplexer configuration (A1 vs GND)
    MUX_A2 = 0x6000  # Input multiplexer configuration (A2 vs GND)
    MUX_A3 = 0x7000  # Input multiplexer configuration (A3 vs GND)
    PGA = 0x0100  # Programmable gain amplifier (±2.048V)
    MODE = 0x0100  # Device operating mode (single-shot)
    DR = 0x0080  # Data rate (128 SPS)
    COMP_MODE = 0x0000  # Comparator mode (traditional)
    COMP_POL = 0x0000  # Comparator polarity (active low)
    COMP_LAT = 0x0000  # Latching comparator (non-latching)
    COMP_QUE = 0x0003  # Comparator queue (disable comparator)

    def __init__(self):
        super().__init__()

        self.init = init
        self.pots = []  # List to store potentiometer objects
        self.polling_active = False  # Flag to control polling
        self.polling_task = None  # Store the polling task
        self.debounce_threshold = 50  # Increased debounce threshold

        # Initialize I2C bus and mutex
        if self.init.POT_ADS1115_I2C_INSTANCE == 2:
            self.init.init_i2c_2()
            self.i2c = self.init.i2c_2
            self.mutex = self.init.i2c_2_mutex
        else:
            self.init.init_i2c_1()
            self.i2c = self.init.i2c_1
            self.mutex = self.init.i2c_1_mutex

        # Verify ADS1115 connection
        if not self._verify_ads1115():
            raise RuntimeError("ADS1115 not detected on I2C bus. Check wiring and address.")

        # Initialize potentiometers
        for i in range(self.init.NUMBER_OF_COILS):
            pin_attr = f"POT_ADS1115_PIN_POT_{i + 1}"
            if not hasattr(self.init, pin_attr):
                raise ValueError(f"Potentiometer configuration for input {i + 1} is missing. Please ensure {pin_attr} is defined in main.")
            pin = getattr(self.init, pin_attr)
            self.pots.append({
                "pin": pin,
                "last_value": 0,
                "channel": i  # ADS1115 channel (0-3)
            })

        # Print initialization details
        self._print_initialization_details()

    def start_polling(self):
        """
        Start the pot polling task.
        """
        if not self.polling_active:
            self.polling_active = True
            self.polling_task = asyncio.create_task(self.poll_pots())
            logger.info("Pot polling task started")

    def stop_polling(self):
        """
        Stop the pot polling task.
        """
        if self.polling_active:
            self.polling_active = False
            if self.polling_task:
                self.polling_task.cancel()
                self.polling_task = None
            logger.info("Pot polling stopped")

    def _verify_ads1115(self):
        """
        Verify that the ADS1115 is connected and responding on the I2C bus.
        """
        self.init.mutex_acquire(self.mutex, "pot_ads1115:_verify_ads1115")
        try:
            devices = self.i2c.scan()
            if self.init.POT_ADS1115_I2C_ADDR not in devices:
                logger.error(f"ADS1115 not found at address 0x{self.init.POT_ADS1115_I2C_ADDR:02X}. Detected devices: {[hex(addr) for addr in devices]}")
                return False
            return True
        except Exception as e:
            logger.error(f"Error verifying ADS1115: {e}")
            return False
        finally:
            self.init.mutex_release(self.mutex, "pot_ads1115:_verify_ads1115")

    def _configure_ads1115(self, channel):
        """
        Configure the ADS1115 for a specific channel.
        """
        try:
            # Select the appropriate MUX setting based on the channel
            if channel == 0:
                mux = self.MUX_A0
            elif channel == 1:
                mux = self.MUX_A1
            elif channel == 2:
                mux = self.MUX_A2
            elif channel == 3:
                mux = self.MUX_A3
            else:
                raise ValueError("Invalid channel. Must be 0, 1, 2, or 3.")

            # Construct the configuration value for the selected channel
            config = self.OS | mux | self.PGA | self.MODE | self.DR | self.COMP_MODE | self.COMP_POL | self.COMP_LAT | self.COMP_QUE
            logger.debug(f"Configuring ADS1115 for channel {channel} with config value: 0x{config:04X}")
            self._write_register(self.CONFIG, config)
        except Exception as e:
            logger.error(f"Error configuring ADS1115: {e}")

    def _read_register(self, reg):
        """
        Read a register from the ADS1115.
        """
        self.init.mutex_acquire(self.mutex, "pot_ads1115:_read_register")
        try:
            data = self.i2c.readfrom_mem(self.init.POT_ADS1115_I2C_ADDR, reg, 2)
            return (data[0] << 8) | data[1]
        except OSError as e:
            logger.error(f"Error reading from ADS1115: {e}")
            return 0
        finally:
            self.init.mutex_release(self.mutex, "pot_ads1115:_read_register")

    def _write_register(self, reg, value):
        """
        Write a value to a register on the ADS1115.
        """
        self.init.mutex_acquire(self.mutex, "pot_ads1115:_write_register")
        try:
            self.i2c.writeto_mem(self.init.POT_ADS1115_I2C_ADDR, reg, bytearray([(value >> 8) & 0xFF, value & 0xFF]))
        except OSError as e:
            logger.error(f"Error writing to ADS1115: {e}")
        finally:
            self.init.mutex_release(self.mutex, "pot_ads1115:_write_register")

    def _print_initialization_details(self):
        """
        Print initialization details for the ADS1115 potentiometer driver.
        """
        logger.info(f"ADS1115 potentiometer driver initialized on I2C_{self.init.POT_ADS1115_I2C_INSTANCE} at address: 0x{self.init.POT_ADS1115_I2C_ADDR:02X}")
        for i, pot in enumerate(self.pots):
            logger.info(f"- Pot {i + 1}: Pin={pot['pin']}, Channel={pot['channel']}")

    async def _read_pot_value(self, channel):
        """
        Read the analog value from a specific channel.
        """
        try:
            # Configure the ADS1115 for the specified channel
            self._configure_ads1115(channel)
            await asyncio.sleep(0.01)  # Wait for conversion to complete
            value = self._read_register(self.CONVERSION)
            logger.debug(f"Read value from channel {channel}: {value}")  # Debugging output
            return value
        except Exception as e:
            logger.error(f"Error reading pot value: {e}")
            return 0

    async def poll_pots(self):
        """
        Poll the potentiometers and handle changes.
        """
        logger.info("Starting pot polling task")
        while self.polling_active:  # Only poll while polling_active is True
            logger.debug("Polling pots...")
            for i, pot in enumerate(self.pots):
                value = await self._read_pot_value(pot["channel"])  # Await the coroutine
                logger.debug(f"Pot {i + 1} (Channel {pot['channel']}): Value = {value}")  # Debugging output
                if abs(value - pot["last_value"]) > self.debounce_threshold:  # State changed with debounce
                    change = value - pot["last_value"]
                    logger.info(f"Pot {i + 1} value changed: {value} (Previous: {pot['last_value']})")  # Debugging output
                    pot["last_value"] = value
                    self._handle_pot_change(i, change)
            await asyncio.sleep(0.1)  # Polling interval

    def _handle_pot_change(self, idx, change):
        """
        Handle a change in potentiometer value.
        """
        logger.info(f"Handling pot {idx + 1} change: Change = {change}")  # Debugging output
        # Map the ADC change to a direction and call encoder_change
        direction = 1 if change > 0 else -1
        logger.debug(f"Direction: {direction}")  # Debugging output
        # Call encoder_change based on the change value
        super().encoder_change(idx, direction * abs(change))

    def initialize_pots(self):
        """
        Initialize potentiometer values and adjust levels accordingly.
        """
        for i, pot in enumerate(self.pots):
            value = self._read_register(self.CONVERSION)
            logger.info(f"Initializing pot {i + 1} with value: {value}")  # Debugging output
            pot["last_value"] = value
            # Call encoder_change to match the initial pot position
            super().encoder_change(i, value)

    def get_pot_percentage(self, idx):
        """
        Calculate the percentage value of the potentiometer.
        """
        pot_value = self.pots[idx]["last_value"]
        percentage = (pot_value / self.ADC_MAX_VALUE) * 100
        return percentage
