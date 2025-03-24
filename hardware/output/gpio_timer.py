"""
MicroPython Tesla Coil Controller (MPTCC)
by Cameron Prince
teslauniverse.com

hardware/output/gpio_timer.py
Class for driving outputs with timers.
"""

from machine import Pin, Timer
from ..output.output import Output


class Output_GPIO_Timer:
    """
    A class to wrap a single timer-based PWM output and provide output control.
    """
    def __init__(self, pin):
        """
        Initialize the Output_GPIO_Timer instance.

        Parameters:
        ----------
        pin : int
            The GPIO pin number for the timer-based PWM output.
        """
        self.pin = pin
        self.output = Pin(pin, Pin.OUT) if pin is not None else None
        self.timer = Timer() if pin is not None else None
        self.running = False  # Flag to control timer execution.

    def _set_output_timer(self, frequency, on_time):
        """
        Configures a hardware timer to generate a PWM signal on the specified output.

        Parameters:
        ----------
        frequency : int
            The frequency of the PWM signal in Hz.
        on_time : int
            The on time of the PWM signal in microseconds.
        """
        if self.output is None or self.timer is None:
            return  # Skip if the pin or timer is not configured.

        # Ensure the pin starts in the LOW state.
        self.output.value(0)

        def toggle_pin(timer):
            # Toggle the pin state.
            self.output.toggle()

        # Initialize the timer.
        self.timer.deinit()  # Stop the timer if it's already running.
        self.timer.init(
            freq=frequency * 2,  # Set the timer frequency to twice the desired frequency.
            mode=Timer.PERIODIC, # Run the timer in periodic mode.
            callback=toggle_pin  # Callback to toggle the pin.
        )

    def set_output(self, active=False, freq=None, on_time=None):
        """
        Sets the output based on the provided parameters.

        Parameters:
        ----------
        active : bool, optional
            Whether the output should be active.
        freq : int, optional
            The frequency of the output signal in Hz.
        on_time : int, optional
            The on time of the output signal in microseconds.

        Raises:
        -------
        ValueError
            If freq or on_time is not provided when activating the output.
        """
        if self.output is None or self.timer is None:
            return  # Skip if the pin or timer is not configured.

        if active:
            if freq is None or on_time is None:
                raise ValueError("Frequency and on_time must be provided when activating the output.")

            freq = int(freq)
            on_time = int(on_time)

            # Configure the timer for PWM generation.
            self._set_output_timer(freq, on_time)
            self.running = True
        else:
            # Stop the timer and deactivate the output.
            self.running = False
            self.timer.deinit()
            # Set the pin low.
            self.output.value(0)


class GPIO_Timer(Output):
    def __init__(self, pins):
        """
        Initialize the GPIO_Timer driver.

        Parameters:
        ----------
        pins : list of int
            A list of GPIO pin numbers for timer-based PWM outputs.
        """
        super().__init__()

        # Initialize Output_GPIO_Timer instances for the provided pins.
        self.instances = [Output_GPIO_Timer(pin) for pin in pins]

        # Print initialization details.
        print(f"GPIO_Timer driver initialized")
        for i, pin in enumerate(pins):
            if pin is not None:
                print(f"- Output {i}: GPIO {pin}")
