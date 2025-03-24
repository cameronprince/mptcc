from machine import I2C, Pin
import time

# Initialize I2C
i2c = I2C(1, scl=Pin(15), sda=Pin(14), freq=400000)

# PCF8574 I2C address
PCF8574_ADDRESS = 0x27

# Mask for each pin (0-7)
PIN_MASKS = [0x01, 0x02, 0x04, 0x08, 0x10, 0x20, 0x40, 0x80]  # Binary: 00000001, 00000010, etc.

# Function to toggle a specific pin
def toggle_pin(pin_mask):
    # Read the current state of all pins
    current_state = i2c.readfrom(PCF8574_ADDRESS, 1)[0]
    
    # Toggle the specified pin (XOR with pin_mask)
    new_state = current_state ^ pin_mask
    
    # Write the new state back to the PCF8574
    i2c.writeto(PCF8574_ADDRESS, bytes([new_state]))

# Main loop to cycle through all relays
while True:
    for pin_mask in PIN_MASKS:
        print(f"Toggling relay {PIN_MASKS.index(pin_mask)}")
        toggle_pin(pin_mask)  # Toggle the relay
        time.sleep(1)  # Wait for 1 second