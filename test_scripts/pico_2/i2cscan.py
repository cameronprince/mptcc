from machine import Pin, I2C

# Initialize I2C
i2c = I2C(1, scl=Pin(19), sda=Pin(18), freq=400000)

# Scan for devices
devices = i2c.scan()

if devices:
    print("I2C devices found:", devices)
else:
    print("No I2C devices found")
