"""
MicroPython Tesla Coil Controller (MPTCC)
by Cameron Prince
teslauniverse.com

hardware/profiles/mptcc_3.py
Hardware profile for MPTCC 3.
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
    "universal": {
        "wombat_18ab": {
        "class": "Wombat_18AB",
            "instances": [
                {
                    "enabled": True,
                    "i2c_instance": 1,
                    "init_delay": 0.2,
                    "i2c_addr": 0x6B,
                    "switch": {
                        "pins": [1, 0, 14, 10],
                        "pull_up": False,
                        "pulse_on_change_pin": 5,
                        "host_interrupt_pin": 14,
                        "host_interrupt_pin_pull_up": True,
                    },
                    "encoder": {
                        "pins": [
                            [13, 12],
                            [15, 11],
                            [17, 16],
                            [19, 18],
                        ],
                        "pull_up": False,
                        "pulse_on_change_pin": 6,
                        "host_interrupt_pin": 15,
                        "host_interrupt_pin_pull_up": True,
                    },
                },
            ],
        },
    },
    "output": {
        "gpio_pwm": {
            "class": "GPIO_PWM",
            "instances": [
                {
                    "enabled": True,
                    "pins": [9, 8, 7, 6],
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
                "default_color": "#00FFFF",
                "threshold_brightness": 16,
                "full_brightness": 255,
            },
            "instances": [
                {
                    "enabled": True,
                    "pin": 13,
                },
                {
                    "enabled": True,
                    "pin": 12,
                },
                {
                    "enabled": True,
                    "pin": 11,
                },
                {
                    "enabled": True,
                    "pin": 10,
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