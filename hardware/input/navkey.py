"""
MicroPython Tesla Coil Controller (MPTCC)
by Cameron Prince
teslauniverse.com

hardware/input/navkey.py
Input driver for DuPPA I2C NavKey.
"""

import time
import uasyncio as asyncio
from machine import Pin
from ...lib.duppa import DuPPa
from ...hardware.init import init
from ..input.input import Input

CONSTANTS = {
    "REG_GCONF": 0x00,
    "REG_INTCONF": 0x04,
    "REG_ISTATUS": 0x06,
    "REG_CVALB4": 0x0A,
    "REG_CMAXB4": 0x0E,
    "REG_CMINB4": 0x12,
    "REG_ISTEPB4": 0x16,
    "REG_DPPERIOD": 0x1D,
    "WRAP_ENABLE": 0x01,
    "DIRE_RIGHT": 0x00,
    "DIRE_LEFT": 0x04,
    "DTYPE_INT": 0x00,
    "RESET": 0x80,
    # Lower byte (bits 0-7) - Existing working constants
    "ICTRP": 0x0002,  # Center press, bit 1
    "RINC": 0x0008,   # CW, bit 3
    "RDEC": 0x0010,   # CCW, bit 4
    "SCTRP": 0x0002,  # Center status, bit 1
    "SRINC": 0x0008,  # CW status, bit 3
    "SRDEC": 0x0010,  # CCW status, bit 4
    # Upper byte (bits 8-15) - Arrow keys (base orientation, 0 degrees)
    "IUPP": 0x0800,   # Up press, bit 11
    "IDNP": 0x0200,   # Down press, bit 9
    "ILTP": 0x2000,   # Left press, bit 13
    "IRTP": 0x8000,   # Right press, bit 15
    "SUPP": 0x0800,   # Up status, bit 11
    "SDNP": 0x0200,   # Down status, bit 9
    "SLTP": 0x2000,   # Left status, bit 13
    "SRTP": 0x8000    # Right status, bit 15
}


class NavKey(Input):
    def __init__(self, config):
        super().__init__()
        self.init = init
        self.i2c_instance = config.get("i2c_instance", 1)
        self.i2c_addrs = config.get("i2c_addrs", [])
        self.interrupt_pin = config.get("interrupt_pin", None)
        self.rotation = config.get("rotation", 0)  # Store rotation value (0, 90, 180, 270)
        self.instances = []
        self.init_complete = False
        self.active_interrupt = False
        self.class_name = self.__class__.__name__

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
            navkey = DuPPa(self.i2c, addr, CONSTANTS)
            self.instances.append(navkey)
            self.init_navkey(navkey)

        self.init_complete = True
        asyncio.create_task(self.process_interrupt())

        instance_key = len(self.init.input_instances["encoder"]["navkey"])

        print(f"NavKey {instance_key} initialized on I2C_{self.i2c_instance}")
        for i, addr in enumerate(self.i2c_addrs):
            print(f"- {i}: I2C address 0x{addr:02X}")

    def init_navkey(self, navkey):
        self.init.mutex_acquire(self.mutex, f"{self.class_name}:init_navkey")
        navkey.reset()
        time.sleep(0.1)
        status = navkey.readEncoder16(CONSTANTS["REG_ISTATUS"])

        reg = (CONSTANTS["ICTRP"] |  # 0x0002
               CONSTANTS["RINC"]  |  # 0x0008
               CONSTANTS["RDEC"]  |  # 0x0010
               CONSTANTS["IUPP"]  |  # 0x0800
               CONSTANTS["IDNP"]  |  # 0x0200
               CONSTANTS["ILTP"]  |  # 0x2000
               CONSTANTS["IRTP"])    # 0x8000
        # reg = 0xAA1A
        navkey.writeEncoder16(CONSTANTS["REG_INTCONF"], reg)
        navkey.writeCounter(0)
        navkey.writeMax(100)
        navkey.writeMin(0)
        navkey.writeStep(1)

        self.init.mutex_release(self.mutex, f"{self.class_name}:init_navkey")

    def interrupt_handler(self, pin):
        if not self.init_complete:
            return
        self.active_interrupt = True

    def get_rotated_arrow_mapping(self):
        """Returns a dictionary mapping physical arrow key bits to logical actions based on rotation."""
        # Base mapping (0 degrees): Physical bit -> Logical action
        base_mapping = {
            CONSTANTS["SUPP"]: "up",    # 0x0800 -> Up
            CONSTANTS["SDNP"]: "down",  # 0x0200 -> Down
            CONSTANTS["SLTP"]: "left",  # 0x2000 -> Left
            CONSTANTS["SRTP"]: "right"  # 0x8000 -> Right
        }
        
        # Define rotation transformations (clockwise)
        rotations = {
            0:   ["up", "down", "left", "right"],  # No rotation
            90:  ["right", "left", "up", "down"],  # 90° CW: Up -> Right, Right -> Down, Down -> Left, Left -> Up
            180: ["down", "up", "right", "left"],  # 180°: Up -> Down, Down -> Up, Left -> Right, Right -> Left
            270: ["left", "right", "down", "up"]   # 270° CW: Up -> Left, Left -> Down, Down -> Right, Right -> Up
        }
        
        # Get the rotated actions for the specified rotation
        rotated_actions = rotations.get(self.rotation, rotations[0])  # Default to 0 if invalid
        
        # Create rotated mapping: Physical bit -> Rotated logical action
        rotated_mapping = {
            CONSTANTS["SUPP"]: rotated_actions[0],  # Physical Up bit
            CONSTANTS["SDNP"]: rotated_actions[1],  # Physical Down bit
            CONSTANTS["SLTP"]: rotated_actions[2],  # Physical Left bit
            CONSTANTS["SRTP"]: rotated_actions[3]   # Physical Right bit
        }
        
        return rotated_mapping

    async def process_interrupt(self):
        while True:
            if self.active_interrupt:
                self.active_interrupt = False
                for idx, navkey in enumerate(self.instances):
                    status = None
                    self.init.mutex_acquire(self.mutex, f"{self.class_name}:process_interrupt")
                    try:
                        reg_address = CONSTANTS["REG_ISTATUS"]  # 0x06
                        status = navkey.readEncoder16(reg_address)
                        # Encoder events
                        if status & CONSTANTS["SRINC"]:
                            super().encoder_change(idx, -1)  # CCW
                        elif status & CONSTANTS["SRDEC"]:
                            super().encoder_change(idx, 1)   # CW
                        # Center button press
                        if status & CONSTANTS["SCTRP"] and self.init.integrated_switches:
                            super().switch_click(idx + 1)    # Center
                        # Arrow key presses with rotation
                        arrow_mapping = self.get_rotated_arrow_mapping()
                        if status & CONSTANTS["SUPP"]:  # Physical Up bit
                            action = arrow_mapping[CONSTANTS["SUPP"]]
                            if action == "up":
                                # super().switch_click(idx + 2)
                                # print(f"Up arrow pressed (rotated)")
                                pass
                            elif action == "down":
                                # super().switch_click(idx + 3)
                                # print(f"Down arrow pressed (rotated)")
                                pass
                            elif action == "left":
                                # super().switch_click(idx + 4)
                                # print(f"Left arrow pressed (rotated)")
                                pass
                            elif action == "right":
                                # super().switch_click(idx + 5)
                                # print(f"Right arrow pressed (rotated)")
                                pass
                        if status & CONSTANTS["SDNP"]:  # Physical Down bit
                            action = arrow_mapping[CONSTANTS["SDNP"]]
                            if action == "up":
                                # super().switch_click(idx + 2)
                                # print(f"Up arrow pressed (rotated)")
                                pass
                            elif action == "down":
                                # super().switch_click(idx + 3)
                                # print(f"Down arrow pressed (rotated)")
                                pass
                            elif action == "left":
                                # super().switch_click(idx + 4)
                                # print(f"Left arrow pressed (rotated)")
                                pass
                            elif action == "right":
                                # super().switch_click(idx + 5)
                                # print(f"Right arrow pressed (rotated)")
                                pass
                        if status & CONSTANTS["SLTP"]:  # Physical Left bit
                            action = arrow_mapping[CONSTANTS["SLTP"]]
                            if action == "up":
                                # super().switch_click(idx + 2)
                                # print(f"Up arrow pressed (rotated)")
                                pass
                            elif action == "down":
                                # super().switch_click(idx + 3)
                                # print(f"Down arrow pressed (rotated)")
                                pass
                            elif action == "left":
                                # super().switch_click(idx + 4)
                                # print(f"Left arrow pressed (rotated)")
                                pass
                            elif action == "right":
                                # super().switch_click(idx + 5)
                                # print(f"Right arrow pressed (rotated)")
                                pass
                        if status & CONSTANTS["SRTP"]:  # Physical Right bit
                            action = arrow_mapping[CONSTANTS["SRTP"]]
                            if action == "up":
                                # super().switch_click(idx + 2)
                                # print(f"Up arrow pressed (rotated)")
                                pass
                            elif action == "down":
                                # super().switch_click(idx + 3)
                                # print(f"Down arrow pressed (rotated)")
                                pass
                            elif action == "left":
                                # super().switch_click(idx + 4)
                                # print(f"Left arrow pressed (rotated)")
                                pass
                            elif action == "right":
                                # super().switch_click(idx + 5)
                                # print(f"Right arrow pressed (rotated)")
                                pass
                    except OSError as e:
                        print(f"I2CEncoder error: {e}")
                    finally:
                        self.init.mutex_release(self.mutex, f"{self.class_name}:process_interrupt")
            await asyncio.sleep(0.05)
