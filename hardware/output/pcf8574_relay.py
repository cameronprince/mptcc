"""
MicroPython Tesla Coil Controller (MPTCC)
by Cameron Prince
teslauniverse.com

hardware/output/pcf8574_relay.py
Class for driving outputs with a relay board connected via PCF8574.
"""

from machine import Pin
from ...hardware.init import init
from ..output.output import Output


class Output_PCF8574_Relay(Output):
    """
    A class to wrap a single relay output and provide control.
    """
    def __init__(self, i2c, i2c_addr, pin_mask, threshold, mutex):
        """
        Initialize the Output_PCF8574_Relay instance.

        Parameters:
        ----------
        i2c : machine.I2C
            The I2C bus connected to the PCF8574.
        i2c_addr : int
            The I2C address of the PCF8574.
        pin_mask : int
            The bitmask for the specific relay pin (e.g., 0x01 for Pin 0).
        threshold : int
            The minimum on-time (in microseconds) required to trigger the relay.
        mutex : _thread.Lock
            The mutex for I2C communication.
        """
        self.i2c = i2c
        self.i2c_addr = i2c_addr
        self.pin_mask = pin_mask
        self.threshold = threshold
        self.mutex = mutex
        self.init = init

        # Initialize the relay to the off state.
        self._set_relay(False)

    def set_output(self, active=False, freq=None, on_time=None):
        """
        Sets the relay output based on the provided parameters.

        Parameters:
        ----------
        active : bool, optional
            Whether the relay should be active.
        freq : int, optional
            The frequency of the output signal (ignored for relays).
        on_time : int, optional
            The on time of the output signal in microseconds.
        """
        if active:
            # Ignore if on_time is below the threshold.
            if on_time is None or on_time < self.threshold:
                return
            self._set_relay(True)
        else:
            self._set_relay(False)

    def _set_relay(self, state):
        """
        Internal method to set the relay state.

        Parameters:
        ----------
        state : bool
            The desired state of the relay (True = on, False = off).
        """
        # Acquire the mutex for I2C communication.
        self.init.mutex_acquire(self.mutex, "Output_PCF8574_Relay:_set_relay")
        try:
            # Read the current state of all pins.
            current_state = self.i2c.readfrom(self.i2c_addr, 1)[0]

            # Toggle the specific pin (inverted logic for active-low relays).
            if state:
                new_state = current_state & ~self.pin_mask  # Set the bit to 0 to turn on.
            else:
                new_state = current_state | self.pin_mask   # Set the bit to 1 to turn off.

            # Write the new state back to the PCF8574.
            self.i2c.writeto(self.i2c_addr, bytes([new_state]))
        except Exception as e:
            print(f"Error setting relay state: {e}")
        finally:
            # Release the mutex.
            self.init.mutex_release(self.mutex, "Output_PCF8574_Relay:_set_relay")


class PCF8574_Relay():
    def __init__(self, i2c_instance, i2c_addr, pins, threshold=100):
        """
        Initialize the PCF8574_Relay driver.

        Parameters:
        ----------
        i2c_instance : int
            The I2C instance to use (1 or 2).
        i2c_addr : int
            The I2C address of the PCF8574.
        pins : list of int
            A list of relay pin numbers (0-7).
        threshold : int, optional
            The minimum on-time (in microseconds) required to trigger the relay.
        """
        super().__init__()
        self.init = init
        self.pins = pins
        self.instances = []

        # Prepare the I2C bus.
        if i2c_instance == 2:
            self.init.init_i2c_2()
            self.i2c = self.init.i2c_2
            self.mutex = self.init.i2c_2_mutex
        else:
            self.init.init_i2c_1()
            self.i2c = self.init.i2c_1
            self.mutex = self.init.i2c_1_mutex

        # Define pin masks for each relay pin.
        self.pin_masks = [0x01 << pin for pin in self.pins]

        # Initialize Output_PCF8574_Relay instances for the provided pins.
        self.instances = [
            Output_PCF8574_Relay(self.i2c, i2c_addr, pin_mask, threshold, self.mutex)
            for pin_mask in self.pin_masks
        ]

        # Initialize all pins to the off state.
        self._initialize_relays()

        # Assign this instance to the next available key.
        instance_key = len(self.init.output_instances['pcf8574_relay'])

        # Print initialization details.
        print(f"PCF8574_Relay driver {instance_key} initialized")
        for i, pin in enumerate(self.pins):
            print(f"- Output {i}: Relay Pin {pin} (Mask: {hex(self.pin_masks[i])})")

    def _initialize_relays(self):
        """
        Initialize all relays to the off state.
        """
        # Acquire the mutex for I2C communication.
        self.init.mutex_acquire(self.mutex, "PCF8574_Relay:_initialize_relays")
        try:
            # Write 0xFF to the PCF8574 to turn off all relays (active-low logic).
            self.i2c.writeto(self.i2c_addr, bytes([0xFF]))
        except Exception as e:
            print(f"Error initializing relays: {e}")
        finally:
            # Release the mutex.
            self.init.mutex_release(self.mutex, "PCF8574_Relay:_initialize_relays")
