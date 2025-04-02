import time
import asyncio
from machine import Pin, I2C
from mcp23017 import MCP23017 as MCP23017_Driver

class Init:
    def __init__(self):
        self.universal_instances = {}
        self.input_instances = {}
        self.i2c_1 = None

    def init_i2c_1(self):
        if self.i2c_1 is None:
            self.i2c_1 = I2C(0, scl=Pin(17), sda=Pin(16), freq=400000)

class Input:
    def encoder_change(self, index, direction):
        print(f"Encoder {index} changed: {'clockwise' if direction == 1 else 'counterclockwise'}")

    def switch_click(self, index):
        print(f"Switch {index} clicked")

class MCP23017:
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
        self.init = Init()
        self.class_name = self.__class__.__name__
        self.interrupt = {}
        self.init_complete = [False]
        self.encoder_states = {}
        self.switch_states = {}
        self.instance_number = len(self.init.universal_instances.get("mcp23017", []))

        self.init.init_i2c_1()
        self.i2c = self.init.i2c_1

        # Initialize the MCP23017 driver.
        self.mcp = MCP23017_Driver(self.i2c, i2c_addr)

        self._configure()

        if "mcp23017" not in self.init.universal_instances:
            self.init.universal_instances["mcp23017"] = []
        self.init.universal_instances["mcp23017"].append(self)

        print(f"MCP23017 {self.instance_number} initialized on I2C_{i2c_instance} ({hex(i2c_addr)})")
        print(f"- Host interrupt pin: {host_interrupt_pin} (pull_up={host_interrupt_pin_pull_up})")

        self.host_int = Pin(
            host_interrupt_pin,
            Pin.IN,
            Pin.PULL_UP if host_interrupt_pin_pull_up else None
        )
        self.host_int.irq(trigger=Pin.IRQ_FALLING, handler=self._interrupt)

        if switch is not None and switch.get("enabled", True):
            self._init_switches()

        if encoder is not None and encoder.get("enabled", True):
            self._init_encoders()

        self.init_complete[0] = True
        asyncio.create_task(self._poll())

    def _configure(self):
        switch_pins = self.switch.get("pins", [])
        encoder_pins = self.encoder.get("pins", [])
        switch_port = self.switch.get("port", "B").upper()
        encoder_port = self.encoder.get("port", "A").upper()

        port_mask = 0x0000
        pullup_mask = 0x0000
        defval_mask = 0x0000
        intcon_mask = 0x0000

        if encoder_pins:
            for clk_pin, dt_pin in encoder_pins:
                if encoder_port == "A":
                    port_mask |= (1 << clk_pin) | (1 << dt_pin)
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

        self.mcp.config(
            interrupt_polarity=0,
            interrupt_open_drain=0,
            sda_slew=0,
            sequential_operation=0,
            interrupt_mirror=1,
            bank=0,
        )
        self.mcp.mode |= port_mask
        self.mcp.pullup |= pullup_mask
        self.mcp.input_polarity |= port_mask
        # print(f"defval_mask: {defval_mask}")
        # print(f"intcon_mask: {intcon_mask}")
        # self.mcp.default_value = defval_mask              # DEFVAL
        # self.mcp.interrupt_compare_default = intcon_mask  # INTCON
        self.mcp.interrupt_enable = port_mask
        _ = self.mcp.interrupt_flag
        _ = self.mcp.interrupt_captured

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
        if "mcp23017_encoder" not in self.init.input_instances:
            self.init.input_instances["mcp23017_encoder"] = []
        
        encoder_instance = Encoder_MCP23017(self.init, self.mcp, self.encoder)
        self.init.input_instances["mcp23017_encoder"].append([encoder_instance])

        port = self.encoder.get("port", "A").upper()
        pull_up = self.encoder.get("pull_up", False)
        
        print(f"- Encoders initialized on port {port} (pull_up={pull_up})")
        
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

        flagged_a = self.mcp.porta.interrupt_flag
        if flagged_a != 0:
            # No mutex
            captured_a = self.mcp.porta.interrupt_captured
            self.interrupt = [flagged_a, captured_a, "A"]
        else:
            flagged_b = self.mcp.portb.interrupt_flag
            if flagged_b != 0:
                # No mutex
                captured_b = self.mcp.portb.interrupt_captured
                self.interrupt = [flagged_b, captured_b, "B"]

    async def _poll(self):
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
        super().encoder_change(index, direction)

class Switch_MCP23017(Input):
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
        super().switch_click(index + 1)

# Configuration from your provided JSON
config = {
    "mcp23017": {
        "class": "MCP23017",
        "instances": [
            {
                "enabled": True,
                "i2c_instance": 1,
                "i2c_addr": 0x20,
                "host_interrupt_pin": 18,
                "host_interrupt_pin_pull_up": True,
                "switch": {
                    "enabled": True,
                    "port": "B",
                    "pins": [0, 1, 2, 3],
                    "pull_up": False,
                },
                "encoder": {
                    "enabled": True,
                    "port": "A",
                    "pins": [
                        [0, 1],
                        [2, 3],
                        [4, 5],
                        [6, 7],
                    ],
                    "pull_up": False,
                },
            },
        ],
    }
}

# Main function to run the test
async def main():
    instance_config = config["mcp23017"]["instances"][0]
    mcp = MCP23017(
        i2c_instance=instance_config["i2c_instance"],
        i2c_addr=instance_config["i2c_addr"],
        host_interrupt_pin=instance_config["host_interrupt_pin"],
        host_interrupt_pin_pull_up=instance_config["host_interrupt_pin_pull_up"],
        encoder=instance_config["encoder"],
        switch=instance_config["switch"],
    )
    # Keep the asyncio loop running
    while True:
        await asyncio.sleep(1)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Test stopped by user")
