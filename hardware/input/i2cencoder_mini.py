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

        # Prepare the I2C bus.
        if self.init.I2CENCODER_MINI_I2C_INSTANCE == 2:
            self.init.init_i2c_2()
            self.i2c = self.init.i2c_2
            self.mutex = self.init.i2c_2_mutex
        else:
            self.init.init_i2c_1()
            self.i2c = self.init.i2c_1
            self.mutex = self.init.i2c_1_mutex

        self.interrupts = []

        # Shared variable for asyncio task.
        # -1 means no interrupt, otherwise stores the encoder index.
        self.active_interrupt = -1

        # Initialize last_rotations to track previous encoder values
        self.last_rotations = [0] * len(self.init.I2CENCODER_MINI_ADDRESSES)

        # Set up interrupt pins.
        for int_pin in self.init.I2CENCODER_MINI_INTERRUPTS:
            ip = Pin(int_pin, Pin.IN, Pin.PULL_UP)
            ip.irq(trigger=Pin.IRQ_FALLING, handler=self.interrupt_handler)
            self.interrupts.append(ip)

        # Instantiate the encoder objects.
        self.encoders = [i2cEncoderMiniLib.i2cEncoderMiniLib(self.i2c, addr) for addr in self.init.I2CENCODER_MINI_ADDRESSES]

        # Initialize each encoder.
        for encoder in self.encoders:
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
        # self.mutex.acquire()

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
        # self.mutex.release()

    def interrupt_handler(self, pin):
        """
        Minimal interrupt handler. Sets the encoder index.
        """
        if not self.init_complete or not pin:
            return

        # Signal that an interrupt has occurred and pass the index
        # of the triggering encoder.
        self.active_interrupt = self.interrupts.index(pin)

    async def process_interrupt(self):
        """
        Asyncio task to process rotary and switch interrupts.
        """
        while True:
            # Check if an interrupt is pending.
            if self.active_interrupt != -1:
                idx = self.active_interrupt
                # Reset the active interrupt.
                self.active_interrupt = -1

                self.init.mutex_acquire(self.mutex, "i2cencoder_mini:process_interrupt:read_status")
                check_status = self.encoders[idx].updateStatus()
                self.init.mutex_release(self.mutex, "i2cencoder_mini:process_interrupt:read_status")

                if check_status:
                    status = self.encoders[idx].stat

                    if status & (i2cEncoderMiniLib.RINC | i2cEncoderMiniLib.RDEC):
                        direction = 1 if status & i2cEncoderMiniLib.RINC else -1
                        super().rotary_encoder_change(idx, direction)

                    if status & i2cEncoderMiniLib.PUSHP:
                        super().switch_click(idx + 1)

            await asyncio.sleep(0.01)
