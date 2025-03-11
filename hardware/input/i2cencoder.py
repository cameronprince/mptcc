"""
MicroPython Tesla Coil Controller (MPTCC)
by Cameron Prince
teslauniverse.com

hardware/input/i2cencoder.py
Input module for I2CEncoder V2.1.
"""

import time
from machine import Pin
from ...lib.duppa import DuPPa
from ...hardware.init import init
from ..input.input import Input
from ...lib.utils import hex_to_rgb
import uasyncio as asyncio

# Constants and register definitions
CONSTANTS = {
    # Register definitions
    "REG_GCONF": 0x00,
    "REG_INTCONF": 0x04,
    "REG_ESTATUS": 0x05,
    "REG_GCONF2": 0x30,
    "REG_PUSHP": 0x02,
    "REG_RINC": 0x08,
    "REG_RDEC": 0x10,
    "REG_CVALB4": 0x08,
    "REG_CMAXB4": 0x0C,
    "REG_CMINB4": 0x10,
    "REG_ISTEPB4": 0x14,
    "REG_ANTBOUNC": 0x1E,
    "REG_GAMRLED": 0x27,
    "REG_GAMGLED": 0x28,
    "REG_GAMBLED": 0x29,
    "REG_RLED": 0x18,
    "REG_GLED": 0x19,
    "REG_BLED": 0x1A,

    # Configuration values
    "CLK_STRECH_ENABLE": 0x0100,
    "RGB_ENCODER": 0x0020,
    "STD_ENCODER": 0x0000,
    "GAMMA_2": 3,
    "INT_DATA": 0x0000,
    "WRAP_ENABLE": 0x0002,
    "DIRE_RIGHT": 0x0000,
    "IPUP_ENABLE": 0x0000,
    "RMOD_X1": 0x0000,

    # Reset constant
    "RESET": 0x80,
}

class I2CEncoder(Input):
    def __init__(self):
        super().__init__()

        self.init = init
        self.encoders = []
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

        # Print initialization details.
        print(f"I2CEncoder initialized on I2C_{self.init.I2CENCODER_I2C_INSTANCE} with {self.init.NUMBER_OF_COILS} encoders:")
        for i, addr in enumerate(self.init.I2CENCODER_ADDRESSES):
            print(f"- Encoder {i + 1}: I2C address 0x{addr:02X}")
        print(f"- Asyncio polling: {self.init.RGB_LED_ASYNCIO_POLLING}")

        # Shared variable for asyncio task.
        self.active_interrupt = False

        # Initialize last_rotations to track previous encoder values.
        self.last_rotations = [0] * self.init.NUMBER_OF_COILS

        self.interrupt_pin = Pin(self.init.I2CENCODER_INTERRUPT_PIN, Pin.IN, Pin.PULL_UP)
        self.interrupt_pin.irq(trigger=Pin.IRQ_FALLING, handler=self.interrupt_handler)

        # Initialize encoders.
        for i in range(self.init.NUMBER_OF_COILS):
            addr = self.init.I2CENCODER_ADDRESSES[i]
            encoder = DuPPa(self.i2c, addr, CONSTANTS)
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
            type = encoder.constants["RGB_ENCODER"]
        else:
            type = encoder.constants["STD_ENCODER"]

        encconfig = (encoder.constants["INT_DATA"] | encoder.constants["WRAP_ENABLE"]
                     | encoder.constants["DIRE_RIGHT"] | encoder.constants["IPUP_ENABLE"]
                     | encoder.constants["RMOD_X1"] | type)
        encoder.begin(encconfig)

        reg = (encoder.constants["REG_PUSHP"] | encoder.constants["REG_RINC"] | encoder.constants["REG_RDEC"])
        encoder.writeEncoder8(encoder.constants["REG_INTCONF"], reg)

        encoder.writeCounter(0)
        encoder.writeMax(100)
        encoder.writeMin(0)
        encoder.writeStep(1)
        encoder.writeAntibouncingPeriod(10)

        # Enable clock stretching by reading, modifying and writing GCONF2.
        current_gconf2 = encoder.readEncoder8(encoder.constants["REG_GCONF2"])
        new_gconf2 = current_gconf2 | (encoder.constants["CLK_STRECH_ENABLE"] >> 8)
        encoder.writeEncoder8(encoder.constants["REG_GCONF2"], new_gconf2)

        if self.init.I2CENCODER_TYPE == 'RGB':
            # Set gamma correction for RGB LEDs
            encoder.writeGammaRLED(encoder.constants["GAMMA_2"])
            encoder.writeGammaGLED(encoder.constants["GAMMA_2"])
            encoder.writeGammaBLED(encoder.constants["GAMMA_2"])
            
            # Set the default color with default brightness
            default_color = self.init.I2CENCODER_DEFAULT_COLOR
            r, g, b = hex_to_rgb(default_color)
            
            # Apply the default brightness
            dimmed_r = r * self.init.I2CENCODER_THRESHOLD_BRIGHTNESS // 255
            dimmed_g = g * self.init.I2CENCODER_THRESHOLD_BRIGHTNESS // 255
            dimmed_b = b * self.init.I2CENCODER_THRESHOLD_BRIGHTNESS // 255
            
            # Write the dimmed color to the encoder
            encoder.writeRGBCode((dimmed_r << 16) | (dimmed_g << 8) | dimmed_b)

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
        """
        while True:
            if self.active_interrupt:
                self.active_interrupt = False

                for idx, encoder in enumerate(self.encoders):
                    self.init.mutex_acquire(self.mutex, "i2cencoder:process_interrupt")
                    try:
                        status = encoder.readEncoder8(encoder.constants["REG_ESTATUS"])
                    except OSError as e:
                        print(f"I2CEncoder error in process_interrupt: {e}")
                        continue
                    finally:
                        self.init.mutex_release(self.mutex, "i2cencoder:process_interrupt")

                    if status:
                        if status & (encoder.constants["REG_RINC"] | encoder.constants["REG_RDEC"]):
                            direction = 1 if status & encoder.constants["REG_RINC"] else -1
                            super().encoder_change(idx, direction)
                            break

                        if status & encoder.constants["REG_PUSHP"] and self.init.integrated_switches:
                            super().switch_click(idx + 1)
                            break

            await asyncio.sleep(0.01)
