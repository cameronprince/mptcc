import ssd1322_1 as ssd1322
from machine import SPI, Pin
spi = SPI(1, baudrate=16000000, polarity=0, phase=0, sck=Pin(14), mosi=Pin(13))
dc=Pin(17,Pin.OUT)
cs=Pin(22,Pin.OUT)
res=Pin(16,Pin.OUT)
disp=ssd1322.SSD1322_SPI(256,64,spi,dc,cs,res)
#disp.fill(0)
disp.line(5,5,60,60,0xff)
disp.show()