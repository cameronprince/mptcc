from machine import Pin
from rotary_irq_rp2 import RotaryIRQ
import time

# Define the pins for each encoder
encoders = [
    {'clk': 26, 'dt': 27, 'sw': 28},
    {'clk': 20, 'dt': 21, 'sw': 22},
    {'clk': 12, 'dt': 11, 'sw': 10},
    {'clk': 15, 'dt': 14, 'sw': 13}
]

# Initialize the encoders
rotary_encoders = []
switches = []
current_values = []

for pins in encoders:
    # Initialize RotaryIRQ with internal pull-ups enabled
    rotary = RotaryIRQ(
        pin_num_clk=pins['clk'],
        pin_num_dt=pins['dt'],
        min_val=0,
        max_val=100,
        reverse=False,
        range_mode=RotaryIRQ.RANGE_UNBOUNDED,
        pull_up=True  # Enable internal pull-ups
    )
    rotary_encoders.append(rotary)
    current_values.append(0)

    # Initialize switch pin with internal pull-up enabled
    switch = Pin(pins['sw'], Pin.IN, Pin.PULL_UP)
    switches.append(switch)

print("Initialized all encoders. Rotate and press buttons to test.")

# Main loop
try:
    while True:
        for i, rotary in enumerate(rotary_encoders):
            new_val = rotary.value()
            if current_values[i] != new_val:
                print(f"Encoder {i} - Value: {new_val}")
                current_values[i] = new_val
            
            # Check the switch state
            sw_state = switches[i].value()
            if sw_state == 0:
                print(f"Encoder {i} - Switch: Pressed")

        time.sleep(0.1)
except KeyboardInterrupt:
    print("Test script stopped.")
