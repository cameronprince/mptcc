import time
import struct
from machine import Pin, I2C
import i2cEncoderLibV2

# Setup the Interrupt Pins from the encoders.
INT_pins = [
    Pin(18, Pin.IN),
    Pin(19, Pin.IN),
    Pin(20, Pin.IN),
    Pin(21, Pin.IN)
]

# Initialize the device.
i2c = I2C(0, scl=Pin(17), sda=Pin(16), freq=400000)

# Encoder addresses and empty encoders list
encoder_addresses = [0x50, 0x30, 0x60, 0x48]
encoders = [i2cEncoderLibV2.i2cEncoderLibV2(i2c, address) for address in encoder_addresses]

def EncoderChange(idx):
    encoders[idx].writeLEDG(100)
    valBytes = struct.unpack('>i', encoders[idx].readCounter32())
    print(f'Changed {idx + 1}: {valBytes[0]}')
    encoders[idx].writeLEDG(0)

def EncoderPush(idx):
    encoders[idx].writeLEDB(100)
    print(f'Encoder {idx + 1} Pushed!')
    encoders[idx].writeLEDB(0)

def EncoderDoublePush(idx):
    encoders[idx].writeLEDB(100)
    encoders[idx].writeLEDG(100)
    print(f'Encoder {idx + 1} Double Push!')
    encoders[idx].writeLEDB(0)
    encoders[idx].writeLEDG(0)

def Encoder_INT(pin):
    idx = INT_pins.index(pin)
    print(f"Interrupt detected on encoder {idx + 1}")

    # Read and reset the status.
    status = encoders[idx].readEncoder8(i2cEncoderLibV2.REG_ESTATUS)
    print(f"Encoder {idx + 1} status: {status}")
    
    # Fire the appropriate callback.
    if status & (i2cEncoderLibV2.RINC | i2cEncoderLibV2.RDEC):
        print(f"Rotary change detected on encoder {idx + 1}")
        EncoderChange(idx)
    if status & i2cEncoderLibV2.PUSHP:
        print(f"Push detected on encoder {idx + 1}")
        EncoderPush(idx)

# Initialize encoders
for encoder in encoders:
    encoder.reset()
    print("Encoder reset")
    time.sleep(0.1)

encconfig = (i2cEncoderLibV2.INT_DATA | i2cEncoderLibV2.WRAP_ENABLE
             | i2cEncoderLibV2.DIRE_RIGHT | i2cEncoderLibV2.IPUP_ENABLE
             | i2cEncoderLibV2.RMOD_X1 | i2cEncoderLibV2.RGB_ENCODER)
for idx, encoder in enumerate(encoders):
    encoder.begin(encconfig)
    print(f"Encoder {idx + 1} begin with config:", encconfig)

    encoder.writeCounter(0)
    encoder.writeMax(100)
    encoder.writeMin(0)
    encoder.writeStep(1)
    encoder.writeAntibouncingPeriod(8)
    encoder.writeDoublePushPeriod(50)
    encoder.writeGammaRLED(i2cEncoderLibV2.GAMMA_2)
    encoder.writeGammaGLED(i2cEncoderLibV2.GAMMA_2)
    encoder.writeGammaBLED(i2cEncoderLibV2.GAMMA_2)

    reg = (i2cEncoderLibV2.PUSHP | i2cEncoderLibV2.RINC | i2cEncoderLibV2.RDEC)
    encoder.writeEncoder8(i2cEncoderLibV2.REG_INTCONF, reg)

    print(f'Board ID code for Encoder {idx + 1}: 0x{encoder.readIDCode():X}')
    print(f'Board Version for Encoder {idx + 1}: 0x{encoder.readVersion():X}')

for encoder in encoders:
    encoder.writeRGBCode(0x640000)
    time.sleep(0.3)
    encoder.writeRGBCode(0x006400)
    time.sleep(0.3)
    encoder.writeRGBCode(0x000064)
    time.sleep(0.3)
    encoder.writeRGBCode(0x00)

# Setup interrupt handlers for each pin
for INT_pin in INT_pins:
    INT_pin.irq(trigger=Pin.IRQ_FALLING, handler=Encoder_INT)
