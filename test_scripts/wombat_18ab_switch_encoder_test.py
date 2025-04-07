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

i2c = machine.I2C(0, scl=Pin(17), sda=Pin(16), freq=400000)
sw = SerialWombatChip_mp_i2c(i2c, 0x6B)
sw.begin()

switch_pin = 8
encoder_pin_1 = 11
encoder_pin_2 = 12
switch_interrupt_pin = 18
encoder_interrupt_pin = 19
switch_poc_pin = 1
encoder_poc_pin = 0

switch = SerialWombatDebouncedInput(sw)
switch.begin(pin=switch_pin, debounce_mS=30, invert=True, usePullUp=False)

encoder = SerialWombatQuadEnc(sw)
encoder.begin(encoder_pin_1, encoder_pin_2, debounce_mS=0, pullUpsEnabled=False, readState=5)
encoder.write(32768)

poc_switch = SerialWombatPulseOnChange(sw)
poc_switch.begin(pin=switch_poc_pin, activeMode=1, inactiveMode=0, pulseOnTime=1, pulseOffTime=1, orNotAnd=1)
poc_switch.setEntryOnIncrease(0, switch_pin)

poc_encoder = SerialWombatPulseOnChange(sw)
poc_encoder.begin(pin=encoder_poc_pin, activeMode=1, inactiveMode=0, pulseOnTime=1, pulseOffTime=1, orNotAnd=1)
poc_encoder.setEntryOnChange(0, encoder_pin_1)

switch_interrupt = False
encoder_interrupt = False

def switch_callback(pin):
    global switch_interrupt
    switch_interrupt = True

def encoder_callback(pin):
    global encoder_interrupt
    encoder_interrupt = True

Pin(switch_interrupt_pin, Pin.IN, Pin.PULL_UP).irq(trigger=Pin.IRQ_FALLING, handler=switch_callback)
Pin(encoder_interrupt_pin, Pin.IN, Pin.PULL_UP).irq(trigger=Pin.IRQ_FALLING, handler=encoder_callback)

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
print("- Press the switch")
print("- Rotate the encoder")

asyncio.create_task(poll_switch())
asyncio.create_task(poll_encoder())

loop = asyncio.get_event_loop()
loop.run_forever()