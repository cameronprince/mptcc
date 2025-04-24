"""
MicroPython Tesla Coil Controller (MPTCC)
by Cameron Prince
teslauniverse.com

hardware/universal/mcp23017.py
MCP23017 universal class for driving hardware.
"""

from mcp23017 import MCP23017 as MCP23017_Driver
import time
import asyncio
from machine import Pin, I2C
from ..input.input import Input
from ...hardware.init import init


class MCP23017:
    """
    A class to provide hardware instances using the MCP23017 GPIO expander.
    """
    def __init__(self, config):

        self.i2c_instance = config.get("i2c_instance", 1)
        self.i2c_addr = config.get("i2c_addr", 0x20)
        self.host_interrupt_pin = config.get("host_interrupt_pin", None)
        self.host_interrupt_pin_pull_up = config.get("host_interrupt_pin_pull_up", False)
        self.encoder = config.get("encoder", None)
        self.switch = config.get("switch", None)
        self.machine_name = "mcp23017"

        if self.encoder is None and self.switch is None:
            return

        self.init = init
        self.class_name = self.__class__.__name__
        self.interrupt = None
        self.init_complete = [False]
        self.instance_number = len(self.init.universal_instances.get(self.machine_name, []))

        # Prepare the I2C bus.
        if self.i2c_instance == 2:
            self.init.init_i2c_2()
            self.i2c = self.init.i2c_2
            self.mutex = self.init.i2c_2_mutex
        else:
            self.init.init_i2c_1()
            self.i2c = self.init.i2c_1
            self.mutex = self.init.i2c_1_mutex

        # Initialize the MCP23017 driver.
        self.init.mutex_acquire(self.mutex, f"{self.class_name}:__init__")
        self.mcp = MCP23017_Driver(self.i2c, self.i2c_addr)
        self.init.mutex_release(self.mutex, f"{self.class_name}:__init__")

        self._configure()

        # Store in init before initializing hardware.
        if self.machine_name not in self.init.universal_instances:
            self.init.universal_instances[self.machine_name] = []
        self.init.universal_instances[self.machine_name].append(self)

        print(f"MCP23017 {self.instance_number} initialized on I2C_{self.i2c_instance} ({hex(self.i2c_addr)})")
        print(f"- Host interrupt pin: {self.host_interrupt_pin} (pull_up={self.host_interrupt_pin_pull_up})")

        # Configure interrupt pin.
        self.host_int = Pin(
            self.host_interrupt_pin, 
            Pin.IN, 
            Pin.PULL_UP if self.host_interrupt_pin_pull_up else None
        )
        self.host_int.irq(trigger=Pin.IRQ_FALLING, handler=self._interrupt)

        # Initialize switches if configured.
        if self.switch is not None and self.switch.get("enabled", True):
            self._init_switches()

        # Initialize encoders if configured.
        if self.encoder is not None and self.encoder.get("enabled", True):
            self._init_encoders()

        # Start the polling task.
        asyncio.create_task(self._poll())

        self.init_complete[0] = True

    def _configure(self):
        # Prepare pin data.
        switch_pins = self.switch.get("pins", [])
        encoder_pins = self.encoder.get("pins", [])

        # Get port settings.
        switch_port = self.switch.get("port", "B").upper()
        encoder_port = self.encoder.get("port", "A").upper()

        # Initialize 16-bit masks.
        port_mask = 0x0000
        pullup_mask = 0x0000

        # Build masks for encoders.
        if encoder_pins:
            for clk_pin, dt_pin in encoder_pins:
                if encoder_port == "A":
                    port_mask |= (1 << clk_pin) | (1 << dt_pin)
                else:
                    port_mask |= (1 << (clk_pin + 8)) | (1 << (dt_pin + 8))
            
            if self.encoder.get("pull_up", False):
                for clk_pin, dt_pin in encoder_pins:
                    if encoder_port == "A":
                        pullup_mask |= (1 << clk_pin) | (1 << dt_pin)
                    else:
                        pullup_mask |= (1 << (clk_pin + 8)) | (1 << (dt_pin + 8))

        # Build masks for switches.
        if switch_pins:
            for pin in switch_pins:
                if switch_port == "A":
                    port_mask |= (1 << pin)
                else:
                    port_mask |= (1 << (pin + 8))
            
            if self.switch.get("pull_up", False):
                for pin in switch_pins:
                    if switch_port == "A":
                        pullup_mask |= (1 << pin)
                    else:
                        pullup_mask |= (1 << (pin + 8))

        self.init.mutex_acquire(self.mutex, f"{self.class_name}:_configure")

        # Configure the IOCON register.
        self.mcp.config(
            interrupt_polarity=0,    # (INTPOL) Active-low interrupt.
            interrupt_open_drain=0,  # (ODR) Push-pull output.
            sda_slew=0,              # (DISSLW) Disable slew rate control.
            sequential_operation=0,  # (SEQOP) Enable sequential operation.
            interrupt_mirror=1,      # (MIRROR) Mirror interrupts on both INT pins.
            bank=0,                  # (BANK) Sequential registers
        )

        # 16-bit configuration.
        self.mcp.mode |= port_mask                         # IODIR
        self.mcp.pullup |= pullup_mask                     # GPPU
        self.mcp.interrupt_enable = port_mask              # GPINTEN

        _ = self.mcp.interrupt_flag         # Read INTF (porta|b.interrupt_flag).
        _ = self.mcp.interrupt_captured     # Read INTCAP (porta|b.interrupt_captured).

        self.init.mutex_release(self.mutex, f"{self.class_name}:_configure")

    def _init_switches(self):
        if "switch" not in self.init.input_instances:
            self.init.input_instances["switch"] = {}
        if self.machine_name not in self.init.input_instances["switch"]:
            self.init.input_instances["switch"][self.machine_name] = []
        switch_instances = []
        switch_instance = Switch_MCP23017(self.init, self.mcp, self.switch)
        switch_instances.append(switch_instance)
        self.init.input_instances["switch"][self.machine_name].append(MCP23017_Switch(switch_instances))
        port = self.switch.get("port", "B").upper()
        print(f"- Switches initialized on port {port} (pull_up={self.switch.get('pull_up', False)})")
        for i, pin in enumerate(self.switch.get("pins", [])):
            print(f"  - Switch {i+1}: Pin {pin}")

    def _init_encoders(self):
        """Initialize encoder hardware and instances."""
        if "encoder" not in self.init.input_instances:
            self.init.input_instances["encoder"] = {}
        if self.machine_name not in self.init.input_instances["encoder"]:
            self.init.input_instances["encoder"][self.machine_name] = []
        encoder_instances = []
        encoder_instance = Encoder_MCP23017(self.init, self.mcp, self.encoder)
        encoder_instances.append(encoder_instance)
        self.init.input_instances["encoder"][self.machine_name].append(MCP23017_Encoder(encoder_instances))
        port = self.encoder.get("port", "A").upper()
        pull_up = self.encoder.get("pull_up", False)
        print(f"- Encoders initialized on port {port} (pull_up={pull_up})")
        for i, (clk_pin, dt_pin) in enumerate(self.encoder.get("pins", [])):
            print(f"  - Encoder {i}: CLK={clk_pin}, DT={dt_pin}")
        # Initialize state tracking for each encoder.
        self.prev_clk_states = [1] * len(self.encoder.get("pins", []))

    def _interrupt(self, pin):
        if not self.init_complete[0]:
            return
        self.init.mutex_acquire(self.mutex, f"{self.class_name}:_interrupt")
        intf = self.mcp.interrupt_flag
        intcap = self.mcp.interrupt_captured
        self.init.mutex_release(self.mutex, f"{self.class_name}:_interrupt")
        self.interrupt = (intf, intcap)

    async def _poll(self):
        """
        Asyncio task to process MCP23017 interrupts.
        """
        while True:
            if self.interrupt is not None:
                intf, intcap = self.interrupt
                self._process_interrupt(intf, intcap)
                self.interrupt = None
            await asyncio.sleep(0.001)

    def _process_interrupt(self, intf, intcap):
        """
        Process MCP23017 interrupts by delegating to switch and encoder instances.
        
        Args:
            intf (int): Interrupt flags (INTF register).
            intcap (int): Captured pin states (INTCAP register).
        """
        encoder_processed = False
        state = False
        
        # Process encoders first
        for handler in self.init.input_instances["encoder"].get(self.machine_name, []):
            for encoder_instance in handler.instances:
                for instance in encoder_instance.instances:
                    clk_pin = instance['clk_pin']
                    dt_pin = instance['dt_pin']
                    port = instance['port']
                    index = instance['index']
                    clk_mask = (1 << clk_pin) if port == "A" else (1 << (clk_pin + 8))
                    dt_mask = (1 << dt_pin) if port == "A" else (1 << (dt_pin + 8))
                    if intf & (clk_mask | dt_mask):  # Check both CLK and DT
                        clk_state = (intcap & clk_mask) != 0  # True if high
                        dt_state = (intcap & dt_mask) != 0    # True if high
                        direction = encoder_instance.determine_direction(index, clk_state, dt_state)
                        if direction:
                            encoder_instance.process_interrupt(index, direction)
                            encoder_processed = True
                            break  # Exit innermost loop after handling encoder interrupt
                if encoder_processed:
                    break  # Exit encoder_instance loop
            if encoder_processed:
                break  # Exit handler loop

        # Process switches only if no encoder interrupt was handled
        if not encoder_processed:
            for handler in self.init.input_instances["switch"].get(self.machine_name, []):
                for switch_instance in handler.instances:
                    for instance in switch_instance.instances:
                        pin = instance['pin']
                        port = instance['port']
                        index = instance['index']
                        mask = (1 << pin) if port == "A" else (1 << (pin + 8))
                        if intf & mask:
                            state = (intcap & mask) == 0  # Active-low: 0 = pressed
                            if state:  # Only on press
                                switch_instance.process_interrupt(index)
                                break  # Exit innermost loop after handling switch interrupt
                    if state:  # Break outer loop if switch was processed
                        break
                if state:
                    break


class Encoder_MCP23017(Input):
    """MCP23017-based rotary encoder interface."""
    def __init__(self, init, mcp, encoder):
        super().__init__()
        self.init = init
        self.mcp = mcp
        self.encoder = encoder
        self.instances = []
        self.prev_states = []
        
        port = encoder.get("port", "A").upper()
        for i, (clk_pin, dt_pin) in enumerate(encoder.get("pins", [])):
            self.instances.append({
                'clk_pin': clk_pin,
                'dt_pin': dt_pin,
                'port': port,
                'index': i,
            })
            self.prev_states.append((1, 1))

    def determine_direction(self, index, clk_state, dt_state):
        """
        Determine encoder rotation direction using half quadrature decoding.
        
        Args:
            index (int): Index of the encoder.
            clk_state (bool): Current CLK state (True = high, False = low).
            dt_state (bool): Current DT state (True = high, False = low).
        
        Returns:
            int: 1 for CW, -1 for CCW, None if no direction detected.
        """
        prev_clk, prev_dt = self.prev_states[index]
        self.prev_states[index] = (clk_state, dt_state)
        
        # Half quadrature: process falling edge of CLK or DT
        if prev_clk == 1 and clk_state == 0:  # CLK falling edge
            return 1 if dt_state else -1  # CW if DT high, CCW if DT low
        elif prev_dt == 1 and dt_state == 0:  # DT falling edge
            return -1 if clk_state else 1  # CCW if CLK high, CW if CLK low
        return None

    def process_interrupt(self, index, direction):
        """Wrapper for handling encoder interrupt."""
        if direction is not None:
            super().encoder_change(index, direction)


class Switch_MCP23017(Input):
    """MCP23017-based switch interface."""
    def __init__(self, init, mcp, switch):
        super().__init__()
        self.init = init
        self.mcp = mcp
        self.switch = switch
        self.instances = []

        port = switch.get("port", "B").upper()
        for i, pin in enumerate(self.switch.get("pins", [])):
            self.instances.append({
                'pin': pin,
                'port': port,
                'index': i,
            })

    def process_interrupt(self, index):
        """Wrapper for handling switch interrupt."""
        super().switch_click(index + 1)


class MCP23017_Switch:
    def __init__(self, switch_instances):
        self.instances = switch_instances


class MCP23017_Encoder:
    def __init__(self, encoder_instances):
        self.instances = encoder_instances
