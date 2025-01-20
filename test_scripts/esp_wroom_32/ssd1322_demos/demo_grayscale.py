"""SSD1322 demo (grayscale)."""
from time import sleep
from machine import Pin, SPI  # type: ignore
from ssd1322 import Display


def test():
    """Test code."""

    spi = SPI(1, baudrate=16000000, polarity=0, phase=0, sck=Pin(14), mosi=Pin(13))
    dc=Pin(17,Pin.OUT)
    cs=Pin(22,Pin.OUT)
    res=Pin(16,Pin.OUT)

    display = Display(spi, dc=dc, cs=cs, rst=res)

    for x in range(0, 256, 16):
        background = x // 16
        foreground = 15 - background
        display.fill_rectangle(x, 0, 16, 64, background)
        label = str(background)
        x2 = x + 4 if len(label) == 1 else x
        display.draw_text8x8(x2, 28, label, foreground)

    display.present()

    sleep(15)
    display.cleanup()
    print('Done.')


test()
