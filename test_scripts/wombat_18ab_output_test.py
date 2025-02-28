"""
This example shows how to measure servo pulses from a radio control reciever on a Serial Wombat 18AB chip.  

IMPORTANT:   This example requires firmware version 2.1.1 or later to work.

This example assumes 6 channels of RC receiver hooked up to pins 14 through 19.  The measured pulse length in uS is
printed to Serial.

This sketch makes use of the SerialWombat18ABOscillatorTuner to improve the meaurement accuracy.  About 1 minute of
runtime is required after reset to achieve full accuracy improvement.

A video demonstrating the use of the SerialWombatPulseTimer_18AB class for RC measurement  on the Serial Wombat 18AB chip is available at:
TBD

Documentation for the SerialWombatPulseTimer_18AB Arduino class is available at:
https://broadwellconsultinginc.github.io/SerialWombatArdLib/class_serial_wombat_pulse_timer__18_a_b.html

"""

import SerialWombat
from ArduinoFunctions import delay
from ArduinoFunctions import millis

#Comment these lines in if you're connecting directly to a Serial Wombat Chip's UART through cPython serial Module
#Change the paramter of SerialWombatChip_cpy_serial to match the name of your Serial port
#import SerialWombat_cpy_serial
#sw = SerialWombat_cpy_serial.SerialWombatChip_cpy_serial("COM3")


#Comment these lines in if you're connecting to a Serial Wombat Chip's I2C port using Micropython's I2C interface
#Change the values for sclPin, sdaPin, and swI2Caddress to match your configuration
import machine
import SerialWombat_mp_i2c
swI2Caddress = 0x6B
i2c = machine.I2C(1, scl=machine.Pin(19), sda=machine.Pin(18), freq=400000, timeout=50000)
sw = SerialWombat_mp_i2c.SerialWombatChip_mp_i2c(i2c, swI2Caddress)
sw.address = 0x6B

#Comment these lines in if you're connecting to a Serial Wombat Chip's UART port using Micropython's UART interface
#Change the values for UARTnum, txPin, and rxPin to match your configuration
#import machine
#import SerialWombat_mp_UART
#txPin = 12
#rxPin = 14
#UARTnum = 2
#uart = machine.UART(UARTnum, baudrate=115200, tx=txPin, rx=rxPin)
#sw = SerialWombat_mp_UART.SerialWombatChipUART(uart)


#Interface independent code starts here:
import SerialWombatPWM
pwmOutput = SerialWombatPWM.SerialWombatPWM_18AB(sw)

oscTun = SerialWombat.SerialWombat18ABOscillatorTuner(sw)

frequencyMin = 50
frequency = frequencyMin
frequencyMax = 1500
frequencyInc = 50
def setup() :
  # put your setup code here, to run once:
  sw.begin()
  pwmOutput.begin(19,0x8000)  #Output on pin 19 , 50% duty cycle
  pwmOutput.writeFrequency_Hz (frequency)
def loop():
  global frequency;
  global frequencyInc
  global frequencyMax
  global frequencyMin
  # put your main code here, to run repeatedly:
  delay(200);
  frequency = frequency + frequencyInc
  if (frequency > frequencyMax):
      frequency = frequencyMin
  pwmOutput.writeFrequency_Hz(frequency)
  oscTun.update();

	

setup()
while(True):
    loop()

