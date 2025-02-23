from machine import Pin, I2C
from pca9685 import PCA9685
import time

# Initialize the I2C bus
i2c = I2C(0, scl=Pin(17), sda=Pin(16), freq=400000)

# Initialize PCA9685
pca = PCA9685(i2c, address=0x50)

# Set PWM frequency to 200Hz
pca.freq(200)

# Run PWM continuously on channel 0
while True:
    pca.duty(0, 2048)  # Set channel 0 to 50% duty cycle
    time.sleep(1)