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

encoder1 = i2cEncoderLibV2.i2cEncoderLibV2(i2c, 0x50)
encoder1.reset()
time.sleep(0.1)
encoder1.begin(encconfig)

encoder2 = i2cEncoderLibV2.i2cEncoderLibV2(i2c, 0x30)
encoder2.reset()
time.sleep(0.1)
encoder2.begin(encconfig)

encoder3 = i2cEncoderLibV2.i2cEncoderLibV2(i2c, 0x60)
encoder3.reset()
time.sleep(0.1)
encoder3.begin(encconfig)

encoder4 = i2cEncoderLibV2.i2cEncoderLibV2(i2c, 0x44)
encoder4.reset()
time.sleep(0.1)
encoder4.begin(encconfig)

encoder1.writeGammaRLED(i2cEncoderLibV2.GAMMA_2)
encoder1.writeGammaGLED(i2cEncoderLibV2.GAMMA_2)
encoder1.writeGammaBLED(i2cEncoderLibV2.GAMMA_2)
encoder1.writeFadeRGB(2)
encoder1.writeRGBCode(0x640000)

encoder2.writeGammaRLED(i2cEncoderLibV2.GAMMA_2)
encoder2.writeGammaGLED(i2cEncoderLibV2.GAMMA_2)
encoder2.writeGammaBLED(i2cEncoderLibV2.GAMMA_2)
encoder2.writeFadeRGB(2)
encoder2.writeRGBCode(0x640000)

encoder3.writeGammaRLED(i2cEncoderLibV2.GAMMA_2)
encoder3.writeGammaGLED(i2cEncoderLibV2.GAMMA_2)
encoder3.writeGammaBLED(i2cEncoderLibV2.GAMMA_2)
encoder3.writeFadeRGB(2)
encoder3.writeRGBCode(0x640000)

encoder4.writeGammaRLED(i2cEncoderLibV2.GAMMA_2)
encoder4.writeGammaGLED(i2cEncoderLibV2.GAMMA_2)
encoder4.writeGammaBLED(i2cEncoderLibV2.GAMMA_2)
encoder4.writeFadeRGB(2)
encoder4.writeRGBCode(0x640000)

time.sleep(0.3)
encoder4.writeRGBCode(0x000000)
encoder3.writeRGBCode(0x000000)
encoder2.writeRGBCode(0x000000)
encoder1.writeRGBCode(0x000000)
