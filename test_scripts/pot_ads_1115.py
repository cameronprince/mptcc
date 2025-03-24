from machine import I2C, Pin
import time

# ADS1115 Registers
ADS1115_ADDRESS = 0x48  # Default I2C address (decimal 72, hex 0x48)
ADS1115_CONVERSION = 0x00  # Conversion register
ADS1115_CONFIG = 0x01  # Config register

# Configuration settings
OS = 0x8000  # Operational status/single-shot conversion start
MUX_A0 = 0x4000  # Input multiplexer configuration (A0 vs GND)
MUX_A1 = 0x5000  # Input multiplexer configuration (A1 vs GND)
MUX_A2 = 0x6000  # Input multiplexer configuration (A2 vs GND)
MUX_A3 = 0x7000  # Input multiplexer configuration (A3 vs GND)
PGA = 0x0200  # Programmable gain amplifier (±4.096V)
MODE = 0x0100  # Device operating mode (single-shot)
DR = 0x0080  # Data rate (128 SPS)
COMP_MODE = 0x0000  # Comparator mode (traditional)
COMP_POL = 0x0000  # Comparator polarity (active low)
COMP_LAT = 0x0000  # Latching comparator (non-latching)
COMP_QUE = 0x0003  # Comparator queue (disable comparator)

# Initialize I2C
i2c = I2C(0, scl=Pin(17), sda=Pin(16), freq=100000)  # Reduced I2C clock speed

# Function to read a 16-bit value from a register
def read_register(reg):
    try:
        data = i2c.readfrom_mem(ADS1115_ADDRESS, reg, 2)
        value = (data[0] << 8) | data[1]
        print(f"Read from register {reg}: 0x{value:04X}")
        return value
    except OSError as e:
        print(f"Error reading from ADS1115: {e}")
        return 0

# Function to write a 16-bit value to a register
def write_register(reg, value):
    try:
        # Split the 16-bit value into two bytes
        upper_byte = (value >> 8) & 0xFF
        lower_byte = value & 0xFF
        data = bytearray([upper_byte, lower_byte])
        
        # Debugging: Print the data being written
        print(f"Writing to register {reg}: 0x{upper_byte:02X}{lower_byte:02X}")
        
        # Write the data to the register
        i2c.writeto_mem(ADS1115_ADDRESS, reg, data)
    except OSError as e:
        print(f"Error writing to ADS1115: {e}")

# Function to configure the ADS1115 for a specific channel
def configure_ads1115(channel):
    try:
        # Select the appropriate MUX setting based on the channel
        if channel == 0:
            mux = MUX_A0
        elif channel == 1:
            mux = MUX_A1
        elif channel == 2:
            mux = MUX_A2
        elif channel == 3:
            mux = MUX_A3
        else:
            raise ValueError("Invalid channel. Must be 0, 1, 2, or 3.")

        # Construct the configuration value for the selected channel
        config = OS | mux | PGA | MODE | DR | COMP_MODE | COMP_POL | COMP_LAT | COMP_QUE
        print(f"Configuring ADS1115 for channel {channel} with config value: 0x{config:04X}")
        write_register(ADS1115_CONFIG, config)

        # Read back the configuration register to verify (ignore the OS bit)
        read_config = read_register(ADS1115_CONFIG)
        expected_config = config & 0x7FFF  # Mask out the OS bit for comparison
        actual_config = read_config & 0x7FFF  # Mask out the OS bit for comparison
        print(f"Read back config: 0x{read_config:04X}")
        
        # Verify that the configuration was applied correctly (ignoring the OS bit)
        if actual_config != expected_config:
            print(f"ERROR: Configuration mismatch! Expected: 0x{expected_config:04X}, Actual: 0x{actual_config:04X}")
        else:
            print("Configuration verified successfully!")
    except Exception as e:
        print(f"Error configuring ADS1115: {e}")

# Function to read the analog value from a specific channel
def read_analog(channel):
    configure_ads1115(channel)  # Configure for the specified channel
    time.sleep(0.01)  # Wait for conversion to complete
    raw_value = read_register(ADS1115_CONVERSION)
    print(f"Raw value from channel {channel}: {raw_value}")
    return raw_value

# Main loop
def main():
    while True:
        # Read values from all four channels
        for channel in range(4):
            pot_value = read_analog(channel)
            print(f"Potentiometer (A{channel}) raw value: {pot_value}")
        
        # Wait a bit before reading again
        time.sleep(1)

# Run the main loop
main()