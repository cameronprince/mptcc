from machine import Pin, freq
from neopixel import NeoPixel
from time import sleep
import network

# Disable Wi-Fi to reduce interference
wlan = network.WLAN(network.STA_IF)
wlan.active(False)

# Set consistent clock speed
freq(125000000)

NUM_SEGMENTS = 4
PIN = 28

# Initialize with explicit output pin
pin = Pin(PIN, Pin.OUT)
np = NeoPixel(pin, NUM_SEGMENTS)

COLORS = [
    (255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0),
    (0, 255, 255), (255, 0, 255), (255, 165, 0), (255, 255, 255)
]

# Clear the strip first
for i in range(NUM_SEGMENTS):
    np[i] = (0, 0, 0)
np.write()

# Test with a single color first
np[0] = (255, 0, 0)  # Red on first LED
np.write()
sleep(2)

# Then cycle colors
for color in COLORS:
    for i in range(NUM_SEGMENTS):
        np[i] = color
        np.write()
        sleep(0.5)
        np[i] = (0, 0, 0)
        np.write()