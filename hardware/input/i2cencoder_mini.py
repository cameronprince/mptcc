"""
MicroPython Tesla Coil Controller (MPTCC)
by Cameron Prince
teslauniverse.com

hardware/input/i2cencoder_mini.py
Input module for I2CEncoderMini V1.2.
"""

import _thread
import time
import uasyncio as asyncio
import struct
import i2cEncoderMiniLib
from machine import Pin, I2C
from ...hardware.init import init
from ..input.input import Input

class I2CEncoderMini(Input):
    def __init__(self):
        super().__init__()

        self.init = init
        self.encoders = []

        # Flag to track initialization status.
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
            encoder = i2cEncoderMiniLib.i2cEncoderMiniLib(self.i2c, addr)
            self.encoders.append(encoder)
            self.init_encoder(encoder)

        # Mark initialization as complete.
        self.init_complete = True

        # Start the asyncio task to process interrupts.
        asyncio.create_task(self.process_interrupt())

    def init_encoder(self, encoder):
        """
        Initialize a specific encoder.
        """
        self.init.mutex_acquire(self.mutex, "i2cencoder_mini:init_encoder")

        encoder.reset()
        time.sleep(0.1)

        encconfig = (i2cEncoderMiniLib.WRAP_ENABLE | i2cEncoderMiniLib.DIRE_LEFT
                     | i2cEncoderMiniLib.RMOD_X1)
        encoder.begin(encconfig)

        reg = (i2cEncoderMiniLib.PUSHP | i2cEncoderMiniLib.RINC | i2cEncoderMiniLib.RDEC)
        encoder.writeInterruptConfig(reg)

        encoder.writeCounter(0)
        encoder.writeMax(100)
        encoder.writeMin(0)
        encoder.writeStep(1)
        encoder.writeDoublePushPeriod(10)

        self.init.mutex_release(self.mutex, "i2cencoder:init_encoder")

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
        When using a shared interrupt pin, this function loops through all encoders
        to determine which one triggered the interrupt.
        """
        while True:
            # Check if an interrupt is pending.
            if self.active_interrupt:
                # Reset the active interrupt flag.
                self.active_interrupt = False

                # Loop through all encoders to find the one that triggered the interrupt.
                for idx, encoder in enumerate(self.encoders):
                    # Acquire the mutex for thread-safe I2C access.
                    self.init.mutex_acquire(self.mutex, "i2cencoder_mini:process_interrupt:read_status")

                    # Check the status of the current encoder.
                    check_status = encoder.updateStatus()

                    # Release the mutex.
                    self.init.mutex_release(self.mutex, "i2cencoder_mini:process_interrupt:read_status")

                    # If this encoder triggered the interrupt, process it.
                    if check_status:
                        status = encoder.stat

                        # Handle rotary encoder changes.
                        if status & (i2cEncoderMiniLib.RINC | i2cEncoderMiniLib.RDEC):
                            direction = 1 if status & i2cEncoderMiniLib.RINC else -1
                            super().rotary_encoder_change(idx, direction)
                            break

                        # Handle button presses.
                        if status & i2cEncoderMiniLib.PUSHP:
                            super().switch_click(idx + 1)
                            break

                # Sleep briefly to avoid busy-waiting.
                await asyncio.sleep(0.01)
