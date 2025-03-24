"""
MicroPython Tesla Coil Controller (MPTCC)
by Cameron Prince
teslauniverse.com

hardware/profiles/mptcc_1.py
Hardware profile for MPTCC 1.
"""

CONFIG = {
    "NUMBER_OF_COILS": 4,
    "RGB_LED_ASYNCIO_POLLING": False,
    "PIN_I2C_1_SCL": 17,
    "PIN_I2C_1_SDA": 16,
    "I2C_1_INTERFACE": 0,
    "I2C_1_FREQ": 400000,
    "I2C_1_TIMEOUT": 50000,
    "CONFIG_PATH": "/mptcc/config.json",
    "SD_CARD_READER_SPI_INSTANCE": 1,
    "SD_CARD_READER_MOUNT_POINT": "/sd",
    "PIN_BATT_STATUS_ADC": 28,
    "VOLTAGE_DROP_FACTOR": 848.5,
    "PIN_MIDI_INPUT": 13,
    "UART_INTERFACE": 0,
    "UART_BAUD": 31250,
    "SPI_1_INTERFACE": 0,
    "SPI_1_BAUD": 1000000,
    "PIN_SPI_1_SCK": 2,
    "PIN_SPI_1_MOSI": 3,
    "PIN_SPI_1_MISO": 4,
    "PIN_SPI_1_CS": 5,
    "PRIMARY_DISPLAY_WIDTH": 128,
    "PRIMARY_DISPLAY_HEIGHT": 64,
    "PRIMARY_DISPLAY_LINE_HEIGHT": 12,
    "PRIMARY_DISPLAY_FONT_WIDTH": 8,
    "PRIMARY_DISPLAY_FONT_HEIGHT": 8,
    "PRIMARY_DISPLAY_HEADER_HEIGHT": 10,
    "PRIMARY_DISPLAY_ITEMS_PER_PAGE": 4,
}

DRIVERS = {
    "display": {
        "ssd1306": {
            "class": "SSD1306",
            "instances": [
                {
                    "enabled": True,
                    "i2c_instance": 1,
                    "i2c_addr": 0x3C,
                    "spi_instance": None,
                    "external_vcc": False,
                    "width": 128,
                    "height": 64,
                    "line_height": 12,
                    "font_width": 8,
                    "font_height": 8,
                    "header_height": 10,
                    "items_per_page": 4,
                },
            ],

        },
    },
    "input": {
        "encoder": {
            "ky_040": {
                "class": "KY040",
                "instances": [
                    {
                        "enabled": True,
                        "pins": [
                            [14, 12, 15], # CLK, DT, SW
                            [10, 9, 11],
                            [21, 22, 20],
                            [27, 0, 26],
                        ],
                        "pull_up": False,
                    },
                ],
            },
            "i2cencoder": {
                "class": "I2CEncoder",
                "instances": [
                    {
                        "enabled": True,
                        "i2c_instance": 1,
                        "i2c_addrs": [0x50, 0x30, 0x60, 0x44],
                        "interrupt_pin": 18,
                        "type": "rgb",
                        "default_color": "#FFFFFF",
                        "threshold_brightness": 32,
                        "full_brightness": 255,
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
                    "pins": [1, 8, 7, 6],
                },
            ],
        },
        "gpio_pio": {
            "class": "GPIO_PIO",
            "instances": [
                {
                    "enabled": False,
                    "pins": [1, 8, 7, 6],
                },
            ],
        },
        "gpio_bitbang": {
            "class": "GPIO_BitBang",
            "instances": [
                {
                    "enabled": False,
                    "pins": [1, 8, 7, 6],
                },
            ],
        },
        "gpio_timer": {
            "class": "GPIO_Timer",
            "instances": [
                {
                    "enabled": False,
                    "pins": [1, 8, 7, 6],
                },
            ],
        },
        "pcf8574_relay": {
            "class": "PCF8574_Relay",
            "instances": [
                {
                    "enabled": False,
                    "i2c_instance": 1,
                    "i2c_addr": 0x27,
                    "pins": [0, 1, 2, 3],
                    "threshold": 40,
                },
            ],
        },
    },
    "rgb_led": {
        "neopixel": {
            "class": "NeoPixel",
            "common_cfg": {
                "segments": 4,
                "reverse": True,
                "default_color": "#FFFFFF",
                "threshold_brightness": 16,
                "full_brightness": 255,
            },
            "instances": [
                {
                    "enabled": False,
                    "pin": 18,
                },
                {
                    "enabled": True,
                    "pin": 19,
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