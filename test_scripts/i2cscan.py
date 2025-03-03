from machine import Pin, I2C

# Initialize I2C
# i2c = I2C(1, scl=Pin(19), sda=Pin(18), freq=400000)
# i2c = I2C(0, scl=Pin(17), sda=Pin(16), freq=400000)
# i2c = I2C(0, scl=Pin(13), sda=Pin(12), freq=400000)
i2c = I2C(1, scl=Pin(11), sda=Pin(10), freq=400000)

# Scan for devices
devices = i2c.scan()

if devices:
    print("I2C devices found:")
    for device in devices:
        print(f"  Decimal: {device}, Hex: {hex(device)}")
else:
    print("No I2C devices found")