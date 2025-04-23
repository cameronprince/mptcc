"""
MicroPython Tesla Coil Controller (MPTCC)
by Cameron Prince
teslauniverse.com

hardware/profiles/mptcc_6.py
Hardware profile for MPTCC 6.
"""

CONFIG = {
    "OPERATING_FREQ": 150000000, # RP2350 default 150MHz.
    "NUMBER_OF_COILS": 2,
    "PIN_I2C_1_SCL": 15,
    "PIN_I2C_1_SDA": 14,
    "I2C_1_INTERFACE": 1,
    "I2C_1_FREQ": 400000,
    "I2C_1_TIMEOUT": 50000,
    "CONFIG_PATH": "/mptcc/config.json",
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
                            [6, 7, None], # CLK, DT, SW
                            [8, 9, None],
                        ],
                        "pull_up": False,
                    },
                ],
            },
        },
        "switch": {
            "switch_gpio": {
                "class": "Switch_GPIO",
                "instances": [
                    {
                        "pins": [17, 18, 19, 20, 16, 21],
                        "pull_up": True,
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
                    "pins": [12, 13],
                },
            ],
        },
    },
    "rgb_led": {
        "gpio": {
            "class": "GPIO_RGBLED",
            "enabled": True,
            "instances": [
                {
                    "pins": [
                        [12, 10, None],
                        [1, 0, None],
                    ],
                },
            ],
        },
        "neopixel": {
            "class": "GPIO_NeoPixel",
            "common_cfg": {
                "segments": 4,
                "reverse": True,
                "default_color": "#FFFFFF",
                "threshold_brightness": 4,
                "full_brightness": 80,
            },
            "instances": [
                {
                    "enabled": True,
                    "pin": 11,
                },
            ],
        },
    },
    "other": {
        "sd_card_reader": {
            "class": "SDCardReader",
            "instances": [
                {
                    "enabled": True,
                    "spi_instance": 1,
                    "mount_point": "/sd",
                },
            ],
        },
        "beep": {
            "class": "GPIO_Beep",
            "instances": [
                {
                    "enabled": True,
                    "pin": 13,
                    "length_ms": 25,
                    "volume": 100,
                    "pwm_freq": 3000,
                },
            ],
        },
    },
}


class Profile:
    def __init__(self, name, init):
        # Set the operating frequency.
        from machine import freq
        freq(CONFIG["OPERATING_FREQ"])
        print(f"Operating frequency set to {(int(CONFIG["OPERATING_FREQ"] / 1000000))}MHz")
        # Load all drivers.
        init.load_drivers(CONFIG, DRIVERS);
        print(f"Profile ({name}) loading complete")
        init.memory_usage()
# END