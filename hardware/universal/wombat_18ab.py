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
from ...lib.utils import calculate_duty_cycle
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
        beep=None,
    ):
        """
        Constructs all the necessary attributes for the Wombat_18AB object.
        """
        if encoder is None and output is None and rgb_led is None and switch is None and beep is None:
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

        print(f"Wombat_18AB universal driver initialized (I2C Address: {hex(i2c_addr)})")

        if rgb_led is not None or output is not None:
            from SerialWombatPWM import SerialWombatPWM_18AB as swpwm

        # Initialize switches if switch is provided.
        if switch is not None and switch.get("enabled", True):
            from SerialWombatDebouncedInput import SerialWombatDebouncedInput as swdi
            if "wombat_18ab_switch" not in self.init.input_instances:
                self.init.input_instances["wombat_18ab_switch"] = []
            switch_instances = []
            switch_instance = Switch_Wombat_18AB(
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
        if encoder is not None and encoder.get("enabled", True):
            from SerialWombatQuadEnc import SerialWombatQuadEnc as swqe
            if "wombat_18ab_encoder" not in self.init.input_instances:
                self.init.input_instances["wombat_18ab_encoder"] = []
            encoder_instances = []
            encoder_instance = Encoder_Wombat_18AB(
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
        if output is not None and output.get("enabled", True):
            if "wombat_18ab" not in self.init.output_instances:
                self.init.output_instances["wombat_18ab"] = []
            output_instances = []
            for pin in output.get("pins"):
                o = Output_Wombat_18AB(self.driver, swpwm, pin, self.mutex)
                output_instances.append(o)
            self.init.output_instances["wombat_18ab"].append(output_instances)
            print(f"- Outputs initialized:")
            for i, pin in enumerate(output.get("pins")):
                print(f"  - Output {i}: Pin {pin}")

        # Initialize RGB LEDs if rgb_led is provided.
        if rgb_led is not None and rgb_led.get("enabled", True):
            if "wombat_18ab" not in self.init.rgb_led_instances:
                self.init.rgb_led_instances["wombat_18ab"] = []
            rgb_led_instances = []
            for led_pins in rgb_led_pins:
                red_pin, green_pin, blue_pin = led_pins
                led = RGB_Wombat_18AB(
                    driver=self.driver,
                    swpwm=swpwm,
                    red_pin=red_pin,
                    green_pin=green_pin,
                    blue_pin=blue_pin,
                    mutex=self.mutex,
                )
                rgb_led_instances.append(led)
            self.init.rgb_led_instances["wombat_18ab"].append(rgb_led_instances)
            print(f"- RGB LEDs initialized:")
            for i, led_pins in enumerate(rgb_led_pins):
                red_pin, green_pin, blue_pin = led_pins
                print(f"  - LED {i}: R={red_pin}, G={green_pin}, B={blue_pin}")

        # Initialize Beep if beep is provided.
        if beep is not None and beep.get("enabled", True):
            self.init.beep = Beep_Wombat_18AB(
                driver=self.driver,
                beep=beep,
                mutex=self.mutex,
            )
            print(f"- Beep tone confirmation enabled (Pin: {beep.get("pin")}, Length: {beep.get("length_ms")}ms, Volume: {beep.get("volume")}%, PWM frequency: {beep.get("pwm_freq")}Hz)")

        self.init_complete[0] = True


class Output_Wombat_18AB(Output):
    """
    A class for handling outputs with a Serial Wombat 18AB driver.
    """
    def __init__(self, driver, swpwm, pin, mutex):
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
        self.class_name = self.__class__.__name__

        # Initialize the PWM output on the specified pin with a duty cycle of 0 (off).
        self.pwm = self.swpwm(self.driver)
        self.init.mutex_acquire(self.mutex, f"{self.class_name}:init")
        try:
            self.pwm.begin(self.pin, 0)
        except Exception as e:
            print(f"Error initializing PWM on pin {pin}: {e}")
        finally:
            self.init.mutex_release(self.mutex, f"{self.class_name}:init")

    def set_output(self, active=False, freq=None, on_time=None, max_duty=None, max_on_time=None):
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
            duty_cycle = calculate_duty_cycle(on_time, freq)

            # Acquire the mutex for both operations.
            self.init.mutex_acquire(self.mutex, f"{self.class_name}:set_output")
            try:
                # Set the frequency of the PWM signal.
                self.pwm.writeFrequency_Hz(freq)
                # Set the duty cycle.
                self.pwm.writeDutyCycle(duty_cycle)
            except Exception as e:
                print(f"Error setting PWM on pin {self.pin}: {e}")
            finally:
                # Release the mutex.
                self.init.mutex_release(self.mutex, f"{self.class_name}:set_output")
        else:
            # Set the duty cycle to 0 to turn off the output.
            self.init.mutex_acquire(self.mutex, f"{self.class_name}:set_output")
            try:
                self.pwm.writeDutyCycle(0)
            except Exception as e:
                print(f"Error disabling PWM on pin {self.pin}: {e}")
            finally:
                self.init.mutex_release(self.mutex, f"{self.class_name}:set_output")


class RGB_Wombat_18AB(RGB):
    """
    A class for handling RGB LEDs with a Wombat 18AB driver.
    """
    def __init__(self, driver, swpwm, red_pin, green_pin, blue_pin, mutex):
        super().__init__()
        self.init = init
        self.driver = driver
        self.swpwm = swpwm
        self.red_pin = red_pin
        self.green_pin = green_pin
        self.blue_pin = blue_pin
        self.mutex = mutex
        self.class_name = self.__class__.__name__

        # Initialize PWM outputs for the RGB LED (skip if pin is None).
        self.red_pwm = None
        self.green_pwm = None
        self.blue_pwm = None

        # Set up PWM outputs with a frequency of 1 kHz and 0% duty cycle (off).
        self.init.mutex_acquire(self.mutex, f"{self.class_name}:init")
        try:
            if self.red_pin is not None:
                self.red_pwm = self.swpwm(self.driver)
                self.red_pwm.begin(self.red_pin, 0)
                self.red_pwm.writeFrequency_Hz(1000)

            if self.green_pin is not None:
                self.green_pwm = self.swpwm(self.driver)
                self.green_pwm.begin(self.green_pin, 0)
                self.green_pwm.writeFrequency_Hz(1000)

            if self.blue_pin is not None:
                self.blue_pwm = self.swpwm(self.driver)
                self.blue_pwm.begin(self.blue_pin, 0)
                self.blue_pwm.writeFrequency_Hz(1000)
        finally:
            self.init.mutex_release(self.mutex, f"{self.class_name}:init")

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
        self.init.mutex_acquire(self.mutex, f"{self.class_name}:set_color")
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
            self.init.mutex_release(self.mutex, f"{self.class_name}:set_color")


class Switch_Wombat_18AB(Input):

    def __init__(self, driver, swdi, switch, mutex, init_complete):
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
        self.class_name = self.__class__.__name__

        # Disable integrated switches in encoders.
        self.init.integrated_switches = False

        for i, pin in enumerate(self.switch.get("pins")):
            if pin is None:
                self.di_instances.append(None)
                continue
            self.di = self.swdi(driver)
            self.init.mutex_acquire(self.mutex, f"{self.class_name}:switch:begin")
            try:
                self.di.begin(
                    pin=pin,
                    debounce_mS=self.debounce_delay,
                    invert=True,
                    usePullUp=self.pull_up,
                )
            except Exception as e:
                print(f"Error initializing DebouncedInput on pin {pin}: {e}")
            finally:
                self.init.mutex_release(self.mutex, f"{self.class_name}:switch:begin")
            self.di_instances.append(self.di)

        # Set up the host interrupt pin.
        host_interrupt_pin = self.switch.get("host_interrupt_pin")
        if self.switch.get("host_interrupt_pin_pull_up", False):
            host_int = Pin(host_interrupt_pin, Pin.IN, Pin.PULL_UP)
        else:
            host_int = Pin(host_interrupt_pin, Pin.IN)
        host_int.irq(trigger=Pin.IRQ_FALLING, handler=self._interrupt)

        # Set up the pulse on change pin.
        from SerialWombatPulseOnChange import SerialWombatPulseOnChange as swpoc
        poc = swpoc(self.driver)
        self.init.mutex_acquire(self.mutex, f"{self.class_name}:switch_poc:begin")
        poc.begin(
            pin=switch.get("pulse_on_change_pin"),
            activeMode=1,
            inactiveMode=0,
            pulseOnTime=1,
            pulseOffTime=1,
            orNotAnd=1,
        );
        self.init.mutex_release(self.mutex, f"{self.class_name}:switch_poc:begin")

        for i, pin in enumerate(self.switch.get("pins")):
            self.init.mutex_acquire(self.mutex, f"{self.class_name}:switch_poc:pin{pin}")
            poc.setEntryOnIncrease(i, pin)
            self.init.mutex_release(self.mutex, f"{self.class_name}:switch_poc:pin{pin}")

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
        while True:
            if self.active_interrupt:
                self.active_interrupt = False
                for i, pin in enumerate(self.switch.get("pins")):
                    if pin is None:
                        continue
                    di = self.di_instances[i]
                    self.init.mutex_acquire(self.mutex, f"{self.class_name}:poll")
                    state = di.readTransitionsState()
                    self.init.mutex_release(self.mutex, f"{self.class_name}:poll")
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
        if switch <= 4:
            # Switches 1-4: Call the parent class's switch_click method.
            super().switch_click(switch)
        else:
            # Switches 5-6: Simulate encoder 1 rotation
            direction = 1 if switch == 6 else -1  # Switch 5 = Previous, Switch 6 = Next.
            super().encoder_change(0, direction)  # Encoder 1 is index 0.


class Encoder_Wombat_18AB(Input):

    def __init__(self, driver, swqe, encoder, mutex, init_complete):
        super().__init__()
        self.init = init
        self.driver = driver
        self.swqe = swqe
        self.debounce_delay = 0
        self.encoder = encoder
        self.mutex = mutex
        self.qe_instances = []
        self.init_complete = init_complete
        self.active_interrupt = False
        self.class_name = self.__class__.__name__

        for i, pin in enumerate(self.encoder.get("pins")):
            if pin is None:
                self.qe_instances.append(None)
                continue
            pin, secondPin = pin
            if pin is None or secondPin is None:
                self.qe_instances.append(None)
                continue
            self.qe = self.swqe(driver)
            self.init.mutex_acquire(self.mutex, f"{self.class_name}:encoder:begin")
            try:
                self.qe.begin(
                    pin,
                    secondPin,
                    debounce_mS = self.debounce_delay,
                    pullUpsEnabled = self.encoder.get("pull_up", False),
                    readState = 5,
                )
                val = self.qe.write(32768)
            except Exception as e:
                print(f"Error initializing SerialWombatQuadEnc on pin {pin}: {e}")
            finally:
                self.init.mutex_release(self.mutex, f"{self.class_name}:encoder:begin")
            self.qe_instances.append(self.qe)

        # Set up the pulse on change pin.
        from SerialWombatPulseOnChange import SerialWombatPulseOnChange as swpoc
        poc = swpoc(self.driver)
        self.init.mutex_acquire(self.mutex, f"{self.class_name}:encoder_poc:begin")
        poc.begin(
            pin=encoder.get("pulse_on_change_pin"),
            activeMode=1,
            inactiveMode=0,
            pulseOnTime=1,
            pulseOffTime=1,
            orNotAnd=1,
        );
        self.init.mutex_release(self.mutex, f"{self.class_name}:encoder_poc:begin")

        index = 0
        for pins in self.encoder.get("pins"):
            self.init.mutex_acquire(self.mutex, f"{self.class_name}:encoder_poc:pin{pin}")
            poc.setEntryOnChange(index, pins[0])
            self.init.mutex_release(self.mutex, f"{self.class_name}:encoder_poc:pin{pin}")
            index += 1

        # Sleep one second to allow pins to settle to prevent false interrupts.
        time.sleep(1)

        # Set up the host interrupt pin.
        self.host_int = Pin(
            self.encoder.get("host_interrupt_pin"), 
            Pin.IN, 
            Pin.PULL_UP if self.encoder.get("host_interrupt_pin_pull_up", False) else None
        )
        self.host_int.irq(trigger=Pin.IRQ_FALLING, handler=self._interrupt)

        asyncio.create_task(self._poll())

    def _interrupt(self, pin):
        print("_interrupt")
        if not self.init_complete[0]:
            return
        self.active_interrupt = True

    async def _poll(self):
        """
        Asyncio task to poll Wombat encoders.
        """
        while True:
            if self.active_interrupt:
                print(f"_poll active interrupt")
                self.active_interrupt = False
                self._process_interrupt()
            await asyncio.sleep(0.01)

    def _process_interrupt(self):
        self.init.mutex_acquire(self.mutex, f"{self.class_name}:encoder:read")
        for i, pin in enumerate(self.encoder.get("pins")):
            value = self.qe_instances[i].read(32768)
            if value != 32768:
                break
        self.init.mutex_release(self.mutex, f"{self.class_name}:encoder:read")
        if value > 32768:
            super().encoder_change(i, 1)
        elif value < 32768:
            super().encoder_change(i, -1)


class Beep_Wombat_18AB():
    """
    A class for handling beep tone confirmation with a Serial Wombat 18AB driver.
    """
    def __init__(self, driver, beep, mutex):
        """
        Constructs all the necessary attributes for the Beep_Wombat_18AB object.
        """
        self.driver = driver
        self.mutex = mutex
        self.pin = beep.get("pin")
        self.length_ms = beep.get("length_ms")
        self.volume = beep.get("volume")
        self.duty = int((self.volume / 100) * 65535)
        self.class_name = self.__class__.__name__
        self.init = init

        self.init.mutex_acquire(self.mutex, f"{self.class_name}:init")
        if self.volume == 100:
            # Set the pin as an output and default low.
            self.driver.pinMode(self.pin, 1)
            self.driver.digitalWrite(self.pin, 0)
        else:
            # Set up the pin's PWM and default to off.
            from SerialWombatPWM import SerialWombatPWM_18AB as swpwm
            self.pwm = swpwm(self.driver)
            self.pwm.begin(self.pin, 0)
            self.pwm.writeFrequency_Hz(beep.get("pwm_freq"))
            self.pwm.writeDutyCycle(0)
        self.init.mutex_release(self.mutex, f"{self.class_name}:init")

    def on(self):
        self.init.mutex_acquire(self.mutex, f"{self.class_name}:on")
        if self.volume == 100:
            self.driver.digitalWrite(self.pin, 1)
            time.sleep_ms(self.length_ms)
            self.driver.digitalWrite(self.pin, 0)
        else:
            self.pwm.writeDutyCycle(self.duty)
            time.sleep_ms(self.length_ms)
            self.pwm.writeDutyCycle(0)
        self.init.mutex_release(self.mutex, f"{self.class_name}:on")
