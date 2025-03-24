from machine import Pin
import time

# GPIO pins for switches
SWITCH_PINS = [9, 8, 7, 6, 1, 0]  # Replace with your actual GPIO pins
PULL_UP = True  # Set to False if using pull-down resistors
DEBOUNCE_DELAY = 0  # Debounce delay in milliseconds

# Track the state of each switch
switch_states = [1] * len(SWITCH_PINS)  # 1 = released, 0 = pressed
last_switch_click_time = [0] * len(SWITCH_PINS)  # Track last click time for debouncing

# Initialize GPIO pins for switches
switch_pins = []
for i, pin in enumerate(SWITCH_PINS):
    switch_pin = Pin(pin, Pin.IN, Pin.PULL_UP if PULL_UP else Pin.PULL_DOWN)
    switch_pin.irq(handler=lambda p, idx=i: handle_interrupt(p, idx), trigger=Pin.IRQ_FALLING | Pin.IRQ_RISING)
    switch_pins.append(switch_pin)

# Interrupt handler
def handle_interrupt(pin, idx):
    current_time = time.ticks_ms()
    if time.ticks_diff(current_time, last_switch_click_time[idx]) > DEBOUNCE_DELAY:
        last_switch_click_time[idx] = current_time
        current_state = pin.value()  # Read the state of the switch (0 = pressed, 1 = released)
        if current_state != switch_states[idx]:  # State changed
            switch_states[idx] = current_state
            if current_state == 0:  # Switch pressed
                print(f"Switch {idx + 1} pressed")
            else:  # Switch released
                print(f"Switch {idx + 1} released")

# Main loop
def main():
    print("GPIO switch interrupt test started. Press switches to trigger interrupts.")
    while True:
        time.sleep(1)  # Keep the program running

# Run the main loop
main()