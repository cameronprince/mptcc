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
        self.i2c_error = False # Added error flag.

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
        self.last_rotations = [0] * len(self.init.I2CENCODER_ADDRESSES)

        for int_pin in self.init.I2CENCODER_INTERRUPTS:
            ip = Pin(int_pin, Pin.IN)
            ip.irq(trigger=Pin.IRQ_FALLING, handler=self.interrupt_handler)
            self.interrupts.append(ip)

        self.encoders = [i2cEncoderLibV2.i2cEncoderLibV2(self.i2c, addr) for addr in self.init.I2CENCODER_ADDRESSES]

        self.init_all_encoders() #combined init encoders and init complete into one function.

        asyncio.create_task(self.process_interrupt())

    def init_all_encoders(self):
        for encoder in self.encoders:
            self.init_encoder(encoder)
        self.init_complete = True

    def init_encoder(self, encoder):
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

            # Enable clock stretching by reading, modifying and writing GCONF2
            current_gconf2 = encoder.readEncoder8(i2cEncoderLibV2.REG_GCONF2)
            new_gconf2 = current_gconf2 | (i2cEncoderLibV2.CLK_STRECH_ENABLE >> 8) #shift the bit down by 8 bits.
            encoder.writeEncoder8(i2cEncoderLibV2.REG_GCONF2, new_gconf2)

            if (self.init.I2CENCODER_TYPE == 'RGB'):
                encoder.writeGammaRLED(i2cEncoderLibV2.GAMMA_2)
                encoder.writeGammaGLED(i2cEncoderLibV2.GAMMA_2)
                encoder.writeGammaBLED(i2cEncoderLibV2.GAMMA_2)
                encoder.writeGammaBLED(i2cEncoderLibV2.GAMMA_2)

    def interrupt_handler(self, pin):
        if not self.init_complete or not pin or self.i2c_error: #prevent interrupts if error flag is set.
            return
        self.active_interrupt = self.interrupts.index(pin)

    async def process_interrupt(self):
        while True:
            if self.active_interrupt != -1:
                idx = self.active_interrupt
                self.active_interrupt = -1

                retries = 3
                for attempt in range(retries):
                    if self.i2c_error: #stop retrying if error flag is set.
                        break;
                    self.mutex.acquire()
                    try:
                        status = self.encoders[idx].readEncoder8(i2cEncoderLibV2.REG_ESTATUS)
                        if status & (i2cEncoderLibV2.RINC | i2cEncoderLibV2.RDEC):
                            valBytes = struct.unpack('>i', self.encoders[idx].readCounter32())
                            new_value = valBytes[0]
                            super().rotary_encoder_change(idx, new_value)
                        if status & i2cEncoderLibV2.PUSHP:
                            super().switch_click(idx + 1)
                        break
                    except OSError as e:
                        print(f"I2C communication error in process_interrupt (attempt {attempt + 1}): {e}")
                        if attempt == retries - 1:
                            print("Failed to process interrupt after multiple retries. Resetting I2C and encoders.")
                            self.i2c_error = True;
                            await self.reset_i2c_and_encoders()
                    finally:
                        self.mutex.release()
                    await asyncio.sleep(0.01)

            await asyncio.sleep(0.01)

    async def reset_i2c_and_encoders(self):
        if self.init.I2CENCODER_I2C_INSTANCE == 2:
            self.init.reset_i2c(2)
        else:
            self.init.reset_i2c(1)
        await asyncio.sleep(0.1)
        self.init_all_encoders()
        self.i2c_error = False

