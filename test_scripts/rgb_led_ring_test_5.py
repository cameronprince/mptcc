from utime import sleep_ms
from machine import I2C, Pin

I2C_ADDR = 0x20
i2c = I2C(0, scl=Pin(17), sda=Pin(16), freq=400000)

# Constants from:
# https://github.com/Fattoresaimon/ArduinoDuPPaLib/blob/master/src/LEDRing.h
ISSI3745_PAGE0 = 0x00
ISSI3745_PAGE1 = 0x01
ISSI3745_PAGE2 = 0x02
ISSI3745_COMMANDREGISTER = 0xFD
ISSI3745_COMMANDREGISTER_LOCK = 0xFE
ISSI3745_ULOCK_CODE = 0xC5
ISSI3745_CONFIGURATION = 0x00
ISSI3745_GLOBALCURRENT = 0x01
ISSI3745_SPREADSPECTRUM = 0x25
ISSI3745_RESET_REG = 0x2F
ISSI_LED_MAP = [
    [0x12, 0x24, 0x36, 0x48, 0x5A, 0x6C, 0x7E, 0x90, 0x0F, 0x21, 0x33, 0x45, 0x57, 0x69, 0x7B, 0x8D, 0x0C, 0x1E, 0x30, 0x42, 0x54, 0x66, 0x78, 0x8A, 0x09, 0x1B, 0x2D, 0x3F, 0x51, 0x63, 0x75, 0x87, 0x06, 0x18, 0x2A, 0x3C, 0x4E, 0x60, 0x72, 0x84, 0x03, 0x15, 0x27, 0x39, 0x4B, 0x5D, 0x6F, 0x81],  # Red
    [0x11, 0x23, 0x35, 0x47, 0x59, 0x6B, 0x7D, 0x8F, 0x0E, 0x20, 0x32, 0x44, 0x56, 0x68, 0x7A, 0x8C, 0x0B, 0x1D, 0x2F, 0x41, 0x53, 0x65, 0x77, 0x89, 0x08, 0x1A, 0x2C, 0x3E, 0x50, 0x62, 0x74, 0x86, 0x05, 0x17, 0x29, 0x3B, 0x4D, 0x5F, 0x71, 0x83, 0x02, 0x14, 0x26, 0x38, 0x4A, 0x5C, 0x6E, 0x80],  # Green
    [0x10, 0x22, 0x34, 0x46, 0x58, 0x6A, 0x7C, 0x8E, 0x0D, 0x1F, 0x31, 0x43, 0x55, 0x67, 0x79, 0x8B, 0x0A, 0x1C, 0x2E, 0x40, 0x52, 0x64, 0x76, 0x88, 0x07, 0x19, 0x2B, 0x3D, 0x4F, 0x61, 0x73, 0x85, 0x04, 0x16, 0x28, 0x3A, 0x4C, 0x5E, 0x70, 0x82, 0x01, 0x13, 0x25, 0x37, 0x49, 0x5B, 0x6D, 0x7F]   # Blue
]

# Functions from:
# https://github.com/Fattoresaimon/ArduinoDuPPaLib/blob/master/src/LEDRing.cpp
def PWM_MODE():
    print("PWM_MODE")
    selectBank(ISSI3745_PAGE0)

def Configuration(conf):
    print(f"Configuration conf: {conf}")
    selectBank(ISSI3745_PAGE2)
    writeRegister8(ISSI3745_CONFIGURATION, conf)

def SetScalingAll(scal):
    print(f"SetScaling_All scal: {scal}")
    selectBank(ISSI3745_PAGE1)
    for i in range(1, 145):
        writeRegister8(i, scal)

def GlobalCurrent(curr):
    print(f"GlobalCurrent curr {curr}")
    selectBank(ISSI3745_PAGE2)
    writeRegister8(ISSI3745_GLOBALCURRENT, curr)

def SpreadSpectrum(spread):
    print(f"SpreadSpectrum spread: {spread}")
    selectBank(ISSI3745_PAGE2)
    writeRegister8(ISSI3745_SPREADSPECTRUM, spread)

def Reset():
    print("Reset")
    selectBank(ISSI3745_PAGE2);
    writeRegister8(ISSI3745_RESET_REG, 0xAE);

"""
def Set_RGB(led_n, color):
    print(f"Set_RGB led_n: {led_n} color: {color}")
    selectBank(ISSI3745_PAGE0)
    writeRegister8(ISSI_LED_MAP[0][led_n], (color >> 16) & 0xFF)
    writeRegister8(ISSI_LED_MAP[1][led_n], (color >> 8) & 0xFF)
    writeRegister8(ISSI_LED_MAP[2][led_n], color & 0xFF)
"""

def Set_RGB(led_n, color):
    print(f"Set_RGB led_n: {led_n} color: {color}")
    if not 0 <= led_n < 48:
        raise ValueError("LED index must be 0-47")
    selectBank(ISSI3745_PAGE0)
    r = (color >> 16) & 0xFF
    g = (color >> 8) & 0xFF
    b = color & 0xFF
    data = [b, g, r]  # Blue, green, red order for consecutive registers
    start_reg = ISSI_LED_MAP[2][led_n]  # Start at blue register
    print(f"Set_RGB data: {data} start_reg: {start_reg}")
    writeBuff(start_reg, data, 3)

def ClearAll():
    print("ClearAll")
    PWM_MODE()
    data = [0] * 144
    writeBuff(1, data, 144)

def selectBank(b):
    print(f"selectBank {b}")
    writeRegister8(ISSI3745_COMMANDREGISTER_LOCK, ISSI3745_ULOCK_CODE)
    writeRegister8(ISSI3745_COMMANDREGISTER, b)

def writeRegister8(reg, data):
    print(f"writeRegister8 reg: {reg} data: {data}")
    i2c.writeto_mem(I2C_ADDR, reg, bytes([data]))

def writeBuff(reg, data, dim):
    print(f"writeBuff reg: {reg} data: {data} dim: {dim}")
    if isinstance(data, (bytes, bytearray)):
        buffer = data[:dim]
    else:
        buffer = bytes(data[:dim])
    i2c.writeto_mem(I2C_ADDR, reg, buffer)

# Custom functions.
def rgb_to_hex(rgb):
    """
    Convert an RGB tuple to a hex color code.

    Parameters:
    ----------
    rgb : tuple
        The RGB color as a tuple (R, G, B), each 0-255.
    as_string : bool, optional
        If True, return "#RRGGBB" string; if False, return 0xRRGGBB integer.
        Default is True to reverse hex_to_rgb.

    Returns:
    -------
    str or int
        Hex color code as "#RRGGBB" (if as_string=True) or 0xRRGGBB integer.
    """
    r, g, b = rgb
    color = (r << 16) | (g << 8) | b
    return color

def SetAll_RGB(color):
    print(f"SetAll_RGB color: {color}")
    selectBank(ISSI3745_PAGE0)
    r = (color >> 16) & 0xFF
    g = (color >> 8) & 0xFF
    b = color & 0xFF
    data = [0] * 144
    for i in range(48):
        data[ISSI_LED_MAP[0][i] - 1] = r  # Red
        data[ISSI_LED_MAP[1][i] - 1] = g  # Green
        data[ISSI_LED_MAP[2][i] - 1] = b  # Blue
    print(f"data: {data}")
    writeBuff(1, data, 144)

# Functions from:
# https://github.com/Fattoresaimon/ArduinoDuPPaLib/blob/master/examples/RGB%20LED%20Ring/LEDRing_Demo/LEDRing_Demo.ino

def setup():
    Reset()
    sleep_ms(40)
    ClearAll()
    Configuration(0x01) # Normal operation
    SpreadSpectrum(0b0010110)
    GlobalCurrent(0xFf) # maximum current output
    SetScalingAll(0xFF)
    PWM_MODE()
    ClearAll()


setup()

print(len(["ISSI_LED_MAP"][0]))

# Set_RGB(40, 0x10)
SetAll_RGB(rgb_to_hex((255, 255, 0)))

sleep_ms(1000)
ClearAll()

Set_RGB(0, rgb_to_hex((128, 128, 0)))
Set_RGB(11, rgb_to_hex((128, 128, 0)))
Set_RGB(23, rgb_to_hex((128, 128, 0)))
Set_RGB(35, rgb_to_hex((128, 128, 0)))

sleep_ms(1000)
ClearAll()
