"""
MicroPython Tesla Coil Controller (MPTCC)
by Cameron Prince
teslauniverse.com

hardware/profiles/mptcc_8.py
Hardware profile for MPTCC 8.
"""

CONFIG = {
    "OPERATING_FREQ": 150000000, # RP2350 default 150MHz.
    "NUMBER_OF_COILS": 4,

    "CONFIG_PATH": "/mptcc/config.json",
    "PIN_BATT_STATUS_ADC": 28,
    "VOLTAGE_DROP_FACTOR": 848.5,
    "PIN_MIDI_INPUT": 1,
    "UART_INTERFACE": 0,
    "UART_BAUD": 31250,
    "PIN_I2C_2_SCL": 19,
    "PIN_I2C_2_SDA": 18,
    "I2C_2_INTERFACE": 1,
    "I2C_2_FREQ": 400000,
    "I2C_2_TIMEOUT": 50000,
    "SPI_1_INTERFACE": 0,
    "SPI_1_BAUD": 1000000,
    "PIN_SPI_1_SCK": 2,
    "PIN_SPI_1_MOSI": 3,
    "PIN_SPI_1_MISO": 4,
    "PIN_SPI_1_CS": 5,
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
                "enabled": True,
                "instances": [
                    {
                        "enabled": True,
                        "i2c_instance": 2,
                        "i2c_addrs": [0x50, 0x30, 0x60, 0x44],
                        "interrupt_pin": 0,
                        "type": "rgb",
                        "default_color": "#FFFF00",
                        "threshold_brightness": 32,
                        "full_brightness": 255,
                        "asyncio_polling": True,
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
                    "pins": [20, 21, 22, 26],
                },
            ],
        },
    },
    "rgb_led": {
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
                    "pin": 6,
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
                    "pin": 1,
                    "length_ms": 1,
                    "volume": 50,
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