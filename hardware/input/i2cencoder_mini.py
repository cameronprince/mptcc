"""
MicroPython Tesla Coil Controller (MPTCC)
by Cameron Prince
teslauniverse.com

hardware/input/i2cencoder_mini.py
Input module for I2CEncoder Mini.
"""

import time
import uasyncio as asyncio
from machine import Pin
from ...lib.duppa import DuPPa
from ...hardware.init import init
from ..input.input import Input

CONSTANTS = {
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
}


class I2CEncoderMini(Input):
    def __init__(self, config):
        super().__init__()
        self.init = init

        self.i2c_instance = config.get("i2c_instance", 1)
        self.i2c_addrs = config.get("i2c_addrs", [])
        self.interrupt_pin = config.get("interrupt_pin", None)
        self.master = config.get("master", False)

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

        instance_key = len(self.init.input_instances["encoder"]["i2cencoder_mini"])

        print(f"I2CEncoder Mini {instance_key} initialized on I2C_{self.i2c_instance}")
        for i, addr in enumerate(self.i2c_addrs):
            print(f"- {i}: I2C address 0x{addr:02X}{' (master)' if self.master else ''}")

    def init_encoder(self, encoder):
        self.init.mutex_acquire(self.mutex, "i2cencoder:init_encoder")
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
                    self.init.mutex_acquire(self.mutex, "i2cencoder_mini:process_interrupt")
                    try:
                        if encoder.updateStatus():
                            status = encoder.readStatusRaw()
                    finally:
                        self.init.mutex_release(self.mutex, "i2cencoder_mini:process_interrupt")
                    if status & (CONSTANTS["RINC"] | CONSTANTS["RDEC"]):
                        direction = 1 if status & CONSTANTS["RINC"] else -1
                        super().encoder_change(("master" if self.master else idx), direction)
                        break
                    if status & CONSTANTS["PUSHP"] and self.init.integrated_switches:
                        super().switch_click(("master" if self.master else (idx + 1)))
                        break
            await asyncio.sleep(0.05)
