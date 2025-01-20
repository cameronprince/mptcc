import time
import struct
from machine import Pin, I2C
import i2cEncoderLibV2

# Setup the Interrupt Pin from the encoder.
INT_pin = Pin(34, Pin.IN)

# Initialize the device.
i2c = I2C(1, scl=Pin(33), sda=Pin(32), freq=400000)

encconfig = (i2cEncoderLibV2.INT_DATA | i2cEncoderLibV2.WRAP_ENABLE
             | i2cEncoderLibV2.DIRE_RIGHT | i2cEncoderLibV2.IPUP_ENABLE
             | i2cEncoderLibV2.RMOD_X1 | i2cEncoderLibV2.RGB_ENCODER)

encoder_addresses = [0x50, 0x30, 0x60, 0x44]
encoders = []

for address in encoder_addresses:
    encoder = i2cEncoderLibV2.i2cEncoderLibV2(i2c, address)
    encoder.reset()
    time.sleep(0.1)
    encoder.begin(encconfig)
    encoder.writeGammaRLED(i2cEncoderLibV2.GAMMA_2)
    encoder.writeGammaGLED(i2cEncoderLibV2.GAMMA_2)
    encoder.writeGammaBLED(i2cEncoderLibV2.GAMMA_2)
    encoder.writeFadeRGB(2)
    encoder.writeRGBCode(0x640000)
    encoders.append(encoder)

while True:
    time.sleep(1)
    for encoder in encoders:
        # Red
        encoder.writeRGBCode(0x640000)
    time.sleep(0.3)
    for encoder in encoders:
        encoder.writeRGBCode(0x000000)

    time.sleep(1)
    for encoder in encoders:
        # Yellow
        encoder.writeRGBCode(0xFFFF00)
    time.sleep(0.3)
    for encoder in encoders:
        encoder.writeRGBCode(0x000000)

    time.sleep(1)
    for encoder in encoders:
        # Green
        encoder.writeRGBCode(0x006400)
    time.sleep(0.3)
    for encoder in encoders:
        encoder.writeRGBCode(0x000000)

    time.sleep(1)
    for encoder in encoders:
        # Blue
        encoder.writeRGBCode(0x000064)
    time.sleep(0.3)
    for encoder in encoders:
        encoder.writeRGBCode(0x000000)



