"""SSD1309 demo (fonts)."""
from time import sleep
from machine import Pin, I2C  # type: ignore
from xglcd_font import XglcdFont
from ssd1309 import Display

i2c = I2C(1, sda=Pin(18), scl=Pin(19), freq=400000)
display = Display(i2c=i2c, rst=Pin(2), flip=True)

# bally = XglcdFont('fonts/Bally7x9.c', 7, 9)

# text_height = bally.height
# display.draw_text(display.width, display.height // 2 - text_height // 2,
#                   "Bally", bally, rotate=180)

text = str.upper("MicroPython TCC")

display.draw_text8x8(0, 0, text)
display.draw_hline(0, 10, 128)
display.present()
