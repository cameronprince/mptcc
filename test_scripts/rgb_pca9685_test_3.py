from machine import Pin, I2C
import time

# PCA9685 I2C address
PCA9685_ADDR = 0x40

# PCA9685 registers
MODE1 = 0x00
MODE2 = 0x01
PRE_SCALE = 0xFE
LED0_ON_L = 0x06
LED0_ON_H = 0x07
LED0_OFF_L = 0x08
LED0_OFF_H = 0x09

# Initialize I2C bus
i2c = I2C(1, scl=Pin(19), sda=Pin(18), freq=400000)

# Function to write a byte to a register
def write_register(register, value):
    i2c.writeto_mem(PCA9685_ADDR, register, bytes([value]))

# Function to read a byte from a register
def read_register(register):
    return i2c.readfrom_mem(PCA9685_ADDR, register, 1)[0]

# Function to set PWM frequency
def set_pwm_frequency(frequency):
    prescale = int(25000000 / (4096 * frequency)) - 1
    old_mode = read_register(MODE1)
    write_register(MODE1, (old_mode & 0x7F) | 0x10)  # Sleep mode
    write_register(PRE_SCALE, prescale)  # Set prescaler
    write_register(MODE1, old_mode)  # Restore mode
    time.sleep(0.005)
    write_register(MODE1, old_mode | 0x80)  # Restart

# Function to set PWM duty cycle for a channel
def set_pwm(channel, on_time, off_time):
    write_register(LED0_ON_L + 4 * channel, on_time & 0xFF)
    write_register(LED0_ON_H + 4 * channel, on_time >> 8)
    write_register(LED0_OFF_L + 4 * channel, off_time & 0xFF)
    write_register(LED0_OFF_H + 4 * channel, off_time >> 8)

# Initialize PCA9685
def init_pca9685():
    write_register(MODE1, 0x00)  # Reset MODE1
    write_register(MODE2, 0x04)  # Set MODE2 (output logic, etc.)
    set_pwm_frequency(1000)  # Set PWM frequency to 1kHz

# Main program
try:
    print("Initializing PCA9685...")
    init_pca9685()

    print("Turning on LED on channel 0...")
    set_pwm(0, 0, 2048)  # 50% duty cycle (2048/4096)

    # Keep the LED on for 5 seconds
    time.sleep(5)

    print("Turning off LED on channel 0...")
    set_pwm(0, 0, 0)  # Turn off LED

except KeyboardInterrupt:
    print("Script interrupted. Turning off LED.")
    set_pwm(0, 0, 0)  # Ensure LED is off

finally:
    print("Script ended.")