from machine import I2C, Pin
import time

# I2C Configuration
i2c = I2C(1, scl=Pin(19), sda=Pin(18), freq=400000)

# RGB LED Ring Address
LED_RING_ADDRESS = 0x69  # Adjust this address as needed

# IS31FL3746A Register Definitions
IS31FL3746A_PAGE0 = 0x00  # PWM registers
IS31FL3746A_PAGE1 = 0x01  # Configuration registers
IS31FL3746A_COMMANDREGISTER = 0xFD
IS31FL3746A_COMMANDREGISTER_LOCK = 0xFE
IS31FL3746A_ULOCK_CODE = 0xC5
IS31FL3746A_CONFIGURATION = 0x50
IS31FL3746A_GLOBALCURRENT = 0x51
IS31FL3746A_PULLUPDOWM = 0x52
IS31FL3746A_OPENSHORT = 0x53
IS31FL3746A_TEMPERATURE = 0x5F
IS31FL3746A_SPREADSPECTRUM = 0x60
IS31FL3746A_RESET_REG = 0x8F
IS31FL3746A_PWM_FREQUENCY_ENABLE = 0xE0
IS31FL3746A_PWM_FREQUENCY_SET = 0xE2

# Simplified Logical to Physical Index Mapping (only physical index and on/off state)
logical_to_physical_index = [
    [23, True],   # L1 (Physical Index, On/Off)
    [17, False],  # L2 (Physical Index, On/Off)
    [11, True],   # L3 (Physical Index, On/Off)
    [5, False],   # L4 (Physical Index, On/Off)
    [22, True],   # L5 (Physical Index, On/Off)
    [16, False],  # L6 (Physical Index, On/Off)
    [10, True],   # L7 (Physical Index, On/Off)
    [4, False],   # L8 (Physical Index, On/Off)
    [21, True],   # L9 (Physical Index, On/Off)
    [15, False],  # L10 (Physical Index, On/Off)
    [9, True],    # L11 (Physical Index, On/Off)
    [3, False],   # L12 (Physical Index, On/Off)
    [20, True],   # L13 (Physical Index, On/Off)
    [14, False],  # L14 (Physical Index, On/Off)
    [8, True],    # L15 (Physical Index, On/Off)
    [2, False],   # L16 (Physical Index, On/Off)
    [19, True],   # L17 (Physical Index, On/Off)
    [13, False],  # L18 (Physical Index, On/Off)
    [7, True],    # L19 (Physical Index, On/Off)
    [1, False],   # L20 (Physical Index, On/Off)
    [18, True],   # L21 (Physical Index, On/Off)
    [12, False],  # L22 (Physical Index, On/Off)
    [6, True],    # L23 (Physical Index, On/Off)
    [0, False],   # L24 (Physical Index, On/Off)
]

# Helper Functions
def write_register8(i2c, address, reg, data):
    """Write an 8-bit value to a register."""
    print(f"Writing to register {reg:#04x} data {data:#04x}")
    i2c.writeto_mem(address, reg, bytearray([data]))

def select_page(i2c, address, page):
    """Select the page for the IS31FL3746A LED controller."""
    write_register8(i2c, address, IS31FL3746A_COMMANDREGISTER_LOCK, IS31FL3746A_ULOCK_CODE)
    write_register8(i2c, address, IS31FL3746A_COMMANDREGISTER, page)
    time.sleep(0.01)  # Add a small delay after switching pages

def hex_to_rgb(hex_color):
    """Convert hex color code to RGB values."""
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

def set_leds(i2c, address, color):
    """
    Set the LEDs based on the mapping array.
    """
    # Convert the hex color code to RGB values
    r_val, g_val, b_val = hex_to_rgb(color)

    # Switch to Page 0 (PWM registers)
    select_page(i2c, address, IS31FL3746A_PAGE0)

    # Prepare the buffer for batched write
    buffer = bytearray(72)  # 24 LEDs * 3 channels

    for physical_index, is_on in logical_to_physical_index:
        if is_on:
            # Set the LED color based on the RGB values
            buffer[3 * physical_index + 0] = b_val  # Blue channel
            buffer[3 * physical_index + 1] = g_val  # Green channel
            buffer[3 * physical_index + 2] = r_val  # Red channel
        else:
            # Turn off the LED
            buffer[3 * physical_index + 0] = 0x00
            buffer[3 * physical_index + 1] = 0x00
            buffer[3 * physical_index + 2] = 0x00

    print(f"Buffer to write: {buffer.hex()}")
    # Perform the batched write
    i2c.writeto_mem(address, 0x01, buffer)

def initialize_led_ring(i2c, address):
    """Initialize the LED ring with default settings."""
    # Unlock the command register
    write_register8(i2c, address, IS31FL3746A_COMMANDREGISTER_LOCK, IS31FL3746A_ULOCK_CODE)

    # Reset the LED ring
    select_page(i2c, address, IS31FL3746A_PAGE1)
    write_register8(i2c, address, IS31FL3746A_RESET_REG, 0xAE)
    time.sleep(0.02)

    # Configure the LED ring
    write_register8(i2c, address, IS31FL3746A_CONFIGURATION, 0x01)  # Normal operation
    write_register8(i2c, address, IS31FL3746A_PWM_FREQUENCY_ENABLE, 1)
    write_register8(i2c, address, IS31FL3746A_SPREADSPECTRUM, 0b0010110)
    write_register8(i2c, address, IS31FL3746A_GLOBALCURRENT, 0xFF)  # Max global current

    # Set scaling for all LEDs (0xFF = max brightness)
    for i in range(1, 73):
        write_register8(i2c, address, i, 0xFF)

    # Switch to PWM mode
    select_page(i2c, address, IS31FL3746A_PAGE0)

# Main Script to Set LEDs to a Specified Color
def main():
    # Initialize the LED ring
    initialize_led_ring(i2c, LED_RING_ADDRESS)

    # Set the LEDs to the specified color (e.g., #00ff00 for green)
    set_leds(i2c, LED_RING_ADDRESS, '#326400')
    print("LEDs have been set to the specified color. All other LEDs are off.")

# Run the script
if __name__ == "__main__":
    main()