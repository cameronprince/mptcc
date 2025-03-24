from RGBLEDRingSmall import RGBLEDRingSmall
from machine import I2C, Pin
import time

# Constants and initialization code remain the same...

# Initialize I2C bus
i2c = I2C(1, scl=Pin(19), sda=Pin(18), freq=400000)

# Initialize LED ring
led_ring = RGBLEDRingSmall(i2c, 0x69)  # Adjust the address as needed

# Reset and configure LED ring
led_ring.reset()
time.sleep(0.02)
led_ring.configuration(0x01)  # Normal operation
led_ring.pwm_frequency_enable(1)
led_ring.spread_spectrum(0b0010110)
threshold_brightness = 0x10  # Set to low brightness (0x10 out of 0xFF) as the threshold
led_ring.global_current(0xFF)
led_ring.set_scaling_all(0xFF)
led_ring.pwm_mode()

# Define VU meter colors
vu_colors = [
    (0, 255, 0),   # Green
    (85, 255, 0),  # Yellow-green
    (170, 255, 0), # Yellow
    (255, 170, 0), # Yellow-orange
    (255, 85, 0),  # Orange
    (255, 0, 0)    # Red
]

# Define the number of LEDs
num_leds = 24  # Add this line to define num_leds

# Function to get color gradient
def get_color_gradient(color1, color2, steps):
    gradient = []
    for i in range(steps):
        ratio = i / float(steps)
        red = int(color1[0] * (1 - ratio) + color2[0] * ratio)
        green = int(color1[1] * (1 - ratio) + color2[1] * ratio)
        blue = int(color1[2] * (1 - ratio) + color2[2] * ratio)
        gradient.append((red, green, blue))
    return gradient

# Generate smooth color transitions
vu_meter_colors = []
for i in range(len(vu_colors) - 1):
    vu_meter_colors.extend(get_color_gradient(vu_colors[i], vu_colors[i + 1], num_leds // (len(vu_colors) - 1)))

# Ensure the list has exactly 24 colors
if len(vu_meter_colors) < num_leds:
    vu_meter_colors.extend([vu_colors[-1]] * (num_leds - len(vu_meter_colors)))

# Reverse the order of LEDs to go in the correct direction from green to red
vu_meter_colors.reverse()

# Shift starting LED by 180 degrees (13 LEDs) to make L13 the starting green LED
vu_meter_colors = vu_meter_colors[-13:] + vu_meter_colors[:-13]

# Print the colors for debugging
print("VU Meter Colors:", vu_meter_colors)

# Set all LEDs to the VU meter colors at the threshold brightness
for i in range(num_leds):
    color = vu_meter_colors[i]
    dimmed_color = (color[0] * threshold_brightness // 0xFF,
                    color[1] * threshold_brightness // 0xFF,
                    color[2] * threshold_brightness // 0xFF)
    led_ring.set_rgb(i, (dimmed_color[0] << 16) | (dimmed_color[1] << 8) | dimmed_color[2])

# Allow the initial display to show for a few seconds
time.sleep(3)

# Main loop to simulate pulsing brightness to the beat of rock music at 2Hz
while True:
    # Increase brightness of LEDs one by one from L13 to L12, L11, etc.
    for level in range(1, num_leds + 1):
        for brightness in range(threshold_brightness, 0xFF, 0x20):
            # Only update the current LED (level - 1)
            index = (12 - (level - 1)) % num_leds  # Start from L13 and move counterclockwise
            color = vu_meter_colors[index]
            brightened_color = (color[0] * brightness // 0xFF,
                               color[1] * brightness // 0xFF,
                               color[2] * brightness // 0xFF)
            led_ring.set_rgb(index, (brightened_color[0] << 16) | (brightened_color[1] << 8) | brightened_color[2])
            time.sleep(0.05)  # Adjust timing for smoother transition
    
    # Maintain at max brightness for a moment
    time.sleep(0.2)

    # Decrease brightness of LEDs one by one in reverse order from L12 to L13
    for level in range(num_leds, 0, -1):
        for brightness in range(0xFF, threshold_brightness, -0x20):
            # Only update the current LED (level - 1)
            index = (12 - (level - 1)) % num_leds  # Start from L13 and move counterclockwise
            color = vu_meter_colors[index]
            dimmed_color = (color[0] * brightness // 0xFF,
                            color[1] * brightness // 0xFF,
                            color[2] * brightness // 0xFF)
            led_ring.set_rgb(index, (dimmed_color[0] << 16) | (dimmed_color[1] << 8) | dimmed_color[2])
            time.sleep(0.05)  # Adjust timing for smoother transition
        
        # Dim the current LED back to threshold brightness
        index = (12 - (level - 1)) % num_leds
        color = vu_meter_colors[index]
        dimmed_color = (color[0] * threshold_brightness // 0xFF,
                        color[1] * threshold_brightness // 0xFF,
                        color[2] * threshold_brightness // 0xFF)
        led_ring.set_rgb(index, (dimmed_color[0] << 16) | (dimmed_color[1] << 8) | dimmed_color[2])

    # Ensure all LEDs are at threshold brightness before starting the next cycle
    for i in range(num_leds):
        color = vu_meter_colors[i]
        dimmed_color = (color[0] * threshold_brightness // 0xFF,
                        color[1] * threshold_brightness // 0xFF,
                        color[2] * threshold_brightness // 0xFF)
        led_ring.set_rgb(i, (dimmed_color[0] << 16) | (dimmed_color[1] << 8) | dimmed_color[2])