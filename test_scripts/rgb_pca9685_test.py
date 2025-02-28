from machine import I2C, Pin
from pca9685 import PCA9685
from picoRGB import RGBLed
import utime

# Setup I2C and PCA9685
# i2c = I2C(0, scl=Pin(17), sda=Pin(16))
i2c = I2C(1, scl=Pin(19), sda=Pin(18), freq=400000)
# The PCA default is at 0x40
pca = PCA9685(i2c, address=0x40)
pca.freq(1000)

# Initialize 5 RGB LEDs
leds = [
    RGBLed(pca, red_channel=0, green_channel=1, blue_channel=2),
    RGBLed(pca, red_channel=3, green_channel=4, blue_channel=5),
    RGBLed(pca, red_channel=6, green_channel=7, blue_channel=8),
    RGBLed(pca, red_channel=9, green_channel=10, blue_channel=11),
    RGBLed(pca, red_channel=12, green_channel=13, blue_channel=14),
]

# Testing the new status_color method with multiple LEDs
try:
    while True:
        # Transition from 1 to 100 over 5 seconds
        for value in range(1, 101):
            for led in leds:
                led.status_color(value)
            utime.sleep(0.05)
        
        # Solid red for 1 second
        utime.sleep(1)

        # Turn off LEDs for 1 second
        for led in leds:
            led.off()
        utime.sleep(1)
        
except KeyboardInterrupt:
    for led in leds:
        led.off()
    print("LEDs turned off and script stopped.")
