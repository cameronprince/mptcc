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
    def __init__(
        self,
        i2c_instance,
        i2c_addr=0x20,
        host_interrupt_pin=None,
        host_interrupt_pin_pull_up=True,
        encoder=None,
        switch=None,
    ):
        if encoder is None and switch is None:
            return

        self.encoder = encoder
        self.switch = switch
        self.init = init
        self.class_name = self.__class__.__name__
        self.interrupt = None
        self.init_complete = [False]
        self.instance_number = len(self.init.universal_instances.get("mcp23017", []))

        # Prepare the I2C bus.
        if i2c_instance == 2:
            self.init.init_i2c_2()
            self.i2c = self.init.i2c_2
            self.mutex = self.init.i2c_2_mutex
        else:
            self.init.init_i2c_1()
            self.i2c = self.init.i2c_1
            self.mutex = self.init.i2c_1_mutex

        # Initialize the MCP23017 driver.
        self.init.mutex_acquire(self.mutex, f"{self.class_name}:__init__")
        self.mcp = MCP23017_Driver(self.i2c, i2c_addr)
        self.init.mutex_release(self.mutex, f"{self.class_name}:__init__")

        self._configure()

        # Store in init before initializing hardware.
        if "mcp23017" not in self.init.universal_instances:
            self.init.universal_instances["mcp23017"] = []
        self.init.universal_instances["mcp23017"].append(self)

        print(f"MCP23017 {self.instance_number} initialized on I2C_{i2c_instance} ({hex(i2c_addr)})")
        print(f"- Host interrupt pin: {host_interrupt_pin} (pull_up={host_interrupt_pin_pull_up})")

        # Configure interrupt pin.
        self.host_int = Pin(
            host_interrupt_pin, 
            Pin.IN, 
            Pin.PULL_UP if host_interrupt_pin_pull_up else None
        )
        self.host_int.irq(trigger=Pin.IRQ_FALLING, handler=self._interrupt)

        # Initialize switches if configured.
        if switch is not None and switch.get("enabled", True):
            self._init_switches()

        # Initialize encoders if configured.
        if encoder is not None and encoder.get("enabled", True):
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
        if "mcp23017_switch" not in self.init.input_instances:
            self.init.input_instances["mcp23017_switch"] = []

        port = self.switch.get("port", "B").upper()
        self.init.input_instances["mcp23017_switch"].append([
            Switch_MCP23017(self.init, self.mcp, self.switch)
        ])

        print(f"- Switches initialized on port {port} (pull_up={self.switch.get('pull_up', False)})")
        for i, pin in enumerate(self.switch.get("pins", [])):
            print(f"  - Switch {i+1}: Pin {pin}")

    def _init_encoders(self):
        """Initialize encoder hardware and instances."""
        if "mcp23017_encoder" not in self.init.input_instances:
            self.init.input_instances["mcp23017_encoder"] = []
        
        encoder_instance = Encoder_MCP23017(
            self.init,
            self.mcp,
            self.encoder,
        )
        self.init.input_instances["mcp23017_encoder"].append([encoder_instance])

        port = self.encoder.get("port", "A").upper()
        pull_up = self.encoder.get("pull_up", False)
        
        print(f"- Encoders initialized on port {port} (pull_up={pull_up})")
        
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
        # Process switches
        for switch_handlers in self.init.input_instances.get("mcp23017_switch", []):
            for handler in switch_handlers:
                for instance in handler.instances:
                    pin = instance['pin']
                    port = instance['port']
                    index = instance['index']
                    mask = (1 << pin) if port == "A" else (1 << (pin + 8))
                    if intf & mask:
                        state = (intcap & mask) == 0  # Active-low: 0 = pressed
                        if state:  # Only on press
                            handler.process_interrupt(index)

        # Process encoders
        for encoder_handlers in self.init.input_instances.get("mcp23017_encoder", []):
            for handler in encoder_handlers:
                for instance in handler.instances:
                    clk_pin = instance['clk_pin']
                    dt_pin = instance['dt_pin']
                    port = instance['port']
                    index = instance['index']
                    clk_mask = (1 << clk_pin) if port == "A" else (1 << (clk_pin + 8))
                    dt_mask = (1 << dt_pin) if port == "A" else (1 << (dt_pin + 8))
                    if intf & clk_mask:
                        clk_state = (intcap & clk_mask) != 0  # True if high (1), False if low (0)
                        dt_state = (intcap & dt_mask) != 0    # True if high (1), False if low (0)
                        prev_clk = self.prev_clk_states[index]
                        direction = self._determine_direction(index, clk_state, dt_state, prev_clk)
                        self.prev_clk_states[index] = 1 if clk_state else 0  # Update state
                        if direction:
                            handler.process_interrupt(index, direction)

    def _determine_direction(self, encoder_idx, clk_state, dt_state, prev_clk):
        """
        Determine encoder rotation direction based on CLK and DT states.
        
        Args:
            encoder_idx (int): Index of the encoder.
            clk_state (bool): Current CLK state (True = high, False = low).
            dt_state (bool): Current DT state (True = high, False = low).
            prev_clk (int): Previous CLK state (1 = high, 0 = low).
        
        Returns:
            int: 1 for CW, -1 for CCW, None if no direction detected.
        """
        direction = None
        if prev_clk == 1 and clk_state == 0:  # Falling edge only.
            direction = 1 if dt_state else -1  # CW = 1, CCW = -1.
        return direction


class Encoder_MCP23017(Input):
    """MCP23017-based rotary encoder interface."""
    def __init__(self, init, mcp, encoder):
        super().__init__()
        self.init = init
        self.mcp = mcp
        self.encoder = encoder
        self.instances = []
        self.states = []
        
        port = encoder.get("port", "A").upper()
        for i, (clk_pin, dt_pin) in enumerate(encoder.get("pins", [])):
            self.instances.append({
                'clk_pin': clk_pin,
                'dt_pin': dt_pin,
                'port': port,
                'index': i,
            })
            self.states.append(0b00)

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
