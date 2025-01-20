from ..hardware import Hardware
from machine import Pin
from rotary_irq_rp2 import RotaryIRQ
from mptcc.lib.menu import CustomItem
import time

class KY040:

    # Rotary encoder pin assignments.
    PIN_ROTARY_1_CLK = 11
    PIN_ROTARY_1_DT = 10
    PIN_ROTARY_1_SW = 12

    PIN_ROTARY_2_CLK = 14
    PIN_ROTARY_2_DT = 9
    PIN_ROTARY_2_SW = 15

    PIN_ROTARY_3_CLK = 26
    PIN_ROTARY_3_DT = 27
    PIN_ROTARY_3_SW = 0

    PIN_ROTARY_4_CLK = 20
    PIN_ROTARY_4_DT = 21
    PIN_ROTARY_4_SW = 17

    # Enable/disable encoder pin pull-up resistors.
    # Most of the PCB-mounted encoders have pull-ups on the boards.
    ROTARY_PULL_UP = False

    def __init__(self, init):

        # Define rotary interrupts.
        self.rotary_encoders = [
            RotaryIRQ(pin_num_clk=self.PIN_ROTARY_1_CLK, pin_num_dt=self.PIN_ROTARY_1_DT,
                      min_val=0, max_val=10, reverse=False, range_mode=RotaryIRQ.RANGE_UNBOUNDED,
                      pull_up=self.ROTARY_PULL_UP, half_step=False),
            RotaryIRQ(pin_num_clk=self.PIN_ROTARY_2_CLK, pin_num_dt=self.PIN_ROTARY_2_DT,
                      min_val=0, max_val=10, reverse=False, range_mode=RotaryIRQ.RANGE_UNBOUNDED,
                      pull_up=self.ROTARY_PULL_UP, half_step=False),
            RotaryIRQ(pin_num_clk=self.PIN_ROTARY_3_CLK, pin_num_dt=self.PIN_ROTARY_3_DT,
                      min_val=0, max_val=10, reverse=False, range_mode=RotaryIRQ.RANGE_UNBOUNDED,
                      pull_up=self.ROTARY_PULL_UP, half_step=False),
            RotaryIRQ(pin_num_clk=self.PIN_ROTARY_4_CLK, pin_num_dt=self.PIN_ROTARY_4_DT,
                      min_val=0, max_val=10, reverse=False, range_mode=RotaryIRQ.RANGE_UNBOUNDED,
                      pull_up=self.ROTARY_PULL_UP, half_step=False),
        ]
        self.last_rotations = [encoder.value() for encoder in self.rotary_encoders]

        # Add the listeners which file the rotary_encoder_change callback.
        for encoder in self.rotary_encoders:
            encoder.add_listener(self.rotary_encoder_change)

        # Define the switches.
        self.switch_1 = Pin(self.PIN_ROTARY_1_SW, Pin.IN, Pin.PULL_UP)
        self.switch_2 = Pin(self.PIN_ROTARY_2_SW, Pin.IN, Pin.PULL_UP)
        self.switch_3 = Pin(self.PIN_ROTARY_3_SW, Pin.IN, Pin.PULL_UP)
        self.switch_4 = Pin(self.PIN_ROTARY_4_SW, Pin.IN, Pin.PULL_UP)

        # Set up the switch interrupts.
        self.switch_1.irq(self.switch_click, Pin.IRQ_FALLING)
        self.switch_2.irq(self.switch_click, Pin.IRQ_FALLING)
        self.switch_3.irq(self.switch_click, Pin.IRQ_FALLING)
        self.switch_4.irq(self.switch_click, Pin.IRQ_FALLING)

    # The primary switch callback function.
    def switch_click(self, pin):
        time.sleep_ms(50)
        if pin.value() == 0:
            current_screen = self.init.menu.get_current_screen()
            if isinstance(current_screen, CustomItem):
                switch_dict = {
                    self.init.switch_1: 'switch_1',
                    self.init.switch_2: 'switch_2',
                    self.init.switch_3: 'switch_3',
                    self.init.switch_4: 'switch_4'
                }
                if pin in switch_dict:
                    method_name = switch_dict[pin]
                    if hasattr(current_screen, method_name):
                        getattr(current_screen, method_name)()
            else:
                if pin == self.init.switch_1:
                    self.init.menu.click()
                elif pin == self.init.switch_2:
                    parent_screen = self.init.menu.current_screen.parent
                    if parent_screen:
                        self.init.menu.set_screen(parent_screen)
                        self.init.menu.draw()

    # The primary rotary encoder callback function.
    def rotary_encoder_change(self):
        for idx, encoder in enumerate(self.rotary_encoders):
            new_value = encoder.value()
            if self.last_rotations[idx] != new_value:
                current_screen = self.init.menu.get_current_screen()
                method_name = f'rotary_{idx + 1}'
                if isinstance(current_screen, CustomItem) and hasattr(current_screen, method_name):
                    getattr(current_screen, method_name)(new_value)
                elif idx == 0:
                    self.init.menu.move(-1 if self.last_rotations[idx] > new_value else 1)
                self.last_rotations[idx] = new_value
                time.sleep_ms(50)
