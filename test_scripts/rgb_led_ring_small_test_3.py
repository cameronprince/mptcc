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

# Helper Functions
def write_register8(i2c, address, reg, data):
    """Write an 8-bit value to a register."""
    i2c.writeto_mem(address, reg, bytearray([data]))

def select_page(i2c, address, page):
    """Select the page for the IS31FL3746A LED controller."""
    write_register8(i2c, address, IS31FL3746A_COMMANDREGISTER_LOCK, IS31FL3746A_ULOCK_CODE)
    write_register8(i2c, address, IS31FL3746A_COMMANDREGISTER, page)
    time.sleep(0.01)  # Add a small delay after switching pages

def set_all_leds_batched(i2c, address, colors):
    """
    Set all LEDs to the specified colors using batched writes.
    """
    if len(colors) != 24:
        raise ValueError("Exactly 24 colors must be provided.")

    # Switch to Page 0 (PWM registers)
    select_page(i2c, address, IS31FL3746A_PAGE0)

    # Prepare the buffer for batched write
    buffer = bytearray()
    for led_n in range(24):
        color = colors[led_n]
        red_val = (color >> 16) & 0xFF  # Extract red component
        green_val = (color >> 8) & 0xFF  # Extract green component
        blue_val = color & 0xFF  # Extract blue component

        # Append values for red, green, and blue channels
        buffer.append(red_val)  # Red value
        buffer.append(green_val)  # Green value
        buffer.append(blue_val)  # Blue value

    # Perform the batched write
    # Start from the first PWM register (0x01) and write all 72 bytes (24 LEDs * 3 channels)
    i2c.writeto_mem(address, 0x01, buffer)

# Initialize the RGB LED Ring
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

# Main Script
def main():
    # Initialize the LED ring
    initialize_led_ring(i2c, LED_RING_ADDRESS)

    # Set all LEDs to green
    colors = [0x00FF00] * 24  # Set all LEDs to green (0x00FF00 = green)
    set_all_leds_batched(i2c, LED_RING_ADDRESS, colors)
    print("All LEDs should now be lit in green.")

# Run the script
if __name__ == "__main__":
    main()