from machine import Pin
from rp2 import PIO, StateMachine, asm_pio
from time import sleep

# PIO program definition
@asm_pio(sideset_init=PIO.OUT_LOW)
def pwm_prog():
    pull(noblock) .side(0)  # Pull data into OSR, set pin low
    mov(x, osr)             # Move OSR to X (duty cycle)
    mov(y, isr)             # Move ISR to Y (max count)
    label("pwmloop")
    jmp(x_not_y, "skip")    # If X != Y, skip the high pulse
    nop() .side(1)          # Set pin high
    label("skip")
    jmp(y_dec, "pwmloop")   # Decrement Y and loop

# Configuration
output_pin = 21  # GPIO pin 13
fixed_sm_freq = 10_000_000  # Updated state machine frequency (10 MHz)
desired_freq = 100  # Desired PWM frequency in Hz
desired_high_time_us = 20  # Desired high time in microseconds (20 µs)

# Calculate the maximum count for the PWM signal
max_count = fixed_sm_freq // (desired_freq * 2) # max_count = 10,000,000 / 100 = 100,000

# Calculate the duty cycle for the desired high time
duty_cycle = int((desired_high_time_us / 2_000_000) * fixed_sm_freq)  # Convert on_time (µs) to clock cycles

# Ensure the duty cycle does not exceed the maximum count
if duty_cycle > max_count:
    duty_cycle = max_count

# Print debug information
print(f"Max Count: {max_count}")
print(f"Duty Cycle: {duty_cycle}")

# Initialize the state machine with the fixed frequency
sm = StateMachine(0, pwm_prog, freq=fixed_sm_freq, sideset_base=Pin(output_pin))

# Load the maximum count into the ISR
sm.put(max_count)
sm.exec("pull()")
sm.exec("mov(isr, osr)")

# Load the duty cycle into the TX FIFO
sm.put(duty_cycle)

# Start the state machine
sm.active(1)

# Let the program run indefinitely with the fixed duty cycle
while True:
    sleep(1)  # Keep the program running