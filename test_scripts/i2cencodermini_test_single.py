import time
import struct
from machine import Pin, I2C
import i2cEncoderMiniLib

# Setup the Interrupt Pins from the encoders.
INT_pins = [
    Pin(21, Pin.IN, Pin.PULL_UP),  # Enable internal pull-up
    Pin(22, Pin.IN, Pin.PULL_UP),
    Pin(26, Pin.IN, Pin.PULL_UP),
    Pin(27, Pin.IN, Pin.PULL_UP)
]

INT_pin = INT_pins[0]

# Initialize the device.
i2c = I2C(0, scl=Pin(17), sda=Pin(16), freq=400000)

# Encoder 1
encoder = i2cEncoderMiniLib.i2cEncoderMiniLib(i2c, 0x21)

def EncoderChange():
    val = encoder.readCounter32()
    print('Changed: %d' % val)

def EncoderPush():
    print('Encoder Pushed!')

def Encoder_INT(pin):
    print("Interrupt detected!")  # Debugging
    if encoder.updateStatus():
        print(f"ESTATUS register value: {bin(encoder.stat)}")  # Debugging
        if encoder.stat & i2cEncoderMiniLib.RINC:
            print("Encoder rotated right")
            EncoderChange()
        if encoder.stat & i2cEncoderMiniLib.RDEC:
            print("Encoder rotated left")
            EncoderChange()
        if encoder.stat & i2cEncoderMiniLib.PUSHP:
            print("Encoder button pushed")
            EncoderPush()

# Initialize encoder
encoder.reset()
print("Encoder reset")
time.sleep(0.1)

# Configuration
encconfig = (i2cEncoderMiniLib.WRAP_ENABLE
             | i2cEncoderMiniLib.DIRE_RIGHT | i2cEncoderMiniLib.IPUP_ENABLE
             | i2cEncoderMiniLib.RMOD_X1)
encoder.begin(encconfig)
print("Encoder begin with config:", encconfig)

# Set encoder parameters
encoder.writeCounter(0)
encoder.writeMax(100)
encoder.writeMin(0)
encoder.writeStep(1)  # Set step size to 1
encoder.writeDoublePushPeriod(50)

# Configure INTCONF register (address 0x01)
# Enable interrupts for encoder rotation and button push
encoder.writeInterruptConfig(0x33)  # Enable RINC, RDEC, and PUSHP interrupts

# Read back INTCONF register for debugging
intconf = encoder.readInterruptConfig()
print(f"INTCONF register value: {bin(intconf)}")

# Read back ESTATUS register for debugging
estatus = encoder.readStatusRaw()
print(f"ESTATUS register value: {bin(estatus)}")

# Read back CVAL (counter value) for debugging
cval = encoder.readCounter32()
print(f"Counter value: {cval}")

print('Board ID code: 0x%X' % encoder.readIDCode())
print('Board Version: 0x%X' % encoder.readVersion())

# Setup an interrupt handler
INT_pin.irq(trigger=Pin.IRQ_FALLING, handler=Encoder_INT)

# Debugging loop
while True:
    # Poll status for debugging
    encoder.updateStatus()

    # Read and print ESTATUS and CVAL registers periodically
    estatus = encoder.readStatusRaw()
    cval = encoder.readCounter32()
    print(f"ESTATUS: {bin(estatus)}, CVAL: {cval}, INT pin: {INT_pin.value()}")
    time.sleep(0.1)