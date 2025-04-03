"""
MicroPython Tesla Coil Controller (MPTCC)
by Cameron Prince
teslauniverse.com

init.py
Carries configuration and initialized hardware between classes.
"""

import _thread
import time
from machine import Pin
from ..lib.asyncio import AsyncIOLoop
from .manager import DisplayManager, RGBLEDManager, OutputManager
import gc


class Init:
    """
    A class to carry configuration and initialized hardware between
    classes for the MicroPython Tesla Coil Controller (MPTCC).
    """

    def __init__(self):
        """
        Constructs all the necessary attributes for the Init object.
        """
        self.i2c_1 = None
        self.i2c_2 = None
        self.spi_1 = None
        self.spi_2 = None
        self.uart = None

        self.menu = None
        self.ignore_input = False

    def load_drivers(self, config, drivers):
        """
        Load drivers in a specific order.

        Parameters:
        ----------
        config : dict
            A dictionary of config to be added to the init object.
        drivers : dict
            A dictionary of driver configurations.
        """
        # Handle config.
        for key, value in config.items():
            setattr(self, key, value)

        # Define the order in which drivers should be loaded.
        order = ["display", "input", "output", "rgb_led", "universal", "other"]

        # Create the driver objects in init.
        for driver in order:
            setattr(self, driver, {})
            setattr(self, f"{driver}_instances", {})

        # Load drivers in the specified order.
        for driver_type in order:
            if driver_type in drivers:
                driver_dict = drivers[driver_type]
                self._load_driver_type(driver_type, driver_dict)

        # Initialize the hardware managers.
        self.display = DisplayManager(self)
        self.rgb_led = RGBLEDManager(self)
        self.output = OutputManager(self)

        # Initialize the asyncio loop.
        self.asyncio = AsyncIOLoop()

    def _load_driver_type(self, driver_type, driver_dict):
        """
        Load drivers of a specific type.

        Parameters:
        ----------
        driver_type : str
            The type of driver (e.g., "display", "input").
        driver_dict : dict
            A dictionary of driver configurations for the specified type.
        """
        instance_storage = getattr(self, f"{driver_type}_instances")

        # Load drivers for this type.
        for driver_name, driver_details in driver_dict.items():
            if driver_details.get('enabled', True):
                self._load_driver(driver_type, driver_name, driver_details, instance_storage)

    def _load_driver(self, driver_type, driver_name, driver_details, instance_storage):
        """
        Load a driver and its nested drivers.

        Parameters:
        ----------
        driver_type : str
            The type of driver (e.g., "display", "input").
        driver_name : str
            The name of the driver (e.g., "ssd1306", "encoder").
        driver_details : dict
            The configuration details for the driver.
        instance_storage : dict
            The dictionary to store driver instances.
        """
        if isinstance(driver_details, dict) and "class" not in driver_details:
            # Handle nested driver configurations (e.g., input > encoder > i2cencoder).
            for nested_driver_name, nested_driver_details in driver_details.items():
                # Ensure the nested dictionary exists.
                if driver_name not in instance_storage:
                    instance_storage[driver_name] = {}

                # Recursively load the nested driver.
                self._load_driver(driver_type, nested_driver_name, nested_driver_details, instance_storage[driver_name])
        else:
            if "class" not in driver_details:
                return

            # Initialize a single driver instance.
            self._initialize_driver_instance(driver_type, driver_name, driver_details, instance_storage)

    def _initialize_driver_instance(self, driver_type, driver_name, driver_details, instance_storage):
        """
        Initialize a single driver instance and store it in the init object.

        Parameters:
        ----------
        driver_type : str
            The type of driver (e.g., "display", "input").
        driver_name : str
            The name of the driver (e.g., "ssd1306", "i2cencoder").
        driver_details : dict
            The configuration details for the driver.
        instance_storage : dict
            The dictionary to store driver instances.
        """
        class_name = driver_details["class"]

        # Construct the module path dynamically.
        if "." in driver_name:
            # For nested drivers, skip the intermediate level.
            nested_driver_name = driver_name.split(".")[-1]
            module_path = f"mptcc.hardware.{driver_type}.{nested_driver_name}"
        else:
            # For flat drivers, use the driver_name directly.
            module_path = f"mptcc.hardware.{driver_type}.{driver_name}"

        # Dynamically import the module.
        module = __import__(module_path, None, None, [class_name])

        # Get the driver class.
        driver_class = getattr(module, class_name)

        # Check if there's a common configuration (optional).
        common_cfg = driver_details.get("common_cfg", None)

        # Initialize instances.
        instance_storage[driver_name] = []
        for instance_config in driver_details["instances"]:

            if not instance_config.get("enabled", True):
                continue

            # If common_cfg exists, merge it with instance_config.
            if common_cfg is not None:
                merged_config = common_cfg.copy()  # Create a copy of common_cfg.
                merged_config.update(instance_config)  # Update with instance-specific config.
            else:
                merged_config = instance_config  # Use instance_config as-is.

            # Remove the "enabled" attribute since it's not needed by the drivers.
            merged_config.pop("enabled", None)

            # Create an instance of the driver class.
            instance = driver_class(**merged_config)

            # If the driver has an `instances` attribute, store it as a nested list.
            if hasattr(instance, "instances"):
                instance_storage[driver_name].append(instance.instances)
            else:
                instance_storage[driver_name].append(instance)

            if hasattr(self, "DEBUG_MEMORY") and self.DEBUG_MEMORY:
                self.memory_usage()

    def validate_settings(self):
        """
        Validates the NUMBER_OF_COILS variable and ensures the total number of outputs
        across all drivers matches NUMBER_OF_COILS.

        Raises:
        -------
        ValueError
            If the constraints are not met.
        """
        # Ensure NUMBER_OF_COILS is at least 4.
        if self.NUMBER_OF_COILS < 4:
            raise ValueError("NUMBER_OF_COILS must be at least 4. The program will now exit.")

        # Check if the number of coils is greater than 4.
        if self.NUMBER_OF_COILS > 4:
            if self.display.DISPLAY_WIDTH < 256:
                raise ValueError("For more than 4 coils, the display width must be at least 256 pixels. The program will now exit.")

        # Check if the number of coils is greater than 8.
        if self.NUMBER_OF_COILS > 8:
            raise ValueError("The maximum number of supported coils is currently 8. The program will now exit.")

        # Ensure self.output exists.
        if not hasattr(self, "output"):
            raise ValueError("No output drivers initialized. The program will now exit.")

        # Validate that each driver's output list matches NUMBER_OF_COILS.
        for driver_key, instance_dict in self.output.items():
            for instance_key, driver_instance in instance_dict.items():
                # Check if the driver_instance is a list of outputs.
                if isinstance(driver_instance, list):
                    if len(driver_instance) != self.NUMBER_OF_COILS:
                        raise ValueError(
                            f"Driver {driver_key}[{instance_key}] has {len(driver_instance)} outputs, "
                            f"but NUMBER_OF_COILS is {self.NUMBER_OF_COILS}. The program will now exit."
                        )
                # Alternatively, if the driver_instance is an object with an 'output' attribute.
                elif hasattr(driver_instance, "output") and isinstance(driver_instance.output, list):
                    if len(driver_instance.output) != self.NUMBER_OF_COILS:
                        raise ValueError(
                            f"Driver {driver_key}[{instance_key}] has {len(driver_instance.output)} outputs, "
                            f"but NUMBER_OF_COILS is {self.NUMBER_OF_COILS}. The program will now exit."
                        )
                else:
                    raise ValueError(
                        f"Driver {driver_key}[{instance_key}] does not have a valid output list. "
                        "The program will now exit."
                    )

        # Count the total number of outputs across all drivers.
        total_outputs = 0
        for driver_key, instance_dict in self.output.items():
            for instance_key, driver_instance in instance_dict.items():
                # Check if the driver_instance is a list of outputs.
                if isinstance(driver_instance, list):
                    total_outputs += len(driver_instance)
                # Alternatively, if the driver_instance is an object with an 'output' attribute.
                elif hasattr(driver_instance, "output") and isinstance(driver_instance.output, list):
                    total_outputs += len(driver_instance.output)

        # Ensure there are at least 4 outputs.
        if total_outputs < 4:
            raise ValueError(f"Total number of outputs ({total_outputs}) is less than 4. The program will now exit.")

    def init_i2c_1(self):
        """
        Initializes the first I2C bus.
        """
        from machine import I2C
        if not isinstance(self.i2c_1, I2C):
            self.i2c_1 = I2C(
                self.I2C_1_INTERFACE,
                scl=Pin(self.PIN_I2C_1_SCL),
                sda=Pin(self.PIN_I2C_1_SDA),
                freq=self.I2C_1_FREQ,
                timeout=self.I2C_1_TIMEOUT,
            )
        # Add a mutex for I2C communication to the init object.
        if not hasattr(self, "i2c_1_mutex"):
            self.i2c_1_mutex = _thread.allocate_lock()

    def init_i2c_2(self):
        """
        Initializes the second I2C bus.
        """
        from machine import I2C
        if not isinstance(self.i2c_2, I2C):
            self.i2c_2 = I2C(
                self.I2C_2_INTERFACE,
                scl=Pin(self.PIN_I2C_2_SCL),
                sda=Pin(self.PIN_I2C_2_SDA),
                freq=self.I2C_2_FREQ,
                timeout=self.I2C_2_TIMEOUT,
            )
        # Add a mutex for I2C communication to the init object.
        if not hasattr(self, "i2c_2_mutex"):
            self.i2c_2_mutex = _thread.allocate_lock()

    def init_spi_1(self):
        """
        Initializes the first SPI bus.
        """
        from machine import SPI
        if isinstance(self.spi_1, SPI):
            self.spi_1.deinit()
        miso = None
        if self.PIN_SPI_1_MISO is not None:
            miso = Pin(self.PIN_SPI_1_MISO)
        self.spi_1 = SPI(
            self.SPI_1_INTERFACE,
            baudrate=self.SPI_1_BAUD,
            polarity=0,
            phase=0,
            sck=Pin(self.PIN_SPI_1_SCK),
            mosi=Pin(self.PIN_SPI_1_MOSI),
            miso=miso,
        )

    def init_spi_2(self):
        """
        Initializes the second SPI bus.
        """
        from machine import SPI
        if isinstance(self.spi_2, SPI):
            self.spi_2.deinit()
        miso = None
        if self.PIN_SPI_2_MISO is not None:
            miso = Pin(self.PIN_SPI_2_MISO)
        self.spi_2 = SPI(
            self.SPI_2_INTERFACE,
            baudrate=self.SPI_2_BAUD,
            polarity=0,
            phase=0,
            sck=Pin(self.PIN_SPI_2_SCK),
            mosi=Pin(self.PIN_SPI_2_MOSI),
            miso=miso,
        )

    def init_uart(self):
        """
        Initializes the UART for MIDI input.
        """
        from machine import UART
        self.uart = UART(
            self.UART_INTERFACE,
            baudrate=self.UART_BAUD,
            rx=Pin(self.PIN_MIDI_INPUT),
        )

    def mutex_acquire(self, mutex, src):
        """
        Acquires a mutex and provides a common function for debugging.
        """
        if hasattr(self, "DEBUG_MUTEX") and self.DEBUG_MUTEX:
            print("mutex_acquire:", src)
        mutex.acquire()

    def mutex_release(self, mutex, src):
        """
        Releases a mutex and provides a common function for debugging.
        """
        if hasattr(self, "DEBUG_MUTEX") and self.DEBUG_MUTEX:
            print("mutex_release:", src)
        mutex.release()

    def memory_usage(self):
        # Display memory usage.
        free_memory = gc.mem_free()
        print(f"- Free memory: {free_memory} bytes")


init = Init()
