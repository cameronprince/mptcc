"""
MicroPython Tesla Coil Controller (MPTCC)
by Cameron Prince
teslauniverse.com

hardware/input/i2cencoder.py
Input and RGB LED module for I2CEncoder V2.1.
Also supports I2CEncoder Mini.
"""

import time
import uasyncio as asyncio
from machine import Pin
from ...lib.duppa import DuPPa
from ...hardware.init import init
from ..input.input import Input
from ...lib.utils import hex_to_rgb
from ..rgb_led.rgb_led import RGB, RGBLED

# Constants and register definitions for both types
CONSTANTS = {
    "mini": {
        "REG_GCONF": 0x00,
        "REG_INTCONF": 0x01,
        "REG_ESTATUS": 0x02,
        "REG_CVALB4": 0x03,
        "REG_CMAXB4": 0x07,
        "REG_CMINB4": 0x0B,
        "REG_ISTEPB4": 0x0F,
        "REG_DPPERIOD": 0x13,
        "WRAP_ENABLE": 0x01,
        "DIRE_LEFT": 0x02,
        "RMOD_X1": 0x00,
        "RESET": 0x80,
        "PUSHP": 0x02,
        "RINC": 0x10,
        "RDEC": 0x20,
    },
    "rgb": {
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
}

class I2CEncoder(Input):
    def __init__(self, i2c_instance=1, i2c_addrs=[], interrupt_pin=None, type="rgb", default_color="#326400", threshold_brightness=32, full_brightness=255):
        super().__init__()
        self.init = init
        self.i2c_addrs = i2c_addrs
        self.interrupt_pin = interrupt_pin
        self.type = type
        self.default_color = default_color
        self.threshold_brightness = threshold_brightness
        self.full_brightness = full_brightness
        self.instances = []
        self.init_complete = False
        self.active_interrupt = False

        if i2c_instance == 2:
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
            encoder = DuPPa(self.i2c, addr, CONSTANTS[self.type])
            self.instances.append(encoder)
            self.init_encoder(encoder)

        self.init_complete = True
        asyncio.create_task(self.process_interrupt())

        instance_key = len(self.init.input_instances["encoder"]["i2cencoder"])

        if self.type == "rgb":
            self.init.RGB_LED_ASYNCIO_POLLING = True
            if 'i2cencoder' not in self.init.rgb_led_instances:
                self.init.rgb_led_instances['i2cencoder'] = []
            rgb_encoder_instances = []
            for instance in self.instances:
                led_instance = RGB_I2CEncoder(instance, self.mutex, self.default_color, self.threshold_brightness, self.full_brightness)
                rgb_encoder_instances.append(led_instance)
            self.init.rgb_led_instances['i2cencoder'].append(rgb_encoder_instances)

        print(f"I2CEncoder {instance_key} (type: {self.type}) initialized on I2C_{i2c_instance}")
        for i, addr in enumerate(self.i2c_addrs):
            print(f"- Encoder {i + 1}: I2C address 0x{addr:02X}")
        if self.type == "rgb":
            print(f"- RGB LEDs initialized (default color: {self.default_color})")
            print(f"- Asyncio polling: {self.init.RGB_LED_ASYNCIO_POLLING}")

    def init_encoder(self, encoder):
        self.init.mutex_acquire(self.mutex, "i2cencoder:init_encoder")
        encoder.reset()
        time.sleep(0.1)

        if self.type == "mini":
            encconfig = (CONSTANTS[self.type]["WRAP_ENABLE"] | CONSTANTS[self.type]["DIRE_LEFT"] | CONSTANTS[self.type]["RMOD_X1"])
            encoder.begin(encconfig)
            reg = (CONSTANTS[self.type]["PUSHP"] | CONSTANTS[self.type]["RINC"] | CONSTANTS[self.type]["RDEC"])
            encoder.writeInterruptConfig(reg)
            encoder.writeCounter(0)
            encoder.writeMax(100)
            encoder.writeMin(0)
            encoder.writeStep(1)
            encoder.writeDoublePushPeriod(10)
        else:
            encoder_type = CONSTANTS[self.type]["RGB_ENCODER"] if self.type == "rgb" else CONSTANTS[self.type]["STD_ENCODER"]
            encconfig = (CONSTANTS[self.type]["INT_DATA"] | CONSTANTS[self.type]["WRAP_ENABLE"] |
                         CONSTANTS[self.type]["DIRE_RIGHT"] | CONSTANTS[self.type]["IPUP_ENABLE"] |
                         CONSTANTS[self.type]["RMOD_X1"] | encoder_type)
            encoder.begin(encconfig)
            reg = (CONSTANTS[self.type]["REG_PUSHP"] | CONSTANTS[self.type]["REG_RINC"] | CONSTANTS[self.type]["REG_RDEC"])
            encoder.writeEncoder8(CONSTANTS[self.type]["REG_INTCONF"], reg)
            encoder.writeCounter(0)
            encoder.writeMax(100)
            encoder.writeMin(0)
            encoder.writeStep(1)
            encoder.writeAntibouncingPeriod(10)
            current_gconf2 = encoder.readEncoder8(CONSTANTS[self.type]["REG_GCONF2"])
            new_gconf2 = current_gconf2 | (CONSTANTS[self.type]["CLK_STRECH_ENABLE"] >> 8)
            encoder.writeEncoder8(CONSTANTS[self.type]["REG_GCONF2"], new_gconf2)
            if self.type == "rgb":
                encoder.writeGammaRLED(CONSTANTS[self.type]["GAMMA_2"])
                encoder.writeGammaGLED(CONSTANTS[self.type]["GAMMA_2"])
                encoder.writeGammaBLED(CONSTANTS[self.type]["GAMMA_2"])
                r, g, b = hex_to_rgb(self.default_color)
                dimmed_r = r * self.threshold_brightness // 255
                dimmed_g = g * self.threshold_brightness // 255
                dimmed_b = b * self.threshold_brightness // 255
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
                    if self.type == "mini":
                        self.init.mutex_acquire(self.mutex, "i2cencoder_mini:process_interrupt")
                        try:
                            if encoder.updateStatus():
                                status = encoder.readStatusRaw()
                                if status & (CONSTANTS[self.type]["RINC"] | CONSTANTS[self.type]["RDEC"]):
                                    direction = 1 if status & CONSTANTS[self.type]["RINC"] else -1
                                    super().encoder_change(idx, direction)
                                    break
                                if status & CONSTANTS[self.type]["PUSHP"] and self.init.integrated_switches:
                                    super().switch_click(idx + 1)
                                    break
                        finally:
                            self.init.mutex_release(self.mutex, "i2cencoder_mini:process_interrupt")
                    else:
                        self.init.mutex_acquire(self.mutex, "i2cencoder:process_interrupt")
                        try:
                            status = encoder.readEncoder8(CONSTANTS[self.type]["REG_ESTATUS"])
                        except OSError as e:
                            print(f"I2CEncoder error in process_interrupt: {e}")
                            # continue
                        finally:
                            self.init.mutex_release(self.mutex, "i2cencoder:process_interrupt")

                        if status:
                            if status & (CONSTANTS[self.type]["REG_RINC"] | CONSTANTS[self.type]["REG_RDEC"]):
                                direction = 1 if status & CONSTANTS[self.type]["REG_RINC"] else -1
                                super().encoder_change(idx, direction)
                                break

                            if status & CONSTANTS[self.type]["REG_PUSHP"] and self.init.integrated_switches:
                                super().switch_click(idx + 1)
                                break
            await asyncio.sleep(0.05)

class RGB_I2CEncoder(RGB):
    def __init__(self, encoder, mutex, default_color, threshold_brightness, full_brightness):
        super().__init__()
        self.encoder = encoder
        self.mutex = mutex
        self.default_color = hex_to_rgb(default_color)
        self.threshold_brightness = threshold_brightness
        self.full_brightness = full_brightness
        self.init = init

    def set_color(self, r, g, b):
        if r == 0 and g == 0 and b == 0:
            r, g, b = self.default_color
            dimmed_r = r * self.threshold_brightness // 255
            dimmed_g = g * self.threshold_brightness // 255
            dimmed_b = b * self.threshold_brightness // 255
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
