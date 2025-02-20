from machine import I2C, Pin
import time

# I2C setup (adjust pins based on your hardware)
i2c = I2C(0, scl=Pin(17), sda=Pin(16), freq=100000)  # Lower frequency

# Register for changing the I2C address
I2CADDRESS_REG = 0x72  # Correct register for setting I2C address

# Register for ID code
IDCODE_REG = 0x70  # Correct register for reading ID code

# Expected ID code
ID_CODE = 0x39

def reset_device(address):
    """
    Send a reset command to the device.
    """
    try:
        i2c.writeto(address, b'\xFF')  # Reset command
        print(f"Reset command sent to {hex(address)}")
    except OSError as e:
        print(f"Reset command failed: {e}")

def change_address(current_address, new_address):
    """
    Change the I2C address of the I2C Encoder Mini.
    The address must be written 3 times consecutively to the I2CADDRESS register.
    """
    for _ in range(3):
        try:
            i2c.writeto_mem(current_address, I2CADDRESS_REG, bytes([new_address]))
            print(f"Write to {hex(current_address)} successful")
        except OSError as e:
            print(f"Write to {hex(current_address)} failed: {e}")
        time.sleep(0.1)  # Small delay between writes

    # Reset the device to apply the new address
    reset_device(current_address)
    time.sleep(0.1)

    # Verify the new address
    try:
        id_code = i2c.readfrom_mem(new_address, IDCODE_REG, 1)[0]  # Read ID code register
        if id_code == ID_CODE:
            print(f"Address changed from {hex(current_address)} to {hex(new_address)}")
        else:
            print(f"Error: Device at {hex(new_address)} returned ID code {hex(id_code)} (expected {hex(ID_CODE)})")
    except OSError as e:
        print(f"Error: Device not found at {hex(new_address)}: {e}")

def read_register(address, reg, length=1):
    """
    Read a register from the device.
    """
    try:
        data = i2c.readfrom_mem(address, reg, length)
        print(f"Read from {hex(address)}, register {hex(reg)}: {data}")
        return data
    except OSError as e:
        print(f"Failed to read from {hex(address)}, register {hex(reg)}: {e}")
        return None

def search_i2c_devices():
    """
    Scan the I2C bus for devices and identify I2C Encoder Minis.
    """
    print("Scanning I2C bus...")
    devices = i2c.scan()
    if not devices:
        print("No devices found.")
        return

    for addr in devices:
        try:
            reset_device(addr)  # Send reset command
            time.sleep(0.1)  # Small delay after reset
            id_code = i2c.readfrom_mem(addr, IDCODE_REG, 1)[0]  # Read ID code register
            if id_code == ID_CODE:
                print(f"I2C Encoder Mini found at {hex(addr)}")
            else:
                print(f"Device found at {hex(addr)} (ID code: {hex(id_code)}, not an I2C Encoder Mini)")
        except OSError as e:
            print(f"Device found at {hex(addr)} (communication error: {e})")

def parse_address(input_str):
    """
    Parse an address from a string (hex or decimal).
    """
    try:
        if input_str.startswith("0x"):
            return int(input_str, 16)
        else:
            return int(input_str)
    except ValueError:
        return None

def main():
    print("\n**** I2C Encoder Address Changer ****")
    print("Available commands:")
    print("  S: Scan for I2C Encoder Minis")
    print("  0xXX or XXX: Address of the target device in hex or decimal")
    print("  R: Read a register from the device")
    print("  X: Force address change without verification\n")

    while True:
        command = input("Enter command: ").strip().upper()

        if command == "S":
            search_i2c_devices()
        elif command == "R":
            address_str = input("Enter the device address (hex or decimal): ").strip()
            address = parse_address(address_str)
            if address is None or address < 0 or address > 0x7F:
                print("Invalid address. Use decimal or hex (e.g., 32 or 0x20).")
                continue

            reg_str = input("Enter the register to read (hex or decimal): ").strip()
            reg = parse_address(reg_str)
            if reg is None or reg < 0 or reg > 0xFF:
                print("Invalid register. Use decimal or hex (e.g., 0x00 or 0).")
                continue

            read_register(address, reg)
        elif command == "X":
            current_address_str = input("Enter the current address (hex or decimal): ").strip()
            current_address = parse_address(current_address_str)
            if current_address is None or current_address < 0 or current_address > 0x7F:
                print("Invalid address. Use decimal or hex (e.g., 32 or 0x20).")
                continue

            new_address_str = input("Enter the new address (hex or decimal): ").strip()
            new_address = parse_address(new_address_str)
            if new_address is None or new_address < 0 or new_address > 0x7F:
                print("Invalid address. Use decimal or hex (e.g., 24 or 0x18).")
                continue

            # Force the address change without verification
            change_address(current_address, new_address)
        else:
            current_address = parse_address(command)
            if current_address is None or current_address < 0 or current_address > 0x7F:
                print("Invalid address. Use decimal or hex (e.g., 32 or 0x20).")
                continue

            # Verify the device is an I2C Encoder Mini
            try:
                reset_device(current_address)  # Send reset command
                time.sleep(0.1)  # Small delay after reset
                id_code = i2c.readfrom_mem(current_address, IDCODE_REG, 1)[0]
                if id_code != ID_CODE:
                    print(f"No I2C Encoder Mini found at {hex(current_address)} (ID code: {hex(id_code)})")
                    continue
            except OSError as e:
                print(f"No device found at {hex(current_address)}: {e}")
                continue

            # Get the new address
            new_address_str = input("Enter the new address (hex or decimal): ").strip()
            new_address = parse_address(new_address_str)
            if new_address is None or new_address < 0 or new_address > 0x7F:
                print("Invalid address. Use decimal or hex (e.g., 24 or 0x18).")
                continue

            # Change the address
            change_address(current_address, new_address)

if __name__ == "__main__":
    main()