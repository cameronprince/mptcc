"""
MicroPython Tesla Coil Controller (MPTCC)
by Cameron Prince
teslauniverse.com

hardware/input/i2cencoder.py
Input module for I2CEncoder V2.1.
"""

import time
import uasyncio as asyncio
import struct
import i2cEncoderLibV2
from machine import Pin, I2C
from ...hardware.init import init
from ..input.input import Input

class I2CEncoder(Input):

    def __init__(self):
        super().__init__()

        self.init = init
        self.encoders = []

        self.init_complete = False

        # Validate that the number of encoders and interrupts matches NUMBER_OF_COILS
        if len(self.init.I2CENCODER_ADDRESSES) != self.init.NUMBER_OF_COILS or \
           len(self.init.I2CENCODER_INTERRUPTS) != self.init.NUMBER_OF_COILS:
            raise ValueError(
                f"The number of I2C encoder addresses ({len(self.init.I2CENCODER_ADDRESSES)}) "
                f"and interrupt pins ({len(self.init.I2CENCODER_INTERRUPTS)}) must match "
                f"NUMBER_OF_COILS ({self.init.NUMBER_OF_COILS}). The program will now exit."
            )

        if self.init.I2CENCODER_I2C_INSTANCE == 2:
            self.init.init_i2c_2()
            self.i2c = self.init.i2c_2
            self.mutex = self.init.i2c_2_mutex
        else:
            self.init.init_i2c_1()
            self.i2c = self.init.i2c_1
            self.mutex = self.init.i2c_1_mutex

        self.interrupts = []
        self.active_interrupt = -1
        self.last_rotations = [0] * self.init.NUMBER_OF_COILS

        # Single loop to handle both interrupt pins and encoder addresses
        for i in range(self.init.NUMBER_OF_COILS):
            # Set up interrupt pins
            int_pin = self.init.I2CENCODER_INTERRUPTS[i]
            ip = Pin(int_pin, Pin.IN)
            ip.irq(trigger=Pin.IRQ_FALLING, handler=self.interrupt_handler)
            self.interrupts.append(ip)

            # Initialize encoders
            addr = self.init.I2CENCODER_ADDRESSES[i]
            encoder = i2cEncoderLibV2.i2cEncoderLibV2(self.i2c, addr)
            self.encoders.append(encoder)
            self.init_encoder(encoder)

        self.init_complete = True

        asyncio.create_task(self.process_interrupt())

    def init_encoder(self, encoder):
        self.init.mutex_acquire(self.mutex, "i2cencoder:init_encoder")
        # self.mutex.acquire()
        encoder.reset()
        time.sleep(0.1)

        if (self.init.I2CENCODER_TYPE == 'RGB'):
            type = i2cEncoderLibV2.RGB_ENCODER
        else:
            type = i2cEncoderLibV2.STD_ENCODER

        encconfig = (i2cEncoderLibV2.INT_DATA | i2cEncoderLibV2.WRAP_ENABLE
                     | i2cEncoderLibV2.DIRE_RIGHT | i2cEncoderLibV2.IPUP_ENABLE
                     | i2cEncoderLibV2.RMOD_X1 | type)
        encoder.begin(encconfig)

        reg = (i2cEncoderLibV2.PUSHP | i2cEncoderLibV2.RINC | i2cEncoderLibV2.RDEC)
        encoder.writeEncoder8(i2cEncoderLibV2.REG_INTCONF, reg)

        encoder.writeCounter(0)
        encoder.writeMax(100)
        encoder.writeMin(0)
        encoder.writeStep(1)
        encoder.writeAntibouncingPeriod(10)

        # Enable clock stretching by reading, modifying and writing GCONF2.
        current_gconf2 = encoder.readEncoder8(i2cEncoderLibV2.REG_GCONF2)
        new_gconf2 = current_gconf2 | (i2cEncoderLibV2.CLK_STRECH_ENABLE >> 8)
        encoder.writeEncoder8(i2cEncoderLibV2.REG_GCONF2, new_gconf2)

        if (self.init.I2CENCODER_TYPE == 'RGB'):
            encoder.writeGammaRLED(i2cEncoderLibV2.GAMMA_2)
            encoder.writeGammaGLED(i2cEncoderLibV2.GAMMA_2)
            encoder.writeGammaBLED(i2cEncoderLibV2.GAMMA_2)
            encoder.writeGammaBLED(i2cEncoderLibV2.GAMMA_2)
        self.init.mutex_release(self.mutex, "i2cencoder:init_encoder")
        # self.mutex.release()

    def interrupt_handler(self, pin):
        if not self.init_complete or not pin:
            return
        self.active_interrupt = self.interrupts.index(pin)

    async def process_interrupt(self):
        while True:
            if self.active_interrupt != -1:
                idx = self.active_interrupt
                self.active_interrupt = -1

                self.init.mutex_acquire(self.mutex, "i2cencoder:process_interrupt:read_status")
                # self.mutex.acquire()

                status = self.encoders[idx].readEncoder8(i2cEncoderLibV2.REG_ESTATUS)
                self.init.mutex_release(self.mutex, "i2cencoder:process_interrupt:read_status")
                # self.mutex.release()

                if status & (i2cEncoderLibV2.RINC | i2cEncoderLibV2.RDEC):
                    direction = 1 if status & i2cEncoderLibV2.RINC else -1
                    super().rotary_encoder_change(idx, direction)
                if status & i2cEncoderLibV2.PUSHP:
                    super().switch_click(idx + 1)

            await asyncio.sleep(0.01)
