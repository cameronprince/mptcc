from machine import Pin, PWM
import time

# Choose a GPIO pin for the PWM output
pwm_pin = Pin(22)

# Create a PWM object
pwm1 = PWM(Pin(22))
pwm2 = PWM(Pin(6))
pwm3 = PWM(Pin(7))
pwm4 = PWM(Pin(8))

# Set the frequency to 100Hz
pwm1.freq(100)
pwm2.freq(100)
pwm3.freq(100)
pwm4.freq(100)

# Calculate the duty cycle for 20 microsecond on time
# PWM duty cycle is 0 to 65535, so we need to convert the pulse width accordingly
# Duty cycle percentage = (pulse width / period) * 100
# Period for 100Hz = 1 / 100 = 0.01 seconds (10,000 microseconds)
# Duty cycle percentage = (20 / 10,000) * 100 = 0.2%
# Duty cycle in terms of 0 to 65535 = (0.2 / 100) * 65535 = 131

# Set the duty cycle to achieve 20 microsecond on time
pwm1.duty_u16(131)
pwm2.duty_u16(131)
pwm3.duty_u16(131)
pwm4.duty_u16(131)

# Keep the PWM running
while True:
    time.sleep(1)
