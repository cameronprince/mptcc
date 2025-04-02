from mcp23017 import MCP23017
from machine import I2C, Pin
import time

class Rotary():
    def __init__(self, port, int_pin, clk, dt, cb=None, start_val=0, min_val=0, max_val=10):
        self.port = port
        self.clk = clk
        self.dt = dt
        self.cb = cb

        # initial value
        self.value = start_val
        self.min_val = min_val
        self.max_val = max_val

        pins = (1 << clk | 1 << dt)

        # input
        self.port.mode |= pins
        self.port.pullup |= pins
        self.port.input_polarity |= pins
        self.port.interrupt_enable |= pins

        # interrupt pin, set as input
        self.int_pin = int_pin
        self.int_pin.init(mode=int_pin.IN)

        # last 4 states (2-bits each)
        self.state = 0

    def _step(self, val):
        self.value = min(self.max_val, max(self.min_val, self.value + val))
        self._callback()

    def _switched(self, val):
        self.sw_state = val
        self._callback()

    def _rotated(self, clk, dt):
        # shuffle left and add current 2-bit state
        self.state = (self.state & 0x3f) << 2 | (clk << 1) | dt
        if self.state == 180:
            self._step(-1)
        elif self.state == 120:
            self._step(1)

    def _callback(self):
        if callable(self.cb):
            self.cb(self.value)

    def _irq(self, p):
        flagged = self.port.interrupt_flag
        captured = self.port.interrupt_captured
        clk = (captured >> self.clk) & 1
        dt = (captured >> self.dt) & 1
        if (flagged & (1 << self.clk | 1 << self.dt)) > 0:
            self._rotated(clk, dt)

    def start(self):
        self.int_pin.irq(trigger=self.int_pin.IRQ_FALLING, handler=self._irq)
        print(f"INT pin {self.int_pin} configured: {self.int_pin.value()}")
        # clear previous interrupt, if any
        self.port.interrupt_captured

    def stop(self):
        self.int_pin.irq(None)
        # clear previous interrupt, if any
        self.port.interrupt_captured


# Initialize I2C
i2c = I2C(0, scl=Pin(17), sda=Pin(16), freq=400000)
mcp = MCP23017(i2c)
mcp.config(interrupt_mirror=1)

# interrupt pin
interrupt_pin = Pin(18, mode=Pin.IN)

# encoder pins
clk_pin = 1
dt_pin = 0

def cb(val):
    volume = '\u2590' * val + '\xb7' * (10 - val)
    print(volume)

r = Rotary(mcp.porta, interrupt_pin, clk_pin, dt_pin, cb)

r.start()
