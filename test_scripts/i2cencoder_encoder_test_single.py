import time
import struct
from machine import Pin, I2C
import i2cEncoderLibV2

# Setup the Interrupt Pins from the encoders.
INT_pins = [
    Pin(0, Pin.IN),
    Pin(19, Pin.IN),
    Pin(20, Pin.IN),
    Pin(21, Pin.IN)
]

INT_pin = INT_pins[0]

# Initialize the device.
i2c = I2C(1, scl=Pin(11), sda=Pin(10), freq=400000)

# encoder_addresses = [0x50, 0x30, 0x60, 0x48]

# Encoder 1
encoder = i2cEncoderLibV2.i2cEncoderLibV2(i2c, 0x50)

# Encoder 2
# encoder = i2cEncoderLibV2.i2cEncoderLibV2(i2c, 0x30)

# Encoder 3
# encoder = i2cEncoderLibV2.i2cEncoderLibV2(i2c, 0x60)

# Encoder 4
# encoder = i2cEncoderLibV2.i2cEncoderLibV2(i2c, 0x48)

def EncoderChange():
    encoder.writeLEDG(100)
    valBytes = struct.unpack('>i', encoder.readCounter32())
    print('Changed: %d' % valBytes[0])
    encoder.writeLEDG(0)

def EncoderPush():
    encoder.writeLEDB(100)
    print('Encoder Pushed!')
    encoder.writeLEDB(0)

def Encoder_INT(pin):
    encoder.updateStatus()

# Initialize encoder
encoder.reset()
print("Encoder reset")
time.sleep(0.1)

encconfig = (i2cEncoderLibV2.INT_DATA | i2cEncoderLibV2.WRAP_ENABLE
             | i2cEncoderLibV2.DIRE_RIGHT | i2cEncoderLibV2.IPUP_ENABLE
             | i2cEncoderLibV2.RMOD_X1 | i2cEncoderLibV2.RGB_ENCODER)
encoder.begin(encconfig)
print("Encoder begin with config:", encconfig)

encoder.writeCounter(0)
encoder.writeMax(100)
encoder.writeMin(0)
encoder.writeStep(1)
encoder.writeAntibouncingPeriod(8)
encoder.writeDoublePushPeriod(50)
encoder.writeGammaRLED(i2cEncoderLibV2.GAMMA_2)
encoder.writeGammaGLED(i2cEncoderLibV2.GAMMA_2)
encoder.writeGammaBLED(i2cEncoderLibV2.GAMMA_2)

encoder.onChange = EncoderChange
encoder.onButtonPush = EncoderPush

encoder.autoconfigInterrupt()
print('Board ID code: 0x%X' % encoder.readIDCode())
print('Board Version: 0x%X' % encoder.readVersion())

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
#    encoder.updateStatus()
#    time.sleep(0.1)
