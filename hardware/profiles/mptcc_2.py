"""
MicroPython Tesla Coil Controller (MPTCC)
by Cameron Prince
teslauniverse.com

hardware/profiles/mptcc_2.py
Hardware profile for MPTCC 2.
"""

CONFIG = {
    "NUMBER_OF_COILS": 8,
    "RGB_LED_ASYNCIO_POLLING": False,
    "PIN_I2C_1_SCL": 17,
    "PIN_I2C_1_SDA": 16,
    "I2C_1_INTERFACE": 0,
    "I2C_1_FREQ": 400000,
    "I2C_1_TIMEOUT": 50000,
    "PIN_I2C_2_SCL": 19,
    "PIN_I2C_2_SDA": 18,
    "I2C_2_INTERFACE": 1,
    "I2C_2_FREQ": 400000,
    "I2C_2_TIMEOUT": 50000,
    "CONFIG_PATH": "/mptcc/config.json",
    "SD_CARD_READER_SPI_INSTANCE": 1,
    "SD_CARD_READER_MOUNT_POINT": "/sd",
    "PIN_BATT_STATUS_ADC": 28,
    "VOLTAGE_DROP_FACTOR": 848.5,
    "PIN_MIDI_INPUT": 1,
    "UART_INTERFACE": 0,
    "UART_BAUD": 31250,
    "SPI_1_INTERFACE": 0,
    "SPI_1_BAUD": 1000000,
    "PIN_SPI_1_SCK": 2,
    "PIN_SPI_1_MOSI": 3,
    "PIN_SPI_1_MISO": 4,
    "PIN_SPI_1_CS": 5,
    "PIN_SPI_1_DC": None,
    "PIN_SPI_1_RST": None,
    "SPI_2_INTERFACE": 1,
    "SPI_2_BAUD": 10000000,
    "PIN_SPI_2_SCK": 10,
    "PIN_SPI_2_MOSI": 11,
    "PIN_SPI_2_MISO": None,
    "PIN_SPI_2_CS": 13,
    "PIN_SPI_2_DC": 12,
    "PIN_SPI_2_RST": 14,
    "PRIMARY_DISPLAY_WIDTH": 256,
    "PRIMARY_DISPLAY_HEIGHT": 64,
    "PRIMARY_DISPLAY_LINE_HEIGHT": 12,
    "PRIMARY_DISPLAY_FONT_WIDTH": 8,
    "PRIMARY_DISPLAY_FONT_HEIGHT": 8,
    "PRIMARY_DISPLAY_HEADER_HEIGHT": 10,
    "PRIMARY_DISPLAY_ITEMS_PER_PAGE": 4,
}

DRIVERS = {
    "display": {
        "ssd1322": {
            "class": "SSD1322",
            "instances": [
                {
                    "enabled": True,
                    "spi_instance": 2,
                },
            ],
        },
    },
    "input": {
        "encoder": {
            "i2cencoder": {
                "class": "I2CEncoder",
                "instances": [
                    {
                        "enabled": True,
                        "i2c_instance": 1,
                        "i2c_addrs": [0x21, 0x22, 0x23, 0x24, 0x25, 0x26, 0x27, 0x28],
                        "interrupt_pin": 20,
                        "type": "mini",
                    },
                ],
            },
        },
    },
    "output": {
        "gpio_pwm": {
            "class": "GPIO_PWM",
            "instances": [
                {
                    "enabled": True,
                    "pins": [27, 26, 15, 21, 9, 8, 7, 6],
                },
            ],
        },
    },
    "rgb_led": {
        "rgb_led_ring_small": {
            "class": "RGBLEDRingSmall",
            "instances": [
                {
                    "i2c_instance": 2,
                    "addresses": [0x6A, 0x68, 0x6B, 0x69, 0x67, 0x66, 0x64, 0x63],
                    "default_color": "#00FFFF", # Hex code or "vu_meter".
                    "threshold_brightness": 16,
                    "full_brightness": 32,
                    "rotation": 180,
                    "delay_between_steps": 0, # 0.005 is nice, but it does delay playback timing.
                    "mode": "vu_meter", # Either "status" or "vu_meter".
                },
            ],
        },
        "neopixel": {
            "class": "GPIO_NeoPixel",
            "common_cfg": {
                "segments": 8,
                "reverse": True,
                "default_color": "#00FFFF",
                "threshold_brightness": 16,
                "full_brightness": 255,
            },
            "instances": [
                {
                    "enabled": False,
                    "pin": 0,
                    "segments": 64,
                    "rotation": 0,
                    "reverse": False,    # The first LED becomes the last LED when True.
                    "invert": True,
                    "mode": "vu_meter",
                    "matrix": "8x8",
                },
                {
                    "enabled": True,
                    "pin": 22,
                },
            ],
        },
    },
}

class Profile:
    def __init__(self, name, init):
        init.load_drivers(CONFIG, DRIVERS);
        print(f"Profile ({name}) loading complete")

# END