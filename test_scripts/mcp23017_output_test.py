"""
MCP23017 Direct Register Access Test Script
Pulses pins PA0-PA3 high and low at 5 Hz by directly writing to MCP23017 registers.
"""

from machine import I2C, Pin
import uasyncio as asyncio
import time

# I2C configuration.
I2C_BUS = 0
SCL_PIN = 17  # Adjust based on your setup.
SDA_PIN = 16  # Adjust based on your setup.
MCP23017_ADDR = 0x27  # Default I2C address for MCP23017.

# MCP23017 register addresses.
IODIRA = 0x00  # I/O Direction Register for Port A.
GPIOA = 0x12   # GPIO Port A Register.
OLATA = 0x14   # Output Latch Register for Port A.

# Pins to test (PA0-PA3).
TEST_PINS = [0, 1, 2, 3]

# Frequency of the pulse (5 Hz).
PULSE_FREQUENCY = 5  # Hz
PULSE_PERIOD = 1 / PULSE_FREQUENCY  # Seconds.

def write_register(i2c, addr, reg, value):
    """
    Writes a value to a register on the MCP23017.

    Parameters:
    ----------
    i2c : I2C
        The I2C bus object.
    addr : int
        The I2C address of the MCP23017.
    reg : int
        The register address to write to.
    value : int
        The value to write to the register.
    """
    i2c.writeto_mem(addr, reg, bytes([value]))

def read_register(i2c, addr, reg):
    """
    Reads a value from a register on the MCP23017.

    Parameters:
    ----------
    i2c : I2C
        The I2C bus object.
    addr : int
        The I2C address of the MCP23017.
    reg : int
        The register address to read from.

    Returns:
    -------
    int
        The value of the register.
    """
    return i2c.readfrom_mem(addr, reg, 1)[0]

def reset_mcp23017(i2c, addr):
    """
    Resets the MCP23017 to its default state.
    """
    # Reset IODIRA and IODIRB to default (0xFF, all pins as inputs).
    write_register(i2c, addr, IODIRA, 0xFF)
    write_register(i2c, addr, 0x01, 0xFF)  # IODIRB register.

    # Reset GPIOA and GPIOB to default (0x00, all pins low).
    write_register(i2c, addr, GPIOA, 0x00)
    write_register(i2c, addr, 0x13, 0x00)  # GPIOB register.

async def pulse_pins(i2c, addr):
    """
    Pulses the specified pins high and low at 5 Hz.
    """
    while True:
        # Set all pins high.
        write_register(i2c, addr, GPIOA, 0x0F)  # Set PA0-PA3 high.
        print("Pins PA0-PA3 set HIGH")
        await asyncio.sleep(PULSE_PERIOD / 2)  # Wait for half the period.

        # Set all pins low.
        write_register(i2c, addr, GPIOA, 0x00)  # Set PA0-PA3 low.
        print("Pins PA0-PA3 set LOW")
        await asyncio.sleep(PULSE_PERIOD / 2)  # Wait for half the period.

def main():
    # Initialize I2C bus.
    i2c = I2C(I2C_BUS, scl=Pin(SCL_PIN), sda=Pin(SDA_PIN))

    # Scan I2C bus to confirm MCP23017 is detected.
    devices = i2c.scan()
    if MCP23017_ADDR not in devices:
        print(f"MCP23017 not found at address {hex(MCP23017_ADDR)}. Detected devices: {[hex(addr) for addr in devices]}")
        return

    print("MCP23017 detected.")

    # Reset the MCP23017 to its default state.
    reset_mcp23017(i2c, MCP23017_ADDR)
    print("MCP23017 reset to default state.")

    # Read the IODIRA register to confirm the device is an MCP23017.
    iodira_value = read_register(i2c, MCP23017_ADDR, IODIRA)
    print(f"IODIRA register value: {hex(iodira_value)}")

    # By default, all pins are inputs (0xFF).
    if iodira_value != 0xFF:
        print("Unexpected IODIRA value. Device may not be an MCP23017.")
        return

    print("Confirmed: Device is an MCP23017.")

    # Configure PA0-PA3 as outputs.
    write_register(i2c, MCP23017_ADDR, IODIRA, 0xF0)  # Set PA0-PA3 as outputs (0 = output, 1 = input).
    print("Configured PA0-PA3 as outputs.")

    # Run the pulse task.
    print("Starting pulse task...")
    asyncio.run(pulse_pins(i2c, MCP23017_ADDR))

if __name__ == "__main__":
    main()