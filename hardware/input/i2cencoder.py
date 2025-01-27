"""
MicroPython Tesla Coil Controller (MPTCC)
by Cameron Prince
teslauniverse.com

hardware/input/i2cencoder.py
Input module for I2CEncoder V2.1.
"""

import time
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

        # Prepare the I2C bus.
        self.init.init_i2c_2()

        self.interrupt_pin = Pin(self.init.PIN_I2CENCODER_INT, Pin.IN)
        self.interrupt_pin.irq(trigger=Pin.IRQ_FALLING, handler=self.interrupt_handler)

        # Instantiate the encoder objects.
        self.encoders = [i2cEncoderLibV2.i2cEncoderLibV2(self.init.i2c_2, addr) for addr in init.I2CENCODER_ADDRESSES]

        self.last_rotations = [0] * len(self.encoders)

        # Initialize each encoder.
        for encoder in self.encoders:
            self.init_encoder(encoder)

    # Initialize a specific encoder.
    def init_encoder(self, encoder):
        encoder.reset()
        time.sleep(0.1)

        encconfig = (i2cEncoderLibV2.INT_DATA | i2cEncoderLibV2.WRAP_ENABLE  # Enable wrapping
                     | i2cEncoderLibV2.DIRE_RIGHT | i2cEncoderLibV2.IPUP_ENABLE
                     | i2cEncoderLibV2.RMOD_X1 | i2cEncoderLibV2.RGB_ENCODER)
        encoder.begin(encconfig)

        reg = (i2cEncoderLibV2.PUSHP | i2cEncoderLibV2.RINC | i2cEncoderLibV2.RDEC)
        encoder.writeEncoder8(i2cEncoderLibV2.REG_INTCONF, reg)

        encoder.writeCounter(0)
        encoder.writeMax(100)
        encoder.writeMin(0)
        encoder.writeStep(1)
        encoder.writeAntibouncingPeriod(12)

    def interrupt_handler(self, pin):
        if pin.value() == 0:
            # Loop over all encoders to find the triggering instance.
            for idx, encoder in enumerate(self.encoders):
                # Read and reset the status.
                status = encoder.readEncoder8(i2cEncoderLibV2.REG_ESTATUS)
                # Fire the appropriate callback.
                if status & (i2cEncoderLibV2.RINC | i2cEncoderLibV2.RDEC):
                    valBytes = struct.unpack('>i', encoder.readCounter32())
                    new_value = valBytes[0]
                    self.rotary_encoder_change(idx, new_value)
                if status & i2cEncoderLibV2.PUSHP:
                    self.switch_click(idx + 1)
