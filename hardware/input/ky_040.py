from ..hardware import Hardware
from machine import Pin
from rotary_irq_rp2 import RotaryIRQ
from mptcc.lib.menu import CustomItem

class KY040:
    def __init__(self, init):
        self.init = init
        self.rotary_encoders = [
            RotaryIRQ(pin_num_clk=init.encoders[0]['clk'], pin_num_dt=init.encoders[0]['dt'],
                      min_val=0, max_val=10, reverse=False, range_mode=RotaryIRQ.RANGE_UNBOUNDED,
                      pull_up=init.ROTARY_PULL_UP, half_step=False),
            RotaryIRQ(pin_num_clk=init.encoders[1]['clk'], pin_num_dt=init.encoders[1]['dt'],
                      min_val=0, max_val=10, reverse=False, range_mode=RotaryIRQ.RANGE_UNBOUNDED,
                      pull_up=init.ROTARY_PULL_UP, half_step=False),
            RotaryIRQ(pin_num_clk=init.encoders[2]['clk'], pin_num_dt=init.encoders[2]['dt'],
                      min_val=0, max_val=10, reverse=False, range_mode=RotaryIRQ.RANGE_UNBOUNDED,
                      pull_up=init.ROTARY_PULL_UP, half_step=False),
            RotaryIRQ(pin_num_clk=init.encoders[3]['clk'], pin_num_dt=init.encoders[3]['dt'],
                      min_val=0, max_val=10, reverse=False, range_mode=RotaryIRQ.RANGE_UNBOUNDED,
                      pull_up=init.ROTARY_PULL_UP, half_step=False),
        ]
        self.last_rotations = [encoder.value() for encoder in self.rotary_encoders]
        self.setup_interrupts()

    def setup_interrupts(self):
        self.init.switch_1.irq(self.switch_click, Pin.IRQ_FALLING)
        self.init.switch_2.irq(self.switch_click, Pin.IRQ_FALLING)
        self.init.switch_3.irq(self.switch_click, Pin.IRQ_FALLING)
        self.init.switch_4.irq(self.switch_click, Pin.IRQ_FALLING)
        for encoder in self.rotary_encoders:
            encoder.add_listener(self.rotary_encoder_change)

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
