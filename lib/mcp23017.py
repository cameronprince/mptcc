"""
MicroPython Tesla Coil Controller (MPTCC)
by Cameron Prince
teslauniverse.com

lib/mcp23017.py
Shared library for MCP23017 GPIO expander.
"""

class MCP23017:
    # MCP23017 register addresses
    IODIRA = 0x00  # I/O direction register for Port A
    IODIRB = 0x01  # I/O direction register for Port B
    GPINTENA = 0x04  # Interrupt-on-change control register for Port A
    DEFVALA = 0x06  # Default value register for Port A
    INTCONA = 0x08  # Interrupt control register for Port A
    GPPUA = 0x0C  # Pull-up resistor configuration register for Port A
    INTCAPA = 0x10  # Interrupt capture register for Port A
    GPIOA = 0x12  # GPIO register for Port A
    OLATA = 0x14  # Output latch register for Port A
    GPIOB = 0x13  # GPIO register for Port B

    def __init__(self, i2c, address, mutex):
        self.i2c = i2c
        self.address = address
        self.mutex = mutex

    def _read_register(self, reg):
        """
        Read a register from the MCP23017.
        """
        self.mutex.acquire()
        try:
            value = self.i2c.readfrom_mem(self.address, reg, 1)[0]
            return value
        except Exception as e:
            print(f"Error reading register 0x{reg:02X}: {e}")
            return 0
        finally:
            self.mutex.release()

    def _write_register(self, reg, value):
        """
        Write a value to a register on the MCP23017.
        """
        self.mutex.acquire()
        try:
            self.i2c.writeto_mem(self.address, reg, bytearray([value]))
        except Exception as e:
            print(f"Error writing to register 0x{reg:02X}: {e}")
        finally:
            self.mutex.release()

    def configure_pins(self, port, direction, pull_up=None, interrupt=None):
        """
        Configure pins on the MCP23017.
        :param port: 'A' or 'B' for Port A or Port B
        :param direction: 0 for output, 1 for input
        :param pull_up: 1 to enable pull-up, 0 to disable (optional)
        :param interrupt: 1 to enable interrupt, 0 to disable (optional)
        """
        if port == 'A':
            iodir_reg = self.IODIRA
            gppu_reg = self.GPPUA
            gpinten_reg = self.GPINTENA
        elif port == 'B':
            iodir_reg = self.IODIRB
            gppu_reg = 0x0D  # GPPUB register
            gpinten_reg = 0x05  # GPINTENB register
        else:
            raise ValueError("Invalid port. Use 'A' or 'B'.")

        # Set pin direction
        self._write_register(iodir_reg, direction)

        # Enable pull-up resistors if specified
        if pull_up is not None:
            self._write_register(gppu_reg, pull_up)

        # Enable interrupts if specified
        if interrupt is not None:
            self._write_register(gpinten_reg, interrupt)

    def read_port(self, port):
        """
        Read the value of a port.
        :param port: 'A' or 'B' for Port A or Port B
        :return: The value of the port
        """
        if port == 'A':
            return self._read_register(self.GPIOA)
        elif port == 'B':
            return self._read_register(self.GPIOB)
        else:
            raise ValueError("Invalid port. Use 'A' or 'B'.")

    def write_port(self, port, value):
        """
        Write a value to a port.
        :param port: 'A' or 'B' for Port A or Port B
        :param value: The value to write
        """
        if port == 'A':
            self._write_register(self.GPIOA, value)
        elif port == 'B':
            self._write_register(self.GPIOB, value)
        else:
            raise ValueError("Invalid port. Use 'A' or 'B'.")