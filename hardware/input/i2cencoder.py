"""
MicroPython Tesla Coil Controller (MPTCC)
by Cameron Prince
teslauniverse.com

hardware/input/i2cencoder.py
Input and RGB LED module for I2CEncoder V2.1.
"""

import time
import uasyncio as asyncio
from machine import Pin
from ...lib.duppa import DuPPa
from ...hardware.init import init
from ..input.input import Input
from ...lib.utils import hex_to_rgb, scale_rgb
from ..rgb_led.rgb_led import RGB, RGBLED

CONSTANTS = {
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
    "CLK_STRECH_ENABLE": 0x0100,
    "RGB_ENCODER": 0x0020,
    "STD_ENCODER": 0x0000,
    "GAMMA_2": 3,
    "INT_DATA": 0x0000,
    "WRAP_ENABLE": 0x0002,
    "DIRE_RIGHT": 0x0000,
    "IPUP_ENABLE": 0x0000,
    "RMOD_X1": 0x0000,
    "RESET": 0x80,
}

class I2CEncoder(Input):
    def __init__(self, config):
        super().__init__()
        self.init = init

        self.i2c_instance = config.get("i2c_instance", 1)
        self.i2c_addrs = config.get("i2c_addrs", [])
        self.interrupt_pin = config.get("interrupt_pin", None)
        self.type = config.get("type", None)
        self.default_color = config.get("default_color", "#000000")
        self.threshold_brightness = config.get("threshold_brightness", 0)
        self.asyncio_polling = config.get("asyncio_polling", False)

        self.instances = []
        self.init_complete = False
        self.active_interrupt = False

        if self.i2c_instance == 2:
            self.init.init_i2c_2()
            self.i2c = self.init.i2c_2
            self.mutex = self.init.i2c_2_mutex
        else:
            self.init.init_i2c_1()
            self.i2c = self.init.i2c_1
            self.mutex = self.init.i2c_1_mutex

        if self.interrupt_pin is not None:
            self.interrupt_pin = Pin(self.interrupt_pin, Pin.IN, Pin.PULL_UP)
            self.interrupt_pin.irq(trigger=Pin.IRQ_FALLING, handler=self.interrupt_handler)

        for addr in self.i2c_addrs:
            encoder = DuPPa(self.i2c, addr, CONSTANTS)
            self.instances.append(encoder)
            self.init_encoder(encoder)

        self.init_complete = True
        asyncio.create_task(self.process_interrupt())

        if self.type == "rgb":
            rgb_instances = []
            for instance in self.instances:
                led_instance = RGB_I2CEncoder(instance, self.mutex, config)
                rgb_instances.append(led_instance)
            if 'i2cencoder' not in self.init.rgb_led_instances:
                self.init.rgb_led_instances['i2cencoder'] = []
            self.init.rgb_led_instances['i2cencoder'].append(I2CEncoderRGB(rgb_instances))

        instance_key = len(self.init.input_instances["encoder"]["i2cencoder"])
        print(f"I2CEncoder {instance_key} (type: {self.type}) initialized on I2C_{self.i2c_instance}")
        for i, addr in enumerate(self.i2c_addrs):
            print(f"- {i}: I2C address 0x{addr:02X}")
        if self.type == "rgb":
            print(f"- RGB LEDs initialized (default color: {config.get("default_color")})")
            if self.asyncio_polling:
                print(f"- Asyncio polling: True")

    def init_encoder(self, encoder):
        self.init.mutex_acquire(self.mutex, "i2cencoder:init_encoder")
        encoder.reset()
        time.sleep(0.1)

        encoder_type = CONSTANTS["RGB_ENCODER"] if self.type == "rgb" else CONSTANTS["STD_ENCODER"]
        encconfig = (CONSTANTS["INT_DATA"] | CONSTANTS["WRAP_ENABLE"] |
                     CONSTANTS["DIRE_RIGHT"] | CONSTANTS["IPUP_ENABLE"] |
                     CONSTANTS["RMOD_X1"] | encoder_type)
        encoder.begin(encconfig)
        reg = (CONSTANTS["REG_PUSHP"] | CONSTANTS["REG_RINC"] | CONSTANTS["REG_RDEC"])
        encoder.writeInterruptConfig(reg)
        encoder.writeCounter(0)
        encoder.writeMax(100)
        encoder.writeMin(0)
        encoder.writeStep(1)
        encoder.writeAntibouncingPeriod(10)
        current_gconf2 = encoder.readEncoder8(CONSTANTS["REG_GCONF2"])
        new_gconf2 = current_gconf2 | (CONSTANTS["CLK_STRECH_ENABLE"] >> 8)
        encoder.writeEncoder8(CONSTANTS["REG_GCONF2"], new_gconf2)
        
        if self.type == "rgb":
            encoder.writeGammaRLED(CONSTANTS["GAMMA_2"])
            encoder.writeGammaGLED(CONSTANTS["GAMMA_2"])
            encoder.writeGammaBLED(CONSTANTS["GAMMA_2"])
            r, g, b = hex_to_rgb(self.default_color)
            dimmed_r, dimmed_g, dimmed_b = scale_rgb(r, g, b, self.threshold_brightness)
            encoder.writeRGBCode((dimmed_r << 16) | (dimmed_g << 8) | dimmed_b)

        self.init.mutex_release(self.mutex, "i2cencoder:init_encoder")

    def interrupt_handler(self, pin):
        if not self.init_complete:
            return
        self.active_interrupt = True

    async def process_interrupt(self):
        while True:
            if self.active_interrupt:
                self.active_interrupt = False
                for idx, encoder in enumerate(self.instances):
                    status = None
                    self.init.mutex_acquire(self.mutex, "i2cencoder:process_interrupt")
                    try:
                        status = encoder.readEncoder8(CONSTANTS["REG_ESTATUS"])
                    except OSError as e:
                        print(f"I2CEncoder error in process_interrupt: {e}")
                    finally:
                        self.init.mutex_release(self.mutex, "i2cencoder:process_interrupt")
                    if status:
                        if status & (CONSTANTS["REG_RINC"] | CONSTANTS["REG_RDEC"]):
                            direction = 1 if status & CONSTANTS["REG_RINC"] else -1
                            super().encoder_change(idx, direction)
                            break
                        if status & CONSTANTS["REG_PUSHP"]:
                            super().switch_click(idx + 1)
                            break
            await asyncio.sleep(0.05)


class I2CEncoderRGB:
    def __init__(self, rgb_instances):
        self.instances = rgb_instances


class RGB_I2CEncoder(RGB):
    def __init__(self, encoder, mutex, config):
        super().__init__()
        self.encoder = encoder
        self.mutex = mutex
        self.init = init

        self.default_color = hex_to_rgb(config.get("default_color", "#000000"))
        self.threshold_brightness = config.get("threshold_brightness", 0)
        self.full_brightness = config.get("full_brightness", 255)
        self.asyncio_polling = config.get("asyncio_polling", False)

    def set_color(self, r, g, b):
        if r == 0 and g == 0 and b == 0:
            r, g, b = self.default_color
            dimmed_r, dimmed_g, dimmed_b = scale_rgb(r, g, b, self.threshold_brightness)
            color_code = (dimmed_r << 16) | (dimmed_g << 8) | dimmed_b
        else:
            color_code = (r << 16) | (g << 8) | b

        self.init.mutex_acquire(self.mutex, "i2cencoder:set_color")
        try:
            self.encoder.writeRGBCode(color_code)
        except OSError as e:
            print(f"I2CEncoder error: {e}")
        finally:
            self.init.mutex_release(self.mutex, "i2cencoder:set_color")
