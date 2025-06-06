"""
MicroPython Tesla Coil Controller (MPTCC)
by Cameron Prince
teslauniverse.com

hardware/profiles/mptcc_4.py
Hardware profile for MPTCC 4.
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
                {
                    "enabled": True,
                    "i2c_instance": 1,
                    "i2c_addr": 0x3D,
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
                        "interrupt_pin": 18,
                        "type": "rgb",
                        "default_color": "#FFFF00",
                        "threshold_brightness": 32,
                        "full_brightness": 255,
                    },
                ],
            },
        },
        "switch": {
            "switch_gpio": {
                "class": "Switch_GPIO",
                "enabled": False,
                "instances": [
                    {
                        "enabled": False,
                        "pins": [15, 14, 9, 8, 7, 6],
                        "pull_up": True,
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
                    "pins": [13, 12, 11, 10],
                },
            ],
        },
    },
    "rgb_led": {
        "neopixel": {
            "class": "GPIO_NeoPixel",
            "enabled": True,
            "common_cfg": {
                "segments": 4,
                "reverse": True,
                "default_color": "#FFFF00",
                "threshold_brightness": 16,
                "full_brightness": 255,
            },
            "instances": [
                {
                    "enabled": True,
                    "pin": 21,
                },
                {
                    "enabled": True,
                    "pin": 22,
                },
                {
                    "enabled": True,
                    "pin": 15,
                    "segments": 64,
                    "rotation": 0,
                    "reverse": False,    # The first LED becomes the last LED when True.
                    "invert": True,
                    "mode": "vu_meter",
                    "matrix": "8x8",
                },
            ],
        },
        "pca9685": {
            "class": "PCA9685_RGBLED",
            "enabled": False,
            "instances": [
                {
                    "enabled": False,
                    "i2c_instance": 1,
                    "i2c_addr": 0x40,
                    "freq": 1000,
                    "pins": [
                        [14, 15, None],
                        [12, 13, None],
                        [10, 11, None],
                        [8, 9, None],
                    ],
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