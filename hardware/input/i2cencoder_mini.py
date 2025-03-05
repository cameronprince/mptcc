"""
MicroPython Tesla Coil Controller (MPTCC)
by Cameron Prince
teslauniverse.com

hardware/input/i2cencoder_mini.py
Input module for I2CEncoderMini V1.2.
"""

import time
import uasyncio as asyncio
from machine import Pin
from ...lib.duppa import DuPPa
from ...hardware.init import init
from ..input.input import Input

# Constants and register definitions
CONSTANTS = {
    # Register definitions
    "REG_GCONF": 0x00,
    "REG_INTCONF": 0x01,
    "REG_ESTATUS": 0x02,
    "REG_CVALB4": 0x03,
    "REG_CMAXB4": 0x07,
    "REG_CMINB4": 0x0B,
    "REG_ISTEPB4": 0x0F,
    "REG_DPPERIOD": 0x13,

    # Configuration values
    "WRAP_ENABLE": 0x01,
    "DIRE_LEFT": 0x02,
    "RMOD_X1": 0x00,
    "RESET": 0x80,

    # Status bits
    "PUSHP": 0x02,
    "RINC": 0x10,
    "RDEC": 0x20,
}

class I2CEncoderMini(Input):
    def __init__(self):
        super().__init__()

        self.init = init
        self.encoders = []
        self.init_complete = False

        # Validate that the number of encoders matches NUMBER_OF_COILS.
        if len(self.init.I2CENCODER_MINI_ADDRESSES) != self.init.NUMBER_OF_COILS:
            raise ValueError(
                f"The number of I2C encoder mini addresses ({len(self.init.I2CENCODER_MINI_ADDRESSES)}) "
                f"must match NUMBER_OF_COILS ({self.init.NUMBER_OF_COILS}). The program will now exit."
            )

        # Prepare the I2C bus.
        if self.init.I2CENCODER_MINI_I2C_INSTANCE == 2:
            self.init.init_i2c_2()
            self.i2c = self.init.i2c_2
            self.mutex = self.init.i2c_2_mutex
        else:
            self.init.init_i2c_1()
            self.i2c = self.init.i2c_1
            self.mutex = self.init.i2c_1_mutex

        # Shared variable for asyncio task.
        self.active_interrupt = False

        # Initialize last_rotations to track previous encoder values.
        self.last_rotations = [0] * self.init.NUMBER_OF_COILS

        # Set up the shared interrupt pin.
        self.interrupt_pin = Pin(self.init.I2CENCODER_MINI_INTERRUPT_PIN, Pin.IN, Pin.PULL_UP)
        self.interrupt_pin.irq(trigger=Pin.IRQ_FALLING, handler=self.interrupt_handler)

        # Initialize encoders.
        for i in range(self.init.NUMBER_OF_COILS):
            addr = self.init.I2CENCODER_MINI_ADDRESSES[i]
            encoder = DuPPa(self.i2c, addr, CONSTANTS)  # Pass all constants
            self.encoders.append(encoder)
            self.init_encoder(encoder)

        # Start the asyncio task to process interrupts.
        asyncio.create_task(self.process_interrupt())

        # Print initialization details.
        print(f"I2CEncoderMini initialized on I2C_{self.init.I2CENCODER_MINI_I2C_INSTANCE} with {self.init.NUMBER_OF_COILS} objects:")
        for i, addr in enumerate(self.init.I2CENCODER_MINI_ADDRESSES):
            print(f"- Encoder {i + 1}: I2C address 0x{addr:02X}")

        # Mark initialization as complete.
        self.init_complete = True

    def init_encoder(self, encoder):
        """
        Initialize a specific encoder.
        """
        self.init.mutex_acquire(self.mutex, "i2cencoder_mini:init_encoder")

        encoder.reset()
        time.sleep(0.1)

        encconfig = (CONSTANTS["WRAP_ENABLE"] | CONSTANTS["DIRE_LEFT"] | CONSTANTS["RMOD_X1"])
        encoder.begin(encconfig)

        reg = (CONSTANTS["PUSHP"] | CONSTANTS["RINC"] | CONSTANTS["RDEC"])
        encoder.writeInterruptConfig(reg)

        encoder.writeCounter(0)
        encoder.writeMax(100)
        encoder.writeMin(0)
        encoder.writeStep(1)
        encoder.writeDoublePushPeriod(10)

        self.init.mutex_release(self.mutex, "i2cencoder_mini:init_encoder")

    def interrupt_handler(self, pin):
        """
        Minimal interrupt handler. Sets the active_interrupt flag.
        """
        if not self.init_complete:
            return

        # Signal that an interrupt has occurred.
        self.active_interrupt = True

    async def process_interrupt(self):
        """
        Asyncio task to process rotary and switch interrupts.
        """
        while True:
            if self.active_interrupt:
                self.active_interrupt = False

                for idx, encoder in enumerate(self.encoders):
                    self.init.mutex_acquire(self.mutex, "i2cencoder_mini:process_interrupt")
                    try:
                        if encoder.updateStatus():
                            status = encoder.readStatusRaw()
                            if status & (CONSTANTS["RINC"] | CONSTANTS["RDEC"]):
                                direction = 1 if status & CONSTANTS["RINC"] else -1
                                super().rotary_encoder_change(idx, direction)
                                break
                            if status & CONSTANTS["PUSHP"]:
                                super().switch_click(idx + 1)
                                break
                    finally:
                        self.init.mutex_release(self.mutex, "i2cencoder_mini:process_interrupt")

            await asyncio.sleep(0.01)
