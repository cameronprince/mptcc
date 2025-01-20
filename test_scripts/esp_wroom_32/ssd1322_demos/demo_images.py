"""SSD1322 demo (images)."""
from time import sleep
from machine import Pin, SPI  # type: ignore
from ssd1322 import Display
import gc


def test():
    """Test code."""
    spi = SPI(1, baudrate=16000000, polarity=0, phase=0, sck=Pin(14), mosi=Pin(13))
    dc=Pin(17,Pin.OUT)
    cs=Pin(22,Pin.OUT)
    res=Pin(16,Pin.OUT)

    display = Display(spi, dc=dc, cs=cs, rst=res)
    
    display.draw_bitmap_GS4('images/faces_256x64.gs4', 0, 0, 256, 64)
    display.present()
    gc.collect()
    sleep(5)

    display.clear_buffers()
    display.draw_bitmap_mono("images/eyes_128x42.mono",
                             0, display.height // 2 - 21, 128, 42)
    display.present()
    gc.collect()
    sleep(2)

    display.draw_bitmap_mono("images/doggy_jet128x64.mono",
                             128, 0, 128, 64, invert=True)
    display.present()
    gc.collect()
    sleep(5)

    display.clear_buffers()
    display.draw_bitmap_mono("images/invaders_48x36.mono",
                             0, 14, 48, 36, rotate=90)
    display.draw_bitmap_mono("images/invaders_48x36.mono",
                             69, 14, 48, 36)
    display.draw_bitmap_mono("images/invaders_48x36.mono",
                             139, 14, 48, 36, rotate=180)
    display.draw_bitmap_mono("images/invaders_48x36.mono",
                             207, 14, 48, 36, rotate=270)
    display.present()
    gc.collect()
    sleep(5)

    display.draw_bitmap_GS4('images/clover_64x64.gs4', 0, 0, 64, 64)
    display.draw_bitmap_GS4('images/clover_64x64.gs4', 64, 0, 64, 64,
                            rotate=90)
    display.draw_bitmap_GS4('images/clover_64x64.gs4', 128, 0, 64, 64,
                            rotate=180)
    display.draw_bitmap_GS4('images/clover_64x64.gs4', 192, 0, 64, 64,
                            rotate=270)
    display.present()
    gc.collect()
    sleep(5)

    display.draw_bitmap_GS4('images/clover_64x64.gs4', 0, 0, 64, 64,
                            invert=True)
    display.draw_bitmap_GS4('images/clover_64x64.gs4', 64, 0, 64, 64,
                            invert=True, rotate=90)
    display.draw_bitmap_GS4('images/clover_64x64.gs4', 128, 0, 64, 64,
                            invert=True, rotate=180)
    display.draw_bitmap_GS4('images/clover_64x64.gs4', 192, 0, 64, 64,
                            invert=True, rotate=270)
    display.present()
    gc.collect()

    sleep(10)
    display.cleanup()
    print('Done.')


test()
