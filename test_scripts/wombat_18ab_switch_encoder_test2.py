import machine
import time
import uasyncio as asyncio
from machine import Pin
from SerialWombat_mp_i2c import SerialWombatChip_mp_i2c
from SerialWombatDebouncedInput import SerialWombatDebouncedInput
from SerialWombatQuadEnc import SerialWombatQuadEnc
from SerialWombatPulseOnChange import SerialWombatPulseOnChange
from SerialWombatPWM import SerialWombatPWM_18AB

# I2C setup
i2c = machine.I2C(0, scl=Pin(17), sda=Pin(16), freq=400000)
sw = SerialWombatChip_mp_i2c(i2c, 0x6B)
sw.begin()

# Pin definitions for 4 encoders and 4 switches
encoder_pins = [
    [11, 12],  # Encoder 0
    [14, 15],  # Encoder 1
    [17, 18],  # Encoder 2
    [5, 6],    # Encoder 3
]
switch_pins = [8, 13, 16, 19]  # Switch pins

# Interrupt pins
switch_interrupt_pin = 18
encoder_interrupt_pin = 19

# Pulse on change pins
switch_poc_pin = 1
encoder_poc_pin = 0

# Beep configuration
beep_pin = 7
beep_length_ms = 5
beep_volume = 10
beep_pwm_freq = 3000
beep_duty = int((beep_volume / 100) * 65535)

# Initialize piezo PWM
pwm = SerialWombatPWM_18AB(sw)
pwm.begin(beep_pin, 0)
pwm.writeFrequency_Hz(beep_pwm_freq)
pwm.writeDutyCycle(0)

# Beep function
def chirp():
    pwm.writeDutyCycle(beep_duty)
    time.sleep_ms(beep_length_ms)
    pwm.writeDutyCycle(0)

# Initialize switch instances
switches = []
for i, pin in enumerate(switch_pins):
    switch = SerialWombatDebouncedInput(sw)
    switch.begin(pin=pin, debounce_mS=30, invert=True, usePullUp=False)
    switches.append(switch)
    print(f"Switch {i} initialized on pin {pin}")

# Initialize encoder instances
encoders = []
for i, (pin1, pin2) in enumerate(encoder_pins):
    encoder = SerialWombatQuadEnc(sw)
    encoder.begin(pin1, pin2, debounce_mS=0, pullUpsEnabled=False, readState=5)
    encoder.write(32768)
    encoders.append(encoder)
    print(f"Encoder {i} initialized on pins {pin1}, {pin2}")

# Set up PulseOnChange for switches
poc_switch = SerialWombatPulseOnChange(sw)
poc_switch.begin(pin=switch_poc_pin, activeMode=1, inactiveMode=0, pulseOnTime=1, pulseOffTime=1, orNotAnd=1)
for i, pin in enumerate(switch_pins):
    poc_switch.setEntryOnIncrease(i, pin)

# Set up PulseOnChange for encoders
poc_encoder = SerialWombatPulseOnChange(sw)
poc_encoder.begin(pin=encoder_poc_pin, activeMode=1, inactiveMode=0, pulseOnTime=1, pulseOffTime=1, orNotAnd=1)
for i, (pin1, pin2) in enumerate(encoder_pins):
    poc_encoder.setEntryOnChange(i, pin1)

# Global interrupt flags
switch_interrupt = False
encoder_interrupt = False

# Callback functions with chirp
def switch_callback(pin):
    global switch_interrupt
    switch_interrupt = True
    # print(f"Switch interrupt triggered on pin {pin}")
    chirp()

def encoder_callback(pin):
    global encoder_interrupt
    encoder_interrupt = True
    # print(f"Encoder interrupt triggered on pin {pin}")
    chirp()

# Set up interrupts
Pin(switch_interrupt_pin, Pin.IN, Pin.PULL_UP).irq(trigger=Pin.IRQ_FALLING, handler=switch_callback)
Pin(encoder_interrupt_pin, Pin.IN, Pin.PULL_UP).irq(trigger=Pin.IRQ_FALLING, handler=encoder_callback)

# Polling tasks
async def poll_switches():
    global switch_interrupt
    while True:
        if switch_interrupt:
            switch_interrupt = False
            for i, switch in enumerate(switches):
                if switch.readTransitionsState() and switch.transitions > 0:
                    print(f"Switch {i} (pin {switch_pins[i]}) pressed!")
                    break
        await asyncio.sleep(0.01)

async def poll_encoders():
    global encoder_interrupt
    while True:
        if encoder_interrupt:
            encoder_interrupt = False
            for i, encoder in enumerate(encoders):
                val = encoder.read(32768)
                if val != 32768:
                    if val > 32768:
                        print(f"Encoder {i} (pins {encoder_pins[i]}) rotated CW")
                    else:
                        print(f"Encoder {i} (pins {encoder_pins[i]}) rotated CCW")
                    break
        await asyncio.sleep(0.01)

# Start the test
print("Encoders and switches are ready for testing")

asyncio.create_task(poll_switches())
asyncio.create_task(poll_encoders())

loop = asyncio.get_event_loop()
loop.run_forever()