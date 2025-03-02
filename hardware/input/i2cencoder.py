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

        # Flag to track initialization status.
        self.init_complete = False

        # Validate that the number of encoders matches NUMBER_OF_COILS.
        if len(self.init.I2CENCODER_ADDRESSES) != self.init.NUMBER_OF_COILS:
            raise ValueError(
                f"The number of I2C encoder addresses ({len(self.init.I2CENCODER_ADDRESSES)}) "
                f"must match NUMBER_OF_COILS ({self.init.NUMBER_OF_COILS}). The program will now exit."
            )

        # Prepare the I2C bus.
        if self.init.I2CENCODER_I2C_INSTANCE == 2:
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
        if not hasattr(self.init, 'I2CENCODER_SHARED_INTERRUPT_PIN'):
            raise ValueError(
                "I2CENCODER_SHARED_INTERRUPT_PIN must be defined in the init object."
            )

        self.interrupt_pin = Pin(self.init.I2CENCODER_SHARED_INTERRUPT_PIN, Pin.IN, Pin.PULL_UP)
        self.interrupt_pin.irq(trigger=Pin.IRQ_FALLING, handler=self.interrupt_handler)

        # Initialize encoders.
        for i in range(self.init.NUMBER_OF_COILS):
            addr = self.init.I2CENCODER_ADDRESSES[i]
            encoder = i2cEncoderLibV2.i2cEncoderLibV2(self.i2c, addr)
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
        self.init.mutex_acquire(self.mutex, "i2cencoder:init_encoder")

        encoder.reset()
        time.sleep(0.1)

        if self.init.I2CENCODER_TYPE == 'RGB':
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

        if self.init.I2CENCODER_TYPE == 'RGB':
            encoder.writeGammaRLED(i2cEncoderLibV2.GAMMA_2)
            encoder.writeGammaGLED(i2cEncoderLibV2.GAMMA_2)
            encoder.writeGammaBLED(i2cEncoderLibV2.GAMMA_2)
            encoder.writeGammaBLED(i2cEncoderLibV2.GAMMA_2)

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
                print("Interrupt detected! Checking encoders...")
                # Reset the active interrupt flag.
                self.active_interrupt = False

                # Loop through all encoders to find the one that triggered the interrupt.
                for idx, encoder in enumerate(self.encoders):
                    print(f"Checking encoder {idx}...")
                    # Acquire the mutex for thread-safe I2C access.
                    self.init.mutex_acquire(self.mutex, "i2cencoder:process_interrupt:read_status")

                    # Check the status of the current encoder.
                    status = encoder.readEncoder8(i2cEncoderLibV2.REG_ESTATUS)

                    # Release the mutex.
                    self.init.mutex_release(self.mutex, "i2cencoder:process_interrupt:read_status")

                    # If this encoder triggered the interrupt, process it.
                    if status:
                        print(f"Encoder {idx} status: {status} (hex: {hex(status)})")

                        # Handle rotary encoder changes.
                        if status & (i2cEncoderLibV2.RINC | i2cEncoderLibV2.RDEC):
                            direction = 1 if status & i2cEncoderLibV2.RINC else -1
                            print(f"Encoder {idx} rotated: direction = {direction}")
                            super().rotary_encoder_change(idx, direction)
                            # Break out of the loop since we've found the encoder that triggered the interrupt.
                            break

                        # Handle button presses.
                        if status & i2cEncoderLibV2.PUSHP:
                            print(f"Encoder {idx} button pressed!")
                            super().switch_click(idx + 1)
                            # Break out of the loop since we've found the encoder that triggered the interrupt.
                            break

                        # If the status is not a valid event, continue to the next encoder.
                        print(f"Encoder {idx} status {status} (hex: {hex(status)}) is not a valid event. Continuing to next encoder...")

            # Sleep briefly to avoid busy-waiting.
            await asyncio.sleep(0.01)
