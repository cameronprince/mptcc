from machine import Pin, SPI
import sdcard
import os

# Initialize SPI for SD card
spi = SPI(0, baudrate=1000000, polarity=0, phase=0, sck=Pin(2), mosi=Pin(3), miso=Pin(4))
sd = sdcard.SDCard(spi, Pin(1, Pin.OUT))
os.mount(sd, '/sd')
with open('/sd/test.txt', 'w') as f:
    f.write('Hello, SD World!\nThis is a test')

# Read and print the contents of the file
with open('/sd/test.txt', 'r') as f:
    contents = f.read()
    print(contents)  # Print file contents to the console

# Delete the file and dismount SD card
os.remove('/sd/test.txt')
os.umount('/sd')

# Deinitialize SPI
spi.deinit()
