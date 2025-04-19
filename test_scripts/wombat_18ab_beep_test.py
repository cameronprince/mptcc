import SerialWombat
import SerialWombatPin
import machine
import SerialWombat_mp_i2c
import time

from ArduinoFunctions import delay
from ArduinoFunctions import millis

swI2Caddress = 0x6B
i2c = machine.I2C(0, scl=machine.Pin(17), sda=machine.Pin(16), freq=400000, timeout=50000)
sw = SerialWombat_mp_i2c.SerialWombatChip_mp_i2c(i2c, swI2Caddress)

pin = 7

sw.begin()
sw.pinMode(pin, 1)
sw.digitalWrite(pin, 1)
time.sleep_ms(5)
sw.digitalWrite(pin, 0)



