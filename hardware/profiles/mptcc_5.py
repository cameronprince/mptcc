"""
MicroPython Tesla Coil Controller (MPTCC)
by Cameron Prince
teslauniverse.com

hardware/profiles/mptcc_5.py
Hardware profile for MPTCC 5.
"""

CONFIG = {
    "NUMBER_OF_COILS": 4,
    "PIN_I2C_1_SCL": 17,
    "PIN_I2C_1_SDA": 16,
    "I2C_1_INTERFACE": 0,
    "I2C_1_FREQ": 400000,
    "I2C_1_TIMEOUT": 50000,
    "CONFIG_PATH": "/mptcc/config.json",
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
    "PRIMARY_DISPLAY_WIDTH": 128,
    "PRIMARY_DISPLAY_HEIGHT": 64,
    "PRIMARY_DISPLAY_LINE_HEIGHT": 12,
    "PRIMARY_DISPLAY_FONT_WIDTH": 8,
    "PRIMARY_DISPLAY_FONT_HEIGHT": 8,
    "PRIMARY_DISPLAY_HEADER_HEIGHT": 10,
    "PRIMARY_DISPLAY_ITEMS_PER_PAGE": 4,
    "MASTER_DEFAULT_POSITION": 50,
}

DRIVERS = {
    "display": {
        "ssd1306": {
            "class": "SSD1306",
            "enabled": True,
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
            "i2cencoder": {
                "class": "I2CEncoder",
                "enabled": True,
                "instances": [
                    {
                        "enabled": True,
                        "i2c_instance": 1,
                        "i2c_addrs": [0x50, 0x30, 0x60, 0x44],
                        "interrupt_pin": 0,
                        "type": "rgb",
                        "default_color": "#00FFFF",
                        "threshold_brightness": 12,
                        "full_brightness": 120,
                    },
                ],
            },
            "i2cencoder_mini": {
                "class": "I2CEncoderMini",
                "instances": [
                    {
                        "i2c_instance": 1,
                        "i2c_addrs": [0x21],
                        "interrupt_pin": 27,
                        "master": True,
                    },
                ],
            },

        },
    },
    "output": {
        "gpio_pwm": {
            "class": "GPIO_PWM",
            "enabled": True,
            "instances": [
                {
                    "enabled": True,
                    "pins": [6, 7, 8, 9],
                },
            ],
        },
    },
    "rgb_led": {
        "rgb_led_ring": {
            "class": "RGBLEDRing",
            "instances": [
                {
                    "i2c_instance": 1,
                    "master": True,
                    "i2c_addrs": [0x20],
                    "asyncio_polling": True,
                    "default_color": "vu_meter", # Hex code or "vu_meter".
                    "threshold_brightness": 2,
                    "full_brightness": 40,
                    "offset": -2,
                    "reverse": True,
                    "delay_between_steps": 0, # 0.005 is nice, but it does delay playback timing.
                    "mode": "vu_meter", # Either "status" or "vu_meter".
                    "vu_meter_sensitivity": 1,
                    "vu_meter_colors": [
                        [0, 255, 0],      # LED 1
                        [0, 255, 0],     # LED 2
                        [0, 255, 0],     # LED 3
                        [0, 255, 0],     # LED 4
                        [0, 255, 0],     # LED 5
                        [0, 255, 0],     # LED 6
                        [0, 255, 0],     # LED 7
                        [0, 255, 0],     # LED 8
                        [0, 255, 0],    # LED 9
                        [0, 255, 0],    # LED 10
                        [0, 255, 0],    # LED 11
                        [0, 255, 0],    # LED 12
                        [0, 255, 0],    # LED 13
                        [0, 255, 0],    # LED 14
                        [0, 255, 0],    # LED 15
                        [0, 255, 0],    # LED 16
                        [0, 255, 0],    # LED 17
                        [0, 255, 0],    # LED 18
                        [0, 255, 0],    # LED 19
                        [0, 255, 0],    # LED 20
                        [0, 255, 0],    # LED 21
                        [0, 255, 0],    # LED 22
                        [0, 255, 0],    # LED 23
                        [0, 255, 0],    # LED 24
                        [0, 255, 0],    # LED 25
                        [0, 255, 0],    # LED 26
                        [0, 255, 0],    # LED 27
                        [0, 255, 0],    # LED 28
                        [255, 255, 0],    # LED 29
                        [255, 255, 0],    # LED 30
                        [255, 255, 0],    # LED 31
                        [255, 255, 0],    # LED 32
                        [255, 255, 0],    # LED 33
                        [255, 255, 0],    # LED 34
                        [255, 255, 0],    # LED 35
                        [255, 255, 0],    # LED 36
                        [255, 102, 0],    # LED 37
                        [255, 102, 0],     # LED 38
                        [255, 102, 0],     # LED 39
                        [255, 102, 0],     # LED 40
                        [255, 102, 0],     # LED 41
                        [255, 102, 0],     # LED 42
                        [255, 0, 0],     # LED 43
                        [255, 0, 0],     # LED 44
                        [255, 0, 0],     # LED 45
                        [255, 0, 0],     # LED 46
                        [255, 0, 0],      # LED 47
                        [255, 0, 0]       # LED 48
                    ],
                },
            ],
        },
        "neopixel": {
            "class": "GPIO_NeoPixel",
            "enabled": True,
            "common_cfg": {
                "segments": 4,
                "reverse": True,
                "default_color": "#00FFFF",
                "threshold_brightness": 12,
                "full_brightness": 100,
            },
            "instances": [
                {
                    "enabled": True,
                    "pin": 14,
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
                    "pin": 15,
                    "length_ms": 5,
                    "volume": 100,
                    "pwm_freq": 3000,
                },
            ],
        },
    },
}

class Profile:
    def __init__(self, name, init):
        from machine import freq
        freq(125000000)

        init.load_drivers(CONFIG, DRIVERS);
        print(f"Profile ({name}) loading complete")

# END