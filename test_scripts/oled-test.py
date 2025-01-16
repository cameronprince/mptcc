from machine import Pin, I2C, SPI
from ssd1306 import SSD1306_I2C

# display address is 0x3c
i2c = I2C(1, sda=Pin(18), scl=Pin(19), freq=400000)
oled = SSD1306_I2C(128, 64, i2c)

# spi = SPI(0, baudrate=1000000, polarity=0, phase=0, sck=Pin(2), mosi=Pin(3), miso=Pin(4))
# cs_display = Pin(5, Pin.OUT)
# cs_display.value(0)
# oled = SSD1306_SPI(128, 64, spi, Pin(4), Pin(16), Pin(5))

oled.fill(0)
oled.text("Python TCC", 0, 0)
oled.show()