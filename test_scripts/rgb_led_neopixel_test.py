from machine import Pin
from neopixel import NeoPixel
from time import sleep

# Define the number of NeoPixel segments and the GPIO pin
NUM_SEGMENTS = 8
PIN = 28

# Initialize the NeoPixel object
np = NeoPixel(Pin(PIN), NUM_SEGMENTS)

# Define some colors (R, G, B)
COLORS = [
    (255, 0, 0),    # Red
    (0, 255, 0),    # Green
    (0, 0, 255),    # Blue
    (255, 255, 0),  # Yellow
    (0, 255, 255),  # Cyan
    (255, 0, 255),  # Magenta
    (255, 165, 0),  # Orange
    (255, 255, 255) # White
]

def cycle_colors():
    for color in COLORS:
        for i in range(NUM_SEGMENTS):
            np[i] = color  # Set the current segment to the current color
            np.write()     # Update the NeoPixel strip
            sleep(0.5)     # Wait for half a second
            np[i] = (0, 0, 0)  # Turn off the current segment
            np.write()     # Update the NeoPixel strip

try:
    while True:
        cycle_colors()
except KeyboardInterrupt:
    # Turn off all LEDs when the script is interrupted
    for i in range(NUM_SEGMENTS):
        np[i] = (0, 0, 0)
    np.write()