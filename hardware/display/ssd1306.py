"""
MicroPython Tesla Coil Controller (MPTCC)
by Cameron Prince
teslauniverse.com

hardware/display/ssd1306.py
Display sub-class for interfacing with SSD1306 display driver.
Based on https://github.com/TimHanewich/MicroPython-SSD1306/blob/master/src/ssd1306.py
"""

from .display import Display
from ...hardware.init import init
from machine import Pin, I2C, SPI
from micropython import const
import framebuf
import time

SET_CONTRAST = const(0x81)
SET_ENTIRE_ON = const(0xA4)
SET_NORM_INV = const(0xA6)
SET_DISP = const(0xAE)
SET_MEM_ADDR = const(0x20)
SET_COL_ADDR = const(0x21)
SET_PAGE_ADDR = const(0x22)
SET_DISP_START_LINE = const(0x40)
SET_SEG_REMAP = const(0xA0)
SET_MUX_RATIO = const(0xA8)
SET_COM_OUT_DIR = const(0xC0)
SET_DISP_OFFSET = const(0xD3)
SET_COM_PIN_CFG = const(0xDA)
SET_DISP_CLK_DIV = const(0xD5)
SET_PRECHARGE = const(0xD9)
SET_VCOM_DESEL = const(0xDB)
SET_CHARGE_PUMP = const(0x8D)

class SSD1306(Display):
    def __init__(
        self,
        i2c_instance=None,
        i2c_addr=0x3C,
        spi_instance=None,
        external_vcc=False,
        width=128,
        height=64,
        line_height=12,
        font_width=8,
        font_height=8,
        header_height=10,
        items_per_page=4,
    ):

        super().__init__()
        self.init = init

        # Initialize the framebuffer.
        self.width = width
        self.height = height
        self.external_vcc = external_vcc
        self.pages = self.height // 8
        self.buffer = bytearray(self.pages * self.width)
        self.framebuf = framebuf.FrameBuffer(self.buffer, self.width, self.height, framebuf.MONO_VLSB)

        instance_key = len(self.init.display_instances['ssd1306'])

        # Initialize the display interface.
        if i2c_instance is not None:
            if i2c_instance == 2:
                self.init.init_i2c_2()
                self.i2c = self.init.i2c_2
                self.mutex = self.init.i2c_2_mutex
            else:
                self.init.init_i2c_1()
                self.i2c = self.init.i2c_1
                self.mutex = self.init.i2c_1_mutex

            self.driver = SSD1306_I2C(
                self.width,
                self.height,
                i2c=self.i2c,
                addr=i2c_addr,
                external_vcc=self.external_vcc,
            )
            print(
                f"SSD1306 display driver {instance_key} initialized on I2C instance {i2c_instance} "
                f"at address: 0x{i2c_addr:02X}"
            )
        elif spi_instance is not None:
            spi = SPI(spi_instance)
            dc_pin = Pin(self.init.PIN_SPI_DC)
            res_pin = Pin(self.init.PIN_SPI_RST)
            cs_pin = Pin(self.init.PIN_SPI_CS)
            self.driver = SSD1306_SPI(
                self.width,
                self.height,
                spi=spi,
                dc=dc_pin,
                res=res_pin,
                cs=cs_pin,
                external_vcc=self.external_vcc,
            )
            print(f"SSD1306 display driver {instance_key} initialized on SPI instance {spi_instance}")
        else:
            raise ValueError("Either i2c_instance or spi_instance must be provided.")

        self.init_display()

    def init_display(self):
        """
        Initialize the SSD1306 display.
        """
        for cmd in (
            SET_DISP | 0x00,  # off
            # address setting
            SET_MEM_ADDR,
            0x00,  # horizontal
            # resolution and layout
            SET_DISP_START_LINE | 0x00,
            SET_SEG_REMAP | 0x01,  # column addr 127 mapped to SEG0
            SET_MUX_RATIO,
            self.height - 1,
            SET_COM_OUT_DIR | 0x08,  # scan from COM[N] to COM0
            SET_DISP_OFFSET,
            0x00,
            SET_COM_PIN_CFG,
            0x02 if self.width > 2 * self.height else 0x12,
            # timing and driving scheme
            SET_DISP_CLK_DIV,
            0x80,
            SET_PRECHARGE,
            0x22 if self.external_vcc else 0xF1,
            SET_VCOM_DESEL,
            0x30,  # 0.83*Vcc
            # display
            SET_CONTRAST,
            0xFF,  # maximum
            SET_ENTIRE_ON,  # output follows RAM contents
            SET_NORM_INV,  # not inverted
            # charge pump
            SET_CHARGE_PUMP,
            0x10 if self.external_vcc else 0x14,
            SET_DISP | 0x01,
        ):  # on
            self.write_cmd(cmd)
        self.framebuf.fill(0)  # Call fill on self.framebuf
        self._show()

    def write_cmd(self, cmd):
        """
        Write a command to the display.
        """
        self.driver.write_cmd(cmd)

    def write_data(self, buf):
        """
        Write data to the display.
        """
        self.driver.write_data(buf)

    def poweroff(self):
        """
        Turn off the display.
        """
        self.write_cmd(SET_DISP | 0x00)

    def poweron(self):
        """
        Turn on the display.
        """
        self.write_cmd(SET_DISP | 0x01)

    def contrast(self, contrast):
        """
        Set the display contrast.
        """
        self.write_cmd(SET_CONTRAST)
        self.write_cmd(contrast)

    def invert(self, invert):
        """
        Invert the display.
        """
        self.write_cmd(SET_NORM_INV | (invert & 1))

    def _show(self):
        """
        Update the display with the current frame buffer content.
        """
        x0 = 0
        x1 = self.width - 1
        if self.width == 64:
            # displays with width of 64 pixels are shifted by 32
            x0 += 32
            x1 += 32
        self.write_cmd(SET_COL_ADDR)
        self.write_cmd(x0)
        self.write_cmd(x1)
        self.write_cmd(SET_PAGE_ADDR)
        self.write_cmd(0)
        self.write_cmd(self.pages - 1)
        self.write_data(self.buffer)

    def _clear(self):
        """
        Clear the display.
        """
        self.framebuf.fill(0)
        self._show()

    def _text(self, text, x, y, color=1):
        """
        Display text on the screen.
        """
        self.framebuf.text(text, x, y, color)

    def _hline(self, x, y, w, color):
        """
        Draw a horizontal line on the screen.
        """
        self.framebuf.hline(x, y, w, color)

    def _fill_rect(self, x, y, w, h, color):
        """
        Draw a filled rectangle on the screen.
        """
        self.framebuf.fill_rect(x, y, w, h, color)


class SSD1306_I2C:
    def __init__(self, width, height, i2c, addr=0x3C, external_vcc=False):
        self.width = width
        self.height = height
        self.i2c = i2c
        self.addr = addr
        self.external_vcc = external_vcc
        self.temp = bytearray(2)
        self.write_list = [b"\x40", None]  # Co=0, D/C#=1

    def write_cmd(self, cmd):
        self.temp[0] = 0x80  # Co=1, D/C#=0
        self.temp[1] = cmd
        self.i2c.writeto(self.addr, self.temp)

    def write_data(self, buf):
        self.write_list[1] = buf
        self.i2c.writevto(self.addr, self.write_list)


class SSD1306_SPI:
    def __init__(self, width, height, spi, dc, res, cs, external_vcc=False):
        self.width = width
        self.height = height
        self.spi = spi
        self.dc = dc
        self.res = res
        self.cs = cs
        self.external_vcc = external_vcc
        self.rate = 10 * 1024 * 1024
        dc.init(dc.OUT, value=0)
        res.init(res.OUT, value=0)
        cs.init(cs.OUT, value=1)
        import time

        self.res(1)
        time.sleep_ms(1)
        self.res(0)
        time.sleep_ms(10)
        self.res(1)

    def write_cmd(self, cmd):
        self.spi.init(baudrate=self.rate, polarity=0, phase=0)
        self.cs(1)
        self.dc(0)
        self.cs(0)
        self.spi.write(bytearray([cmd]))
        self.cs(1)

    def write_data(self, buf):
        self.spi.init(baudrate=self.rate, polarity=0, phase=0)
        self.cs(1)
        self.dc(1)
        self.cs(0)
        self.spi.write(buf)
        self.cs(1)