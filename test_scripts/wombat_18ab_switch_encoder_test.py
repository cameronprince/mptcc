"""
Simplest Serial Wombat 18AB Switch and Encoder Test
Hardcoded for MPTCC configuration:
- Switch on pin 1, interrupt on pin 18
- Encoder on pins 13,12, interrupt on pin 19
"""

import machine
import time
import uasyncio as asyncio
from machine import Pin
from SerialWombat_mp_i2c import SerialWombatChip_mp_i2c
from SerialWombatDebouncedInput import SerialWombatDebouncedInput
from SerialWombatQuadEnc import SerialWombatQuadEnc
from SerialWombatPulseOnChange import SerialWombatPulseOnChange

# Initialize I2C (hardcoded values)
i2c = machine.I2C(0, scl=Pin(17), sda=Pin(16), freq=400000)
sw = SerialWombatChip_mp_i2c(i2c, 0x6B)
sw.begin()
time.sleep(0.2)

# Initialize switch on pin 1
switch = SerialWombatDebouncedInput(sw)
switch.begin(pin=1, debounce_mS=30, invert=True, usePullUp=False)

# Initialize encoder on pins 13,12
encoder = SerialWombatQuadEnc(sw)
encoder.begin(13, 12, debounce_mS=1, pullUpsEnabled=False, readState=6)
encoder.write(32768)  # Center value

# Set up pulse on change for switch (pin 6)
poc_switch = SerialWombatPulseOnChange(sw)
poc_switch.begin(pin=6, activeMode=1, inactiveMode=0, pulseOnTime=50, pulseOffTime=50, orNotAnd=1)
poc_switch.setEntryOnIncrease(0, 13)

# Set up pulse on change for encoder (pin 5)
poc_encoder = SerialWombatPulseOnChange(sw)
poc_encoder.begin(pin=5, activeMode=1, inactiveMode=0, pulseOnTime=50, pulseOffTime=50, orNotAnd=1)
poc_encoder.setEntryOnIncrease(0, 12)


# Set up interrupts
switch_interrupt = False
encoder_interrupt = False

def switch_callback(pin):
    global switch_interrupt
    switch_interrupt = True

def encoder_callback(pin):
    global encoder_interrupt
    encoder_interrupt = True

# Switch interrupt on pin 18 (pull-up)
Pin(18, Pin.IN, Pin.PULL_UP).irq(trigger=Pin.IRQ_FALLING, handler=switch_callback)

# Encoder interrupt on pin 19 (pull-up)
Pin(19, Pin.IN, Pin.PULL_UP).irq(trigger=Pin.IRQ_FALLING, handler=encoder_callback)

async def poll_switch():
    global switch_interrupt
    while True:
        if switch_interrupt:
            switch_interrupt = False
            if switch.readTransitionsState() and switch.transitions > 0:
                print("Switch pressed!")
        await asyncio.sleep(0.01)

async def poll_encoder():
    global encoder_interrupt
    while True:
        if encoder_interrupt:
            encoder_interrupt = False
            val = encoder.read(32768)
            if val != 32768:
                if val > 32768:
                    print("Encoder rotated CW")
                else:
                    print("Encoder rotated CCW")
        await asyncio.sleep(0.01)

print("Testing started:")
print("- Press the switch (pin 1)")
print("- Rotate the encoder (pins 13,12)")

asyncio.create_task(poll_switch())
asyncio.create_task(poll_encoder())

loop = asyncio.get_event_loop()
loop.run_forever()