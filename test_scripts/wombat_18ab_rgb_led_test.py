"""
This example shows how to drive an RGB LED using PWM outputs on a Serial Wombat 18AB chip.

IMPORTANT: This example requires firmware version 2.1.1 or later to work.

This example assumes an RGB LED is connected to pins 10, 11, and 12 of the Serial Wombat 18AB chip.
The script cycles through different colors by varying the duty cycle of the PWM signals on these pins.

Documentation for the SerialWombatPWM_18AB Arduino class is available at:
https://broadwellconsultinginc.github.io/SerialWombatArdLib/class_serial_wombat_p_w_m__18_a_b.html
"""

import SerialWombat
from ArduinoFunctions import delay

# Comment these lines in if you're connecting directly to a Serial Wombat Chip's UART through cPython serial Module
# Change the parameter of SerialWombatChip_cpy_serial to match the name of your Serial port
# import SerialWombat_cpy_serial
# sw = SerialWombat_cpy_serial.SerialWombatChip_cpy_serial("COM3")

# Comment these lines in if you're connecting to a Serial Wombat Chip's I2C port using MicroPython's I2C interface
# Change the values for sclPin, sdaPin, and swI2Caddress to match your configuration
import machine
import SerialWombat_mp_i2c

swI2Caddress = 0x6B
i2c = machine.I2C(1, scl=machine.Pin(19), sda=machine.Pin(18), freq=400000, timeout=50000)
sw = SerialWombat_mp_i2c.SerialWombatChip_mp_i2c(i2c, swI2Caddress)
sw.address = 0x6B

# Comment these lines in if you're connecting to a Serial Wombat Chip's UART port using MicroPython's UART interface
# Change the values for UARTnum, txPin, and rxPin to match your configuration
# import machine
# import SerialWombat_mp_UART
# txPin = 12
# rxPin = 14
# UARTnum = 2
# uart = machine.UART(UARTnum, baudrate=115200, tx=txPin, rx=rxPin)
# sw = SerialWombat_mp_UART.SerialWombatChipUART(uart)

# Interface independent code starts here:
import SerialWombatPWM

# Define the pins for the RGB LED
RED_PIN = 10
GREEN_PIN = 11
BLUE_PIN = 12

# Initialize PWM outputs for the RGB LED
red_pwm = SerialWombatPWM.SerialWombatPWM_18AB(sw)
green_pwm = SerialWombatPWM.SerialWombatPWM_18AB(sw)
blue_pwm = SerialWombatPWM.SerialWombatPWM_18AB(sw)

# Frequency for the PWM signals (1 kHz is a common choice for LEDs)
frequency = 1000  # 1 kHz

# List of colors to cycle through (R, G, B values as duty cycles, 0x0000 to 0xFFFF)
colors = [
    (0xFFFF, 0x0000, 0x0000),  # Red
    (0x0000, 0xFFFF, 0x0000),  # Green
    (0x0000, 0x0000, 0xFFFF),  # Blue
    (0xFFFF, 0xFFFF, 0x0000),  # Yellow
    (0xFFFF, 0x0000, 0xFFFF),  # Magenta
    (0x0000, 0xFFFF, 0xFFFF),  # Cyan
    (0xFFFF, 0xFFFF, 0xFFFF),  # White
]

# Current color index
color_index = 0


def setup():
    """
    Initialize the Serial Wombat chip and PWM outputs.
    """
    sw.begin()

    # Initialize PWM outputs with the specified frequency and 0% duty cycle (off)
    red_pwm.begin(RED_PIN, 0)
    green_pwm.begin(GREEN_PIN, 0)
    blue_pwm.begin(BLUE_PIN, 0)

    # Set the frequency for all PWM outputs
    red_pwm.writeFrequency_Hz(frequency)
    green_pwm.writeFrequency_Hz(frequency)
    blue_pwm.writeFrequency_Hz(frequency)


def loop():
    """
    Cycle through the colors and update the RGB LED.
    """
    global color_index

    # Get the current color
    red_duty, green_duty, blue_duty = colors[color_index]

    # Set the duty cycle for each PWM output
    red_pwm.writeDutyCycle(red_duty)
    green_pwm.writeDutyCycle(green_duty)
    blue_pwm.writeDutyCycle(blue_duty)

    # Move to the next color
    color_index = (color_index + 1) % len(colors)

    # Wait for 1 second before changing the color
    delay(1000)


# Run the setup and loop
setup()
while True:
    loop()