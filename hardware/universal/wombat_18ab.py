"""
MicroPython Tesla Coil Controller (MPTCC)
by Cameron Prince
teslauniverse.com

hardware/universal/wombat_18ab.py
Serial Wombat 18AB universal class for driving hardware.
"""

import _thread
import time
import uasyncio as asyncio
from machine import Pin
from ..input.input import Input
from ..output.output import Output
from ..rgb_led.rgb_led import RGB
from ...lib import utils
from ...hardware.init import init
from SerialWombat_mp_i2c import SerialWombatChip_mp_i2c as driver


class Wombat_18AB:
    """
    A class to provide hardware instances using the Serial Wombat 18AB board.
    """
    def __init__(
        self,
        i2c_instance,
        i2c_addr=0x6B,
        encoder=None,
        output=None,
        rgb_led=None,
        switch=None,
    ):
        """
        Constructs all the necessary attributes for the Wombat_18AB object.
        """
        if encoder is None and output is None and rgb_led is None and switch is None:
            return

        super().__init__()
        self.init = init
        self.instances = []
        self.init_complete = [False]

        # Prepare the I2C bus.
        if i2c_instance == 2:
            self.init.init_i2c_2()
            self.i2c = self.init.i2c_2
            self.mutex = self.init.i2c_2_mutex
        else:
            self.init.init_i2c_1()
            self.i2c = self.init.i2c_1
            self.mutex = self.init.i2c_1_mutex

        # Initialize the Wombat 18AB driver.
        self.driver = driver(self.i2c, i2c_addr)

        print(f"Wombat_18AB universal driver initialized")
        print(f"- I2C Address: {hex(i2c_addr)}")

        if rgb_led is not None or output is not None:
            from SerialWombatPWM import SerialWombatPWM_18AB as swpwm

        # Initialize switches if switch is provided.
        if switch is not None:
            from SerialWombatDebouncedInput import SerialWombatDebouncedInput as swdi
            if "wombat_18ab_switch" not in self.init.input_instances:
                self.init.input_instances["wombat_18ab_switch"] = []
            switch_instances = []
            switch_instance = Switch_Wombat_18AB(
                self.init,
                self.driver,
                swdi,
                switch,
                self.mutex,
                self.init_complete,
            )
            switch_instances.append(switch_instance)
            self.init.input_instances["wombat_18ab_switch"].append(switch_instances)
            print(f"- Switches initialized (pull_up={switch.get("pull_up", False)})")
            for i, pin in enumerate(switch.get("pins")):
                print(f"  - Switch {i}: Pin {pin}")
            print(f"  - Pulse on change pin: {switch.get("pulse_on_change_pin")}")
            print(f"  - Host interrupt pin: {switch.get("host_interrupt_pin")} (pull_up={switch.get("host_interrupt_pin_pull_up", False)})")

        # Initialize encoders if encoder is provided.
        if encoder is not None:
            from SerialWombatQuadEnc import SerialWombatQuadEnc as swqe
            if "wombat_18ab_encoder" not in self.init.input_instances:
                self.init.input_instances["wombat_18ab_encoder"] = []
            encoder_instances = []
            encoder_instance = Encoder_Wombat_18AB(
                self.init,
                self.driver,
                swqe,
                encoder,
                self.mutex,
                self.init_complete,
            )
            encoder_instances.append(encoder_instance)
            self.init.input_instances["wombat_18ab_encoder"].append(encoder_instances)
            print(f"- Encoders initialized (pull_up={encoder.get("pull_up", False)})")
            for i, pin in enumerate(encoder.get("pins")):
                pin, secondPin = pin
                print(f"  - Encoder {i}: Pins {pin} and {secondPin}")
            print(f"  - Pulse on change pin: {encoder.get("pulse_on_change_pin")}")
            print(f"  - Host interrupt pin: {encoder.get("host_interrupt_pin")} (pull_up={encoder.get("host_interrupt_pin_pull_up", False)})")

        # Initialize outputs if output is provided.
        if output is not None:
            if "wombat_18ab" not in self.init.output_instances:
                self.init.output_instances["wombat_18ab"] = []
            output_instances = []
            for pin in output_pins:
                output = Output_Wombat_18AB(self.init, self.driver, swpwm, pin, self.mutex)
                output_instances.append(output)
            self.init.output_instances["wombat_18ab"].append(output_instances)
            print(f"- Outputs initialized:")
            for i, pin in enumerate(output_pins):
                print(f"  - Output {i}: Pin {pin}")

        # Initialize RGB LEDs if rgb_led is provided.
        if rgb_led is not None:
            if "wombat_18ab" not in self.init.rgb_led_instances:
                self.init.rgb_led_instances["wombat_18ab"] = []
            rgb_led_instances = []
            for led_pins in rgb_led_pins:
                red_pin, green_pin, blue_pin = led_pins
                led = RGB_Wombat_18AB(
                    init=self.init,
                    driver=self.driver,
                    swpwm=swpwm,
                    red_pin=red_pin,
                    green_pin=green_pin,
                    blue_pin=blue_pin,
                    mutex=self.mutex
                )
                rgb_led_instances.append(led)
            self.init.rgb_led_instances["wombat_18ab"].append(rgb_led_instances)
            print(f"- RGB LEDs initialized:")
            for i, led_pins in enumerate(rgb_led_pins):
                red_pin, green_pin, blue_pin = led_pins
                print(f"  - LED {i}: R={red_pin}, G={green_pin}, B={blue_pin}")

        self.init_complete[0] = True


class Output_Wombat_18AB(Output):
    """
    A class for handling outputs with a Serial Wombat 18AB driver.
    """
    def __init__(self, init, driver, swpwm, pin, mutex):
        """
        Constructs all the necessary attributes for the Output_Wombat_18AB object.

        Parameters:
        ----------
        driver : SerialWombatChip_mp_i2c
            The Serial Wombat driver instance.
        pin : int
            The pin number on the Serial Wombat chip where the output is connected.
        mutex : _thread.Lock
            The mutex for I2C communication.
        """
        self.driver = driver
        self.swpwm = swpwm
        self.pin = pin
        self.mutex = mutex
        self.init = init

        # Initialize the PWM output on the specified pin with a duty cycle of 0 (off).
        self.pwm = self.swpwm(self.driver)
        self.init.mutex_acquire(self.mutex, "Output_Wombat_18AB:init")
        try:
            self.pwm.begin(self.pin, 0)
        except Exception as e:
            print(f"Error initializing PWM on pin {pin}: {e}")
        finally:
            self.init.mutex_release(self.mutex, "Output_Wombat_18AB:init")

    def set_output(self, active=False, freq=None, on_time=None):
        """
        Sets the output based on the provided parameters.

        Parameters:
        ----------
        active : bool, optional
            Whether the output should be active.
        freq : int, optional
            The frequency of the PWM signal in Hz.
        on_time : int, optional
            The on time of the PWM signal in microseconds.
        """
        if active:
            if freq is None or on_time is None:
                raise ValueError("Frequency and on_time must be provided when activating the output.")

            # Calculate the duty cycle based on the on_time and frequency.
            period = 1.0 / freq  # Period in seconds.
            period_us = period * 1e6  # Period in microseconds.
            duty_cycle = int((on_time / period_us) * 0xFFFF)  # Convert to 16-bit duty cycle value.

            # Acquire the mutex for both operations.
            self.init.mutex_acquire(self.mutex, "Output_Wombat_18AB:set_output")
            try:
                # Set the frequency of the PWM signal.
                self.pwm.writeFrequency_Hz(freq)
                # Set the duty cycle.
                self.pwm.writeDutyCycle(duty_cycle)
            except Exception as e:
                print(f"Error setting PWM on pin {self.pin}: {e}")
            finally:
                # Release the mutex.
                self.init.mutex_release(self.mutex, "Output_Wombat_18AB:set_output")
        else:
            # Set the duty cycle to 0 to turn off the output.
            self.init.mutex_acquire(self.mutex, "Output_Wombat_18AB:set_output")
            try:
                self.pwm.writeDutyCycle(0)
            except Exception as e:
                print(f"Error disabling PWM on pin {self.pin}: {e}")
            finally:
                self.init.mutex_release(self.mutex, "Output_Wombat_18AB:set_output")


class RGB_Wombat_18AB(RGB):
    """
    A class for handling RGB LEDs with a Wombat 18AB driver.
    """
    def __init__(self, init, driver, swpwm, red_pin, green_pin, blue_pin, mutex):
        super().__init__()
        self.init = init
        self.driver = driver
        self.swpwm = swpwm
        self.red_pin = red_pin
        self.green_pin = green_pin
        self.blue_pin = blue_pin
        self.mutex = mutex

        # Initialize PWM outputs for the RGB LED (skip if pin is None).
        self.red_pwm = None
        self.green_pwm = None
        self.blue_pwm = None

        # Set up PWM outputs with a frequency of 1 kHz and 0% duty cycle (off).
        self.init.mutex_acquire(self.mutex, "RGB_Wombat_18AB:init")
        try:
            if self.red_pin is not None:
                self.red_pwm = self.swpwm(self.driver)
                self.red_pwm.begin(self.red_pin, 0)
                self.red_pwm.writeFrequency_Hz(1000)  # 1 kHz

            if self.green_pin is not None:
                self.green_pwm = self.swpwm(self.driver)
                self.green_pwm.begin(self.green_pin, 0)
                self.green_pwm.writeFrequency_Hz(1000)

            if self.blue_pin is not None:
                self.blue_pwm = self.swpwm(self.driver)
                self.blue_pwm.begin(self.blue_pin, 0)
                self.blue_pwm.writeFrequency_Hz(1000)
        finally:
            self.init.mutex_release(self.mutex, "RGB_Wombat_18AB:init")

        # Initialize the LED to off.
        self.set_color(0, 0, 0)

    def set_color(self, r, g, b):
        """
        Sets the color of the RGB LED using the Wombat 18AB driver.

        Parameters:
        ----------
        r : int
            Red value (0-255).
        g : int
            Green value (0-255).
        b : int
            Blue value (0-255).
        """
        # Scale the 8-bit color values (0-255) to 16-bit duty cycles (0-65535).
        red_duty = int((r / 255) * 0xFFFF) if self.red_pin is not None else 0
        green_duty = int((g / 255) * 0xFFFF) if self.green_pin is not None else 0
        blue_duty = int((b / 255) * 0xFFFF) if self.blue_pin is not None else 0

        # Acquire the mutex to ensure thread-safe access to the PWM outputs.
        self.init.mutex_acquire(self.mutex, "RGB_Wombat_18AB:set_color")
        try:
            # Set the duty cycles for the red, green, and blue channels.
            if self.red_pin is not None:
                self.red_pwm.writeDutyCycle(red_duty)
            if self.green_pin is not None:
                self.green_pwm.writeDutyCycle(green_duty)
            if self.blue_pin is not None:
                self.blue_pwm.writeDutyCycle(blue_duty)
        finally:
            # Release the mutex.
            self.init.mutex_release(self.mutex, "RGB_Wombat_18AB:set_color")


class Switch_Wombat_18AB(Input):

    def __init__(self, init, driver, swdi, switch, mutex, init_complete):
        super().__init__()
        self.init = init
        self.driver = driver
        self.swdi = swdi
        self.debounce_delay = 30
        self.switch = switch
        self.pull_up = self.switch.get("pull_up", False)
        self.mutex = mutex
        self.di_instances = []
        self.active_interrupt = False
        self.init_complete = init_complete

        # Disable integrated switches in encoders.
        self.init.integrated_switches = False

        for i, pin in enumerate(self.switch.get("pins")):
            if pin is None:
                self.di_instances.append(None)
                continue
            self.di = self.swdi(driver)
            self.init.mutex_acquire(self.mutex, "Switch_Wombat_18AB:begin")
            try:
                print(f"begin - pin: {pin}, debounce_mS: {self.debounce_delay}, usePullUp: {self.pull_up}")
                self.di.begin(
                    pin=pin,
                    debounce_mS=self.debounce_delay,
                    invert=True,
                    usePullUp=self.pull_up,
                )
            except Exception as e:
                print(f"Error initializing DebouncedInput on pin {pin}: {e}")
            finally:
                self.init.mutex_release(self.mutex, "Switch_Wombat_18AB:begin")
            self.di_instances.append(self.di)

        # Set up the host interrupt pin.
        host_interrupt_pin = self.switch.get("host_interrupt_pin")
        if self.switch.get("host_interrupt_pin_pull_up", False):
            host_int = Pin(host_interrupt_pin, Pin.IN, Pin.PULL_UP)
        else:
            host_int = Pin(host_interrupt_pin, Pin.IN)
        host_int.irq(trigger=Pin.IRQ_FALLING, handler=self._interrupt)

        prefix = "Switch_Wombat_18AB:switch_interrupt_"
        # Set up the pulse on change pin.
        from SerialWombatPulseOnChange import SerialWombatPulseOnChange as swpoc
        poc = swpoc(self.driver)
        self.init.mutex_acquire(self.mutex, f"{prefix}begin")
        poc.begin(
            pin=switch.get("pulse_on_change_pin"),
            activeMode=1,
            inactiveMode=0,
            pulseOnTime=50,
            pulseOffTime=50,
            orNotAnd=1,
        );
        self.init.mutex_release(self.mutex, f"{prefix}begin")

        for i, pin in enumerate(self.switch.get("pins")):
            self.init.mutex_acquire(self.mutex, f"{prefix}set_{pin}")
            poc.setEntryOnIncrease(i, pin)
            self.init.mutex_release(self.mutex, f"{prefix}set_{pin}")

        # Set up the host interrupt pin.
        host_interrupt_pin = self.switch.get("host_interrupt_pin")
        if self.switch.get("host_interrupt_pin_pull_up", False):
            host_int = Pin(host_interrupt_pin, Pin.IN, Pin.PULL_UP)
        else:
            host_int = Pin(host_interrupt_pin, Pin.IN)
        host_int.irq(trigger=Pin.IRQ_FALLING, handler=self._interrupt)

        asyncio.create_task(self._poll())

    async def _poll(self):
        """
        Asyncio task to poll Wombat switch pins.
        """
        text = "Switch_Wombat_18AB:poll"
        while True:
            if self.active_interrupt:
                self.active_interrupt = False
                for i, pin in enumerate(self.switch.get("pins")):
                    if pin is None:
                        continue
                    di = self.di_instances[i]
                    self.init.mutex_acquire(self.mutex, text)
                    state = di.readTransitionsState()
                    self.init.mutex_release(self.mutex, text)
                    if di.transitions > 0 and state:
                        self.switch_click(i+1)
                        break
                    await asyncio.sleep(0.01)
            await asyncio.sleep(0.01)

    def _interrupt(self, pin):
        if self.init_complete[0]:
            self.active_interrupt = True

    def switch_click(self, switch):
        """
        Handle a switch click event.
        """
        print(f"switch click: {switch}")
        if switch <= 4:
            # Switches 1-4: Call the parent class's switch_click method.
            super().switch_click(switch)
        else:
            # Switches 5-6: Simulate encoder 1 rotation
            direction = 1 if switch == 6 else -1  # Switch 5 = Previous, Switch 6 = Next.
            super().encoder_change(0, direction)  # Encoder 1 is index 0.


class Encoder_Wombat_18AB(Input):

    def __init__(self, init, driver, swqe, encoder, mutex, init_complete):
        super().__init__()
        self.init = init
        self.driver = driver
        self.swqe = swqe
        self.debounce_delay = 0
        self.encoder = encoder
        self.pull_up = self.encoder.get("pull_up", False)
        self.mutex = mutex
        self.qe_instances = []
        self.active_interrupt = False
        self.init_complete = init_complete

        text = f"{self.__class__.__name__}:begin"
        for i, pin in enumerate(self.encoder.get("pins")):
            if pin is None:
                self.qe_instances.append(None)
                continue
            pin, secondPin = pin
            if pin is None or secondPin is None:
                self.qe_instances.append(None)
                continue
            self.qe = self.swqe(driver)
            self.init.mutex_acquire(self.mutex, text)
            try:
                self.qe.begin(
                    pin,
                    secondPin,
                    debounce_mS = self.debounce_delay,
                    pullUpsEnabled = self.pull_up,
                    readState = 5,
                )
                val = self.qe.write(32768)
                print(f"encoder init val: {val}")
            except Exception as e:
                print(f"Error initializing SerialWombatQuadEnc on pin {pin}: {e}")
            finally:
                self.init.mutex_release(self.mutex, text)
            self.qe_instances.append(self.qe)

        prefix = f"{self.__class__.__name__}:encoder_interrupt_"
        # Set up the pulse on change pin.
        from SerialWombatPulseOnChange import SerialWombatPulseOnChange as swpoc
        poc = swpoc(self.driver)
        self.init.mutex_acquire(self.mutex, f"{prefix}begin")
        poc.begin(
            pin=encoder.get("pulse_on_change_pin"),
            activeMode=1,
            inactiveMode=0,
            pulseOnTime=50,
            pulseOffTime=50,
            orNotAnd=1,
        );
        self.init.mutex_release(self.mutex, f"{prefix}begin")

        index = 0
        for pin_set in self.encoder.get("pins"):
            for pin in pin_set:
                self.init.mutex_acquire(self.mutex, f"{prefix}set_{pin}")
                print(f"setEntryOnIncrease - index: {index} pin: {pin}")
                poc.setEntryOnChange(index, pin)
                self.init.mutex_release(self.mutex, f"{prefix}set_{pin}")
            index += 1

        # Set up the host interrupt pin.
        host_interrupt_pin = self.encoder.get("host_interrupt_pin")
        if self.encoder.get("host_interrupt_pin_pull_up", False):
            host_int = Pin(host_interrupt_pin, Pin.IN, Pin.PULL_UP)
        else:
            host_int = Pin(host_interrupt_pin, Pin.IN)
        host_int.irq(trigger=Pin.IRQ_FALLING, handler=self._interrupt)

        asyncio.create_task(self._poll())

    def _interrupt(self, pin):
        if self.init_complete[0]:
            print("_encoder_interrupt")
            self.active_interrupt = True

    async def _poll(self):
        print("Encoder_Wombat_18AB - _poll")
        """
        Asyncio task to poll Wombat encoders.
        """
        text = "Encoder_Wombat_18AB:poll"

        while True:
            if self.active_interrupt:
                self.active_interrupt = False
                for i, pin in enumerate(self.encoder.get("pins")):
                    qe = self.qe_instances[i]
                    self.init.mutex_acquire(self.mutex, text)
                    value = qe.read(32768)
                    self.init.mutex_release(self.mutex, text)
                    print(f"pooling encoder: {i} (pin: {pin}) value: {value}")
                    if value != 32768:
                        if value > 32768:
                            print(f"rotary encoder {i} upward change")
                            super().encoder_change(i, 1)
                        else:
                            print(f"rotary encoder {i} downward change")
                            super().encoder_change(i, -1)
                        break
                    await asyncio.sleep(0.01)
            await asyncio.sleep(0.01)
