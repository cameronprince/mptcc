from machine import I2C, Pin
import time

# MCP23017 Registers (Port B)
MCP23017_ADDRESS = 0x20  # Default I2C address (A2=A1=A0=0)
IODIRB = 0x01    # I/O Direction Register for PORTB
GPPUB = 0x0D     # Pull-Up Resistor Register for PORTB
GPINTENB = 0x05  # Interrupt-on-Change Enable Register for PORTB
INTCONB = 0x09   # Interrupt Control Register for PORTB
GPIOB = 0x13     # GPIO Register for PORTB
INTCAPB = 0x11   # Interrupt Capture Register for PORTB

# Initialize I2C
i2c = I2C(0, scl=Pin(17), sda=Pin(16), freq=400000)

# Initialize interrupt pin (MCP23017 INTB connected to GPIO 15)
int_pin = Pin(18, Pin.IN, Pin.PULL_UP)

# Function to write to MCP23017 register
def write_register(reg, value):
    i2c.writeto_mem(MCP23017_ADDRESS, reg, bytearray([value]))

# Function to read from MCP23017 register
def read_register(reg):
    return i2c.readfrom_mem(MCP23017_ADDRESS, reg, 1)[0]

# Configure MCP23017 for interrupts (Port B)
def setup_mcp23017():
    # Set PB0-PB5 as inputs (IODIRB register)
    write_register(IODIRB, 0b00111111)  # PB0-PB5 as inputs (1 = input)

    # Enable pull-up resistors for PB0-PB5 (GPPUB register)
    write_register(GPPUB, 0b00111111)  # PB0-PB5 pull-ups enabled

    # Enable interrupt-on-change for PB0-PB5 (GPINTENB register)
    write_register(GPINTENB, 0b00111111)  # PB0-PB5 interrupt-on-change enabled

    # Set interrupt to trigger on any change (INTCONB register)
    write_register(INTCONB, 0b00000000)  # Interrupt on any change

    # Clear any pending interrupts by reading INTCAPB
    read_register(INTCAPB)

# Track the state of each switch (PB0-PB5)
switch_states = [1] * 6  # 1 = released, 0 = pressed

# Interrupt handler
def handle_interrupt(pin):
    # Read the interrupt capture register (INTCAPB) to determine which switch changed
    int_cap = read_register(INTCAPB)
    for i in range(6):  # Check each switch (PB0-PB5)
        current_state = (int_cap >> i) & 1  # State of the switch (0 = pressed, 1 = released)
        if current_state != switch_states[i]:
            switch_states[i] = current_state
            if current_state == 0:
                print(f"Switch {i} pressed (PB{i})")
            else:
                print(f"Switch {i} released (PB{i})")

    # Clear interrupt flag by reading GPIOB
    read_register(GPIOB)

# Attach interrupt handler to the interrupt pin
int_pin.irq(trigger=Pin.IRQ_FALLING, handler=handle_interrupt)

# Main loop
def main():
    setup_mcp23017()
    print("MCP23017 Port B interrupt test started. Press switches to trigger interrupts.")
    while True:
        time.sleep(1)

# Run the main loop
main()