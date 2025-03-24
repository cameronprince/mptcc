from machine import I2C, Pin
from pca9685 import PCA9685
import utime

# Setup I2C and PCA9685
i2c = I2C(0, scl=Pin(17), sda=Pin(16))  # Use I2C bus 0
pca = PCA9685(i2c, address=0x40)         # PCA9685 address is 0x40
pca.freq(1000)                           # Set PWM frequency to 1000 Hz

# Turn on channel 0 (full brightness)
pca.duty(15, 4095)  # Set duty cycle to 4095 (100%)

# Keep the script running
try:
    while True:
        utime.sleep(1)  # Do nothing, just keep channel 0 on

except KeyboardInterrupt:
    # Turn off channel 0 and exit gracefully
    pca.duty(0, 0)  # Set duty cycle to 0 (off)
    print("Channel 0 turned off and script stopped.")