import machine
import SimpleMIDIDecoder

uart = machine.UART(0, baudrate=31250, rx=machine.Pin(13))
md = SimpleMIDIDecoder.SimpleMIDIDecoder()

from machine import Pin, I2C, SPI

def doMidiNoteOn(ch,cmd,note,vel):
    print("Note On \t", note, "\t", vel)

def doMidiNoteOff(ch,cmd,note,vel):
    print("Note Off\t", note, "\t", vel)

def doMidiThru(ch,cmd,data1,data2):
    print("Thru\t", cmd, "\t", data1, "\t", data2)

md = SimpleMIDIDecoder.SimpleMIDIDecoder()
md.cbNoteOn (doMidiNoteOn)
md.cbNoteOff (doMidiNoteOff)
md.cbThru (doMidiThru)

while True:
    if (uart.any()):
        md.read(uart.read(1)[0])


