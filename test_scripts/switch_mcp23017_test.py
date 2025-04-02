from machine import I2C, Pin
import time

# MCP23017 Registers
MCP23017_ADDRESS = 0x27  # Default I2C address (A2=A1=A0=0)
IODIRA = 0x00  # I/O Direction Register for PORTA
GPPUA = 0x0C  # Pull-Up Resistor Register for PORTA
GPINTENA = 0x04  # Interrupt-on-Change Enable Register for PORTA
INTCONA = 0x08  # Interrupt Control Register for PORTA
GPIOA = 0x12  # GPIO Register for PORTA
INTCAPA = 0x10  # Interrupt Capture Register for PORTA

# Initialize I2C
i2c = I2C(0, scl=Pin(17), sda=Pin(16), freq=400000)

# Initialize interrupt pin
int_pin = Pin(15, Pin.IN, Pin.PULL_UP)  # MCP23017 INTA connected to GPIO 21

# Function to write to MCP23017 register
def write_register(reg, value):
    i2c.writeto_mem(MCP23017_ADDRESS, reg, bytearray([value]))

# Function to read from MCP23017 register
def read_register(reg):
    return i2c.readfrom_mem(MCP23017_ADDRESS, reg, 1)[0]

# Configure MCP23017 for interrupts
def setup_mcp23017():
    # Set PA0-PA5 as inputs (IODIRA register)
    write_register(IODIRA, 0b00111111)  # PA0-PA5 as inputs (1 = input, 0 = output)

    # Enable pull-up resistors for PA0-PA5 (GPPUA register)
    write_register(GPPUA, 0b00111111)  # PA0-PA5 pull-ups enabled (1 = enabled)

    # Enable interrupt-on-change for PA0-PA5 (GPINTENA register)
    write_register(GPINTENA, 0b00111111)  # PA0-PA5 interrupt-on-change enabled

    # Set interrupt to trigger on any change (INTCONA register)
    write_register(INTCONA, 0b00000000)  # Interrupt on any change (not compared to DEFVALA)

    # Clear any pending interrupts by reading INTCAPA
    read_register(INTCAPA)

# Track the state of each switch
switch_states = [1] * 6  # 1 = released, 0 = pressed

# Interrupt handler
def handle_interrupt(pin):
    # Read the interrupt capture register (INTCAPA) to determine which switch changed
    int_cap = read_register(INTCAPA)
    for i in range(6):  # Check each switch (PA0-PA5)
        current_state = (int_cap >> i) & 1  # Read the state of the switch (0 = pressed, 1 = released)
        if current_state != switch_states[i]:  # State changed
            switch_states[i] = current_state
            if current_state == 0:  # Switch pressed
                print(f"Switch {i} pressed")
            else:  # Switch released
                print(f"Switch {i} released")

    # Clear interrupt flag by reading GPIOA
    read_register(GPIOA)

# Attach interrupt handler to the interrupt pin
int_pin.irq(trigger=Pin.IRQ_FALLING, handler=handle_interrupt)

# Main loop
def main():
    setup_mcp23017()
    print("MCP23017 interrupt test started. Press switches to trigger interrupts.")
    while True:
        time.sleep(1)  # Keep the program running

# Run the main loop
main()