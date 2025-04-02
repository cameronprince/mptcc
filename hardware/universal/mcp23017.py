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
        self.interrupt = {}
        self.init_complete = [False]
        self.encoder_states = {}
        self.switch_states = {}
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

        self.init_complete[0] = True
        # Start the polling task.
        asyncio.create_task(self._poll())

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
        defval_mask = 0x0000
        intcon_mask = 0x0000

        # Build masks for encoders.
        if encoder_pins:
            for clk_pin, dt_pin in encoder_pins:
                if encoder_port == "A":
                    port_mask |= (1 << clk_pin) | (1 << dt_pin)
                    # Set CLK high and DT low as default comparison values
                    defval_mask |= (1 << clk_pin)
                    intcon_mask |= (1 << clk_pin) | (1 << dt_pin)
                else:
                    port_mask |= (1 << (clk_pin + 8)) | (1 << (dt_pin + 8))
                    defval_mask |= (1 << (clk_pin + 8))
                    intcon_mask |= (1 << (clk_pin + 8)) | (1 << (dt_pin + 8))
            
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
            interrupt_polarity=0,    # (INTPOL) Active-high interrupt.
            interrupt_open_drain=0,  # (ODR) Push-pull output.
            sda_slew=0,              # (DISSLW) Disable slew rate control.
            sequential_operation=0,  # (SEQOP) Enable sequential operation.
            interrupt_mirror=1,      # (MIRROR) Mirror interrupts on both INT pins.
            bank=0,                  # (BANK) Sequential registers
        )

        # 16-bit configuration.
        self.mcp.mode |= port_mask                         # IODIR
        self.mcp.pullup |= pullup_mask                     # GPPU
        self.mcp.input_polarity |= port_mask               # IPOL
        print(f"defval_mask: {defval_mask}")
        print(f"intcon_mask: {intcon_mask}")
        # self.mcp.default_value = defval_mask              # DEFVAL
        # self.mcp.interrupt_compare_default = intcon_mask  # INTCON
        self.mcp.interrupt_enable = port_mask             # GPINTEN

        _ = self.mcp.interrupt_flag         # Read INTF (porta|b.interrupt_flag)
        _ = self.mcp.interrupt_captured     # Read INTCAP (porta|b.interrupt_captured)

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
        for i, (pin_1, pin_2) in enumerate(self.encoder.get("pins", [])):
            self.encoder_states[i] = {
                'state': 0,
                'clk_pin': pin_1,
                'dt_pin': pin_2,
                'port': port
            }
            print(f"  - Encoder {i+1}: Pins {pin_1} and {pin_2}")

    def _interrupt(self, pin):
        if not self.init_complete[0]:
            return

        # Check Port A first.
        flagged_a = self.mcp.porta.interrupt_flag
        if flagged_a != 0:
            self.init.mutex_acquire(self.mutex, f"{self.class_name}:interrupt_captured:a")
            captured_a = self.mcp.porta.interrupt_captured
            self.init.mutex_release(self.mutex, f"{self.class_name}:interrupt_captured:a")
            self.interrupt = [flagged_a, captured_a, "A"]
        else:
            # Only check Port B if Port A had no activity.
            flagged_b = self.mcp.portb.interrupt_flag
            if flagged_b != 0:
                self.init.mutex_acquire(self.mutex, f"{self.class_name}:interrupt_captured:b")
                captured_b = self.mcp.portb.interrupt_captured
                self.init.mutex_release(self.mutex, f"{self.class_name}:interrupt_captured:b")
                self.interrupt = [flagged_b, captured_b, "B"]

    async def _poll(self):
        """
        Asyncio task to process MCP23017 interrupts.
        """
        while True:
            if isinstance(self.interrupt, (tuple, list)) and len(self.interrupt) == 3:
                print(self.interrupt)
                flagged, captured, port = self.interrupt
                self.interrupt = None
                self._process_interrupt(flagged, captured, port)
            await asyncio.sleep(0.01)

    def _process_interrupt(self, flagged, captured, port):
        if not hasattr(self.init, 'input_instances'):
            return

        print(f"_process_interrupt - flagged: {flagged}, captured: {captured}, port: {port}")

        for handler in self.init.input_instances.get("mcp23017_switch", []):
            print(f"checking for switch handler: {handler}")
            for h in handler:
                # First filter instances by port
                matching_instances = [inst for inst in h.instances if inst['port'] == port]
                if not matching_instances:
                    print("port mismatch for all switch instances")
                    continue
                    
                for inst in matching_instances:
                    print(f"checking instances: {inst}")
                    print("processing switch interrupt")
                    if flagged & (1 << inst['pin']):
                        current_state = (captured >> inst['pin']) & 1
                        
                        if inst['index'] not in self.switch_states:
                            self.switch_states[inst['index']] = current_state
                        
                        if current_state == 0 and self.switch_states[inst['index']] == 1:
                            h.process_interrupt(inst['index'])
                        
                        self.switch_states[inst['index']] = current_state
                        return

        for handler in self.init.input_instances.get("mcp23017_encoder", []):
            print(f"checking for encoder handler: {handler}")
            for h in handler:
                # First filter instances by port
                matching_instances = [inst for inst in h.instances if inst['port'] == port]
                if not matching_instances:
                    print("port mismatch for all encoder instances")
                    continue
                    
                for inst in matching_instances:
                    print(f"checking instances: {inst}")
                    print("processing encoder interrupt")
                    if flagged & ((1 << inst['clk_pin']) | (1 << inst['dt_pin'])):
                        clk = (captured >> inst['clk_pin']) & 1
                        dt = (captured >> inst['dt_pin']) & 1
                        
                        encoder_state = self.encoder_states[inst['index']]
                        print(f"encoder_state: {encoder_state}")
                        encoder_state['state'] = (encoder_state['state'] & 0x3f) << 2 | (clk << 1) | dt
                        print(f"encoder_state['state']: {encoder_state['state']}")
                        if encoder_state['state'] == 180:
                            h.process_interrupt(inst['index'], 1)
                            return
                        elif encoder_state['state'] == 120:
                            h.process_interrupt(inst['index'], -1)
                            return


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
