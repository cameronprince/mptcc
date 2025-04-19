"""
MicroPython Tesla Coil Controller (MPTCC)
by Cameron Prince
teslauniverse.com

hardware/output/gpio_pio.py
Class for driving outputs with PIO PWM.
"""

from machine import Pin
from rp2 import PIO, StateMachine, asm_pio
from ...hardware.init import init
from ..output.output import Output

# PIO program definition.
@asm_pio(sideset_init=PIO.OUT_LOW)
def pwm_prog():
    pull(noblock) .side(0)
    mov(x, osr)  # Keep most recent pull data stashed in X, for recycling by noblock.
    mov(y, isr)  # ISR must be preloaded with PWM count max.
    label("pwmloop")
    jmp(x_not_y, "skip")
    nop() .side(1)
    label("skip")
    jmp(y_dec, "pwmloop")


class Output_GPIO_PIO:
    """
    A class to wrap a single PIO PWM object and provide output control.
    """
    def __init__(self, pin, sm_id, smf=10_000_000):
        """
        Initialize the Output_GPIO_PIO instance.

        Parameters:
        ----------
        pin : int
            The GPIO pin number for the PIO PWM output.
        sm_id : int
            The state machine ID to use for this output.
        smf : int, optional
            The state machine frequency (default is 10 MHz).
        """
        self.pin = pin
        self.smf = smf
        self.sm = StateMachine(sm_id, pwm_prog, freq=self.smf, sideset_base=Pin(pin)) if pin is not None else None
        if self.sm is not None:
            self.sm.active(0)  # Ensure the state machine is initially inactive.

    def set_output(self, active=False, freq=None, on_time=None, max_duty=None, max_on_time=None):
        """
        Sets the output based on the provided parameters.

        Parameters:
        ----------
        active : bool, optional
            Whether the output should be active.
        freq : int, optional
            The frequency of the output signal.
        on_time : int, optional
            The on time of the output signal in microseconds.

        Raises:
        -------
        ValueError
            If freq or on_time is not provided when activating the output.
        """
        if self.sm is None:
            return  # Skip if the pin is not configured.

        if active:
            if freq is None or on_time is None:
                raise ValueError("Frequency and on_time must be provided when activating the output.")

            freq = int(freq)
            on_time = int(on_time)

            # Calculate the maximum count for the PWM signal.
            # Account for the loop running twice per cycle by dividing by 2.
            max_count = int(self.smf / (freq * 2))

            # Calculate the duty cycle for the desired on_time.
            # Account for the loop running twice per cycle by dividing by 2.
            duty_cycle = int((on_time / 2_000_000) * self.smf)  # Convert on_time (µs) to clock cycles

            # Ensure the duty cycle does not exceed the maximum count.
            if duty_cycle > max_count:
                duty_cycle = max_count

            # Deactivate the state machine to change configuration.
            self.sm.active(0)

            # Load the maximum count into the ISR.
            self.sm.put(max_count)
            self.sm.exec("pull()")
            self.sm.exec("mov(isr, osr)")

            # Load the duty cycle into the TX FIFO.
            self.sm.put(duty_cycle)

            # Start the state machine.
            self.sm.active(1)
        else:
            # Stop the state machine.
            self.sm.active(0)

            # Explicitly set the pin low.
            self.sm.exec("set(pins, 0)")


class GPIO_PIO(Output):
    def __init__(self, pins):
        """
        Initialize the GPIO_PIO driver.

        Parameters:
        ----------
        pins : list of int
            A list of GPIO pin numbers for PIO PWM outputs.
        """
        super().__init__()
        self.init = init

        # Initialize Output_GPIO_PIO instances for the provided pins.
        self.instances = []
        for i, pin in enumerate(pins):
            if pin is not None:
                # Assign a unique state machine ID for each output.
                sm_id = len(self.instances)  # Use the current length of instances as the ID.
                instance = Output_GPIO_PIO(pin, sm_id)
                self.instances.append(instance)
            else:
                self.instances.append(None)

        # Assign this instance to the next available key.
        instance_key = len(self.init.output_instances['gpio_pio'])

        # Print initialization details.
        print(f"GPIO_PIO driver {instance_key} initialized")
        for i, pin in enumerate(pins):
            if pin is not None:
                print(f"- Output {i}: GPIO {pin} (StateMachine {i})")
