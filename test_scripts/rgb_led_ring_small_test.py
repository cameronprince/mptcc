from machine import I2C, Pin
from led_ring_small import LEDRingSmall
import time

# Initialize I2C bus
i2c = I2C(0, scl=Pin(22), sda=Pin(21), freq=400000)

# Initialize LED ring
led_ring = LEDRingSmall(i2c, 0x74)  # Change the address as needed

# Reset and configure LED ring
led_ring.reset()
time.sleep(0.02)
led_ring.configuration(0x01)  # Normal operation
led_ring.pwm_frequency_enable(1)
led_ring.spread_spectrum(0b0010110)
led_ring.global_current(0x10)
led_ring.set_scaling_all(0xFF)
led_ring.pwm_mode()

# Define color tables
fade1_table = [0x8011EE, 0xA004DA, 0xBF00BF, 0xDA04A0, 0xEE1180, 0xFB255F, 0xFF4040, 0xFB5F25, 0xEE8011, 0xDAA004, 0xBFBF00, 0xA0DA04, 0x80EE11, 0x5FFB25, 0x40FF40, 0x25FB5F, 0x11EE80, 0x04DAA0, 0x00BFBF, 0x04A0DA, 0x1180EE, 0x255FFB, 0x4040FF, 0x5F25FB]
fade2_table = [0xFF0000, 0xFF0004, 0xFF0020, 0xFF006B, 0xFF00FF, 0x6B00FF, 0x2000FF, 0x0400FF, 0x0000FF, 0x0004FF, 0x0020FF, 0x006BFF, 0x00FFFF, 0x00FF6B, 0x00FF20, 0x00FF04, 0x00FF00, 0x04FF00, 0x20FF00, 0x6BFF00, 0xFFFF00, 0xFF6B00, 0xFF2000, 0xFF0400]

# Helper functions
def set_red(led_ring, index, intensity):
    led_ring.set_red(index, intensity)

def set_green(led_ring, index, intensity):
    led_ring.set_green(index, intensity)

def set_blue(led_ring, index, intensity):
    led_ring.set_blue(index, intensity)

# Main loop
while True:
    # Cycle through red, green, and blue colors
    for i in range(24):
        set_red(led_ring, i, 0xFF)
        time.sleep(0.03)
    for i in range(24):
        set_red(led_ring, i, 0)
        set_green(led_ring, i, 0xFF)
        time.sleep(0.03)
    for i in range(24):
        set_green(led_ring, i, 0)
        set_blue(led_ring, i, 0xFF)
        time.sleep(0.03)
    for i in range(24):
        led_ring.set_rgb(i, 0xfc6b03)
        time.sleep(0.03)
    for i in range(24):
        led_ring.set_rgb(i, 0xfc03c6)
        time.sleep(0.03)

    # Additional effects
    r, g, b, rg, br, bg = 5, 8, 20, 40, 35, 17
    for tim in range(2000):
        if tim % 5 == 0:
            set_red(led_ring, r, 0)
            r = (r + 1) % 24
            set_red(led_ring, r, 0xFF)
        if tim % 6 == 0:
            set_green(led_ring, g, 0)
            g = (g + 1) % 24
            set_green(led_ring, g, 0xFF)
        if tim % 8 == 0:
            set_blue(led_ring, b, 0)
            b = (b + 1) % 24
            set_blue(led_ring, b, 0xFF)
        if tim % 7 == 0:
            set_blue(led_ring, br, 0)
            set_red(led_ring, br, 0)
            br = (br + 1) % 24
            set_blue(led_ring, br, 0xFF)
            set_red(led_ring, br, 0xFF)
        if tim % 10 == 0:
            set_blue(led_ring, bg, 0)
            set_green(led_ring, bg, 0)
            bg = (bg + 1) % 24
            set_blue(led_ring, bg, 0xFF)
            set_green(led_ring, bg, 0xFF)
        if tim % 11 == 0:
            set_red(led_ring, rg, 0)
            set_green(led_ring, rg, 0)
            rg = (rg + 1) % 24
            set_red(led_ring, rg, 0xFF)
            set_green(led_ring, rg, 0xFF)
        time.sleep(0.01)

    # Fade effects
    for tim in range(100):
        j = tim % 24
        for i in range(24):
            led_ring.set_rgb(i, fade1_table[j])
            j = (j + 1) % 24
        time.sleep(0.04)
    for tim in range(100):
        j = tim % 24
        for i in range(24):
            led_ring.set_rgb(i, fade2_table[j])
            j = (j + 1) % 24
        time.sleep(0.04)

    # Global current effect
    for i in range(0xFF, 0, -1):
        led_ring.global_current(i)
        time.sleep(0.02)
    led_ring.clear_all()
    led_ring.global_current(0xFF)