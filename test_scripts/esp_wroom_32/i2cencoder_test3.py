import time
import struct
from machine import Pin, I2C
import i2cEncoderLibV2

# Setup the Interrupt Pin from the encoder.
INT_pin = Pin(34, Pin.IN)

# Initialize the device.
i2c = I2C(1, scl=Pin(33), sda=Pin(32), freq=400000)

# Encoder addresses and empty encoders list
encoder_addresses = [0x50, 0x30, 0x60, 0x44]
encoders = []

for address in encoder_addresses:
    encoder = i2cEncoderLibV2.i2cEncoderLibV2(i2c, address)
    encoders.append(encoder)

def EncoderChange1():
    encoders[0].writeLEDG(100)
    valBytes = struct.unpack('>i', encoders[0].readCounter32())
    print('Changed 1: %d' % valBytes[0])
    encoders[0].writeLEDG(0)

def EncoderPush1():
    encoders[0].writeLEDB(100)
    print('Encoder 1 Pushed!')
    encoders[0].writeLEDB(0)

def EncoderDoublePush1():
    encoders[0].writeLEDB(100)
    encoders[0].writeLEDG(100)
    print('Encoder 1 Double Push!')
    encoders[0].writeLEDB(0)
    encoders[0].writeLEDG(0)

def EncoderMax1():
    encoders[0].writeLEDR(100)
    print('Encoder 1 max!')
    encoders[0].writeLEDR(0)

def EncoderMin1():
    encoders[0].writeLEDR(100)
    print('Encoder 1 min!')
    encoders[0].writeLEDR(0)

def EncoderChange2():
    encoders[1].writeLEDG(100)
    valBytes = struct.unpack('>i', encoders[1].readCounter32())
    print('Changed 2: %d' % valBytes[0])
    encoders[1].writeLEDG(0)

def EncoderPush2():
    encoders[1].writeLEDB(100)
    print('Encoder 2 Pushed!')
    encoders[1].writeLEDB(0)

def EncoderDoublePush2():
    encoders[1].writeLEDB(100)
    encoders[1].writeLEDG(100)
    print('Encoder 2 Double Push!')
    encoders[1].writeLEDB(0)
    encoders[1].writeLEDG(0)

def EncoderMax2():
    encoders[1].writeLEDR(100)
    print('Encoder 2 max!')
    encoders[1].writeLEDR(0)

def EncoderMin2():
    encoders[1].writeLEDR(100)
    print('Encoder 2 min!')
    encoders[1].writeLEDR(0)

# Repeat the same for Encoder 3 and Encoder 4...

def Encoder_INT(pin):
    for encoder in encoders:
        encoder.updateStatus()

# Initialize encoders
for encoder in encoders:
    encoder.reset()
    print("Encoder reset")
    time.sleep(0.1)

encconfig = (i2cEncoderLibV2.INT_DATA | i2cEncoderLibV2.WRAP_ENABLE
             | i2cEncoderLibV2.DIRE_RIGHT | i2cEncoderLibV2.IPUP_ENABLE
             | i2cEncoderLibV2.RMOD_X1 | i2cEncoderLibV2.RGB_ENCODER)
for index, encoder in enumerate(encoders):
    encoder.begin(encconfig)
    print("Encoder begin with config:", encconfig)

    encoder.writeCounter(0)
    encoder.writeMax(35)
    encoder.writeMin(-20)
    encoder.writeStep(1)
    encoder.writeAntibouncingPeriod(8)
    encoder.writeDoublePushPeriod(50)
    encoder.writeGammaRLED(i2cEncoderLibV2.GAMMA_2)
    encoder.writeGammaGLED(i2cEncoderLibV2.GAMMA_2)
    encoder.writeGammaBLED(i2cEncoderLibV2.GAMMA_2)

    if index == 0:
        encoder.onChange = EncoderChange1
        encoder.onButtonPush = EncoderPush1
        encoder.onButtonDoublePush = EncoderDoublePush1
        encoder.onMax = EncoderMax1
        encoder.onMin = EncoderMin1
    elif index == 1:
        encoder.onChange = EncoderChange2
        encoder.onButtonPush = EncoderPush2
        encoder.onButtonDoublePush = EncoderDoublePush2
        encoder.onMax = EncoderMax2
        encoder.onMin = EncoderMin2

    encoder.autoconfigInterrupt()
    print('Board ID code: 0x%X' % encoder.readIDCode())
    print('Board Version: 0x%X' % encoder.readVersion())

for encoder in encoders:
    encoder.writeRGBCode(0x640000)
    time.sleep(0.3)
    encoder.writeRGBCode(0x006400)
    time.sleep(0.3)
    encoder.writeRGBCode(0x000064)
    time.sleep(0.3)
    encoder.writeRGBCode(0x00)

# Setup an interrupt handler
INT_pin.irq(trigger=Pin.IRQ_FALLING, handler=Encoder_INT)

#while True:
#    # For debugging, we can poll status
#    for encoder in encoders:
#        encoder.updateStatus()
#    time.sleep(0.1)
