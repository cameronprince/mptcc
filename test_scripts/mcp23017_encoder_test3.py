import machine
import time
import uasyncio as asyncio
from machine import Pin, PWM

# I2C setup
i2c = machine.I2C(0, scl=Pin(17), sda=Pin(16), freq=400000)
i2c_addr = 0x20
from mcp23017 import MCP23017 as driver
mcp = driver(i2c, i2c_addr)

# Pin definitions for 4 encoders and 4 switches
encoder_pins = [
    [0, 1],  # Encoder 0: CLK, DT
    [2, 3],  # Encoder 1
    [4, 5],  # Encoder 2
    [6, 7],  # Encoder 3
]
encoder_port = "A"
switch_pins = [0, 1, 2, 3]  # Switch pins on Port B
switch_port = "B"
interrupt_pin = 18

# Beep configuration
beep_pin = 15
beep_volume = 100
beep_pwm_freq = 3000
beep_duty = int((beep_volume / 100) * 65535)
pwm = PWM(Pin(beep_pin))
pwm.freq(beep_pwm_freq)
pwm.duty_u16(0)  # Off by default

# Set default mask values
port_mask = 0x0000
pullup_mask = 0x0000

# Loop over encoder pins to set masks (Port A)
for clk_pin, dt_pin in encoder_pins:
    port_mask |= (1 << clk_pin) | (1 << dt_pin)
    pullup_mask |= (1 << clk_pin) | (1 << dt_pin)

# Loop over switch pins to set masks (Port B)
for pin in switch_pins:
    port_mask |= (1 << (pin + 8))
    pullup_mask |= (1 << (pin + 8))

# Configure MCP23017
mcp.config(
    interrupt_polarity=0,  # Active-low interrupt
    interrupt_open_drain=0,
    sda_slew=0,
    sequential_operation=0,
    interrupt_mirror=1,  # Mirror INTA and INTB
    bank=0,
)
mcp.mode |= port_mask  # Set pins as inputs
mcp.pullup |= pullup_mask  # Enable internal pull-ups
mcp.interrupt_enable = port_mask  # Enable interrupts on all pins
_ = mcp.interrupt_flag  # Clear any pending interrupts
_ = mcp.interrupt_captured

# Beep function (non-blocking)
async def chirp():
    pwm.duty_u16(beep_duty)  # Turn on
    await asyncio.sleep_ms(10)  # Short chirp
    pwm.duty_u16(0)  # Turn off

# Global interrupt flags and state tracking
input_interrupt = False
prev_clk_states = [1] * len(encoder_pins)  # Assume high due to pull-ups

# Interrupt handling
def determine_direction(encoder_idx, clk_state, dt_state, prev_clk):
    direction = None
    if prev_clk == 1 and clk_state == 0:  # Falling edge only
        direction = "CW" if dt_state else "CCW"
    return direction

def process_interrupt(intf, intcap):
    # Check switches (Port B)
    for i, pin in enumerate(switch_pins):
        mask = 1 << (pin + 8)
        if intf & mask:
            state = (intcap & mask) == 0  # Active-low: 0 = pressed
            print(f"Switch {i} {'pressed' if state else 'released'}")
            if state:  # Chirp only on press
                asyncio.create_task(chirp())
    # Check encoders (Port A)
    for i, (clk_pin, dt_pin) in enumerate(encoder_pins):
        clk_mask = 1 << clk_pin
        dt_mask = 1 << dt_pin
        if intf & clk_mask:
            clk_state = (intcap & clk_mask) != 0  # True if high (1), False if low (0)
            dt_state = (intcap & dt_mask) != 0    # True if high (1), False if low (0)
            prev_clk = prev_clk_states[i]
            direction = determine_direction(i, clk_state, dt_state, prev_clk)
            prev_clk_states[i] = 1 if clk_state else 0  # Update state
            if direction:
                print(f"Encoder {i} turned {direction}")
                asyncio.create_task(chirp())  # Chirp on rotation
    # Clear interrupts
    _ = mcp.interrupt_flag
    _ = mcp.gpio

def setup_irq():
    pin = Pin(interrupt_pin, Pin.IN, Pin.PULL_UP)
    pin.irq(trigger=Pin.IRQ_FALLING, handler=input_callback)
    return pin

def input_callback(pin):
    global input_interrupt
    input_interrupt = True
    intf = mcp.interrupt_flag
    intcap = mcp.interrupt_captured
    process_interrupt(intf, intcap)

# Set up interrupt on GPIO 18
print(f"Setting up interrupt on pin {interrupt_pin}")
irq_pin = setup_irq()

# Polling task
async def poll_inputs():
    global input_interrupt
    while True:
        if input_interrupt:
            input_interrupt = False
        await asyncio.sleep(0.01)

# Initialize and start
print("Initializing switches and encoders:")
for i, pin in enumerate(switch_pins):
    print(f"Switch {i} initialized on pin {pin} (Port B)")
for i, (pin1, pin2) in enumerate(encoder_pins):
    print(f"Encoder {i} initialized on pins {pin1}, {pin2} (Port A)")

print("Encoders and switches are ready for testing")
asyncio.create_task(poll_inputs())
loop = asyncio.get_event_loop()
loop.run_forever()