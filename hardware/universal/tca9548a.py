"""
MicroPython Tesla Coil Controller (MPTCC)
by Cameron Prince
teslauniverse.com

hardware/universal/tca9548a.py
Universal class for driving hardware via the TCA9548A I2C multiplexer.
"""

import _thread
import time
from machine import Pin, I2C
from ...hardware.init import init


class TCA9548AChannel:
    def __init__(self, mux, channel, mutex):
        self.mux = mux
        self.channel = int(channel)
        self.mutex = mutex
        self.init = mux.init
        self.class_name = self.__class__.__name__

    def writeto(self, addr, buf, **kwargs):
        self.init.mutex_acquire(self.mutex, f"{self.class_name}:{self.channel}:writeto")
        try:
            self.mux.select_channel(self.channel)
            return self.mux.i2c.writeto(addr, buf, **kwargs)
        finally:
            self.init.mutex_release(self.mutex, f"{self.class_name}:{self.channel}:writeto")

    def writevto(self, addr, buffers, **kwargs):
        # Write vector to device on this channel.
        self.init.mutex_acquire(self.mutex, f"{self.class_name}:{self.channel}:writevto")
        try:
            self.mux.select_channel(self.channel)
            return self.mux.i2c.writevto(addr, buffers, **kwargs)
        finally:
            self.init.mutex_release(self.mutex, f"{self.class_name}:{self.channel}:writevto")

    def readfrom(self, addr, nbytes, **kwargs):
        # Read from device on this channel.
        self.init.mutex_acquire(self.mutex, f"{self.class_name}:{self.channel}:readfrom")
        try:
            self.mux.select_channel(self.channel)
            return self.mux.i2c.readfrom(addr, nbytes, **kwargs)
        finally:
            self.init.mutex_release(self.mutex, f"{self.class_name}:{self.channel}:readfrom")


class TCA9548A:
    def __init__(self, i2c_instance, i2c_addr=0x70, display=None):
        self.init = init
        self.i2c_addr = i2c_addr
        self.instances = []
        self.instance_number = len(self.init.universal_instances.get("tca9548a", []))

        # Initialize I2C first.
        if i2c_instance == 2:
            self.init.init_i2c_2()
            self.i2c = self.init.i2c_2
            self.mutex = self.init.i2c_2_mutex
        else:
            self.init.init_i2c_1()
            self.i2c = self.init.i2c_1
            self.mutex = self.init.i2c_1_mutex

        # Store in init before initializing hardware.
        if "tca9548a" not in self.init.universal_instances:
            self.init.universal_instances["tca9548a"] = []
        self.init.universal_instances["tca9548a"].append(self)

        print(f"TCA9548A {self.instance_number} initialized on I2C_{i2c_instance} ({hex(i2c_addr)})")

        # Initialize displays if configured.
        if display is not None:
            self._init_displays(display)

    def _init_displays(self, display_config):
        # Initialize displays after I2C is ready.
        for driver_name, driver_config in display_config.items():
            if "class" not in driver_config:
                continue

            if driver_name not in self.init.display_instances:
                self.init.display_instances[driver_name] = []
            
            display_instances = []
            common_cfg = driver_config.get("common_cfg", {})
            
            for instance_cfg in driver_config.get("instances", []):
                if not instance_cfg.get("enabled", True):
                    continue
                    
                # Create config using compatible dictionary operations.
                config = common_cfg.copy()
                config.update(instance_cfg)
                config.update({
                    "i2c_instance": f"tca9548a_{self.instance_number}",
                    "channel": int(instance_cfg["channel"])
                })
                config.pop("enabled", None)
                
                from ..display.ssd1306 import SSD1306
                try:
                    display = SSD1306(**config)
                    display_instances.append(display)
                except Exception as e:
                    print(f"Failed to initialize display on channel {config["channel"]}: {e}")
                finally:
                    pass

            # Store instances in the same format as init._initialize_driver_instance.
            if display_instances:
                # Append the list of instances directly (not nested).
                self.init.display_instances[driver_name].extend(display_instances)
                self.instances.extend(display_instances)

    def select_channel(self, channel):
        if channel < 0 or channel > 7:
            raise ValueError("Channel must be 0-7")
        self.i2c.writeto(self.i2c_addr, bytes([1 << channel]))

    def disable_all(self):
        self.i2c.writeto(self.i2c_addr, bytes([0]))
