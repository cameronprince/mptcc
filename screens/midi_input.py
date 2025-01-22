"""
MicroPython Tesla Coil Controller (MPTCC)
by Cameron Prince
teslauniverse.com

screens/midi_input.py
Provides functionality for the MIDI input feature.
"""

from mptcc.hardware.init import init
from mptcc.lib.menu import CustomItem
import mptcc.lib.config as config
import mptcc.lib.utils as utils
import _thread
import SimpleMIDIDecoder

class MIDIInput(CustomItem):
    """
    A class to represent and handle the MIDI input feature for the MicroPython Tesla Coil Controller (MPTCC).

    Attributes:
    -----------
    name : str
        The name of the MIDI input screen.
    uart : machine.UART
        The UART object for MIDI communication.
    display : object
        The display object for rendering the screen.
    md : SimpleMIDIDecoder.SimpleMIDIDecoder
        The MIDI decoder object.
    listening : bool
        Flag to indicate if MIDI input is listening.
    midi_thread : _thread
        The thread object for handling MIDI input.
    header_height : int
        The height of the display header.
    """

    def __init__(self, name):
        """
        Constructs all the necessary attributes for the MIDIInput object.

        Parameters:
        ----------
        name : str
            The name of the MIDI input screen.
        """
        super().__init__(name)
        self.uart = None
        self.display = init.display
        self.md = SimpleMIDIDecoder.SimpleMIDIDecoder()
        self.md.cbNoteOn(self.note_on)
        self.md.cbNoteOff(self.note_off)
        self.listening = False
        self.midi_thread = None
        self.header_height = init.display.DISPLAY_HEADER_HEIGHT
        self.level = 50

        self.init = init
        self.display = self.init.display

    def draw(self):
        """
        Displays the MIDI input screen.
        """
        self.display.clear()
        self.display.header(str.upper("MIDI Input"))
        self.display.text("Ready for input", 0, 20, 1)
        self.display.show()
        self.start_midi_input()

    def start_midi_input(self):
        """
        Initializes the UART and starts the listening thread.
        """
        if not self.listening:
            self.listening = True
            self.init.init_uart()
            self.midi_thread = _thread.start_new_thread(self.midi_input_thread, ())

    def stop_midi_input(self):
        """
        Stops MIDI input.
        """
        if self.listening:
            self.listening = False
            self.display.clear()

    def midi_input_thread(self):
        """
        Responds to input from the UART and passes the data to the MIDI parser.
        """
        while self.listening:
            if self.init.uart.any():
                data = self.init.uart.read(1)[0]
                self.md.read(data)

    def note_on(self, ch, cmd, note, vel):
        """
        Responds to note on events and enables outputs.

        Parameters:
        ----------
        ch : int
            MIDI channel.
        cmd : int
            MIDI command.
        note : int
            MIDI note number.
        vel : int
            MIDI note velocity.
        """
        frequency = utils.midi_to_frequency(note)
        on_time = utils.velocity_to_ontime(vel)
        # scaled_on_time = int(on_time * self.level / 100)

        # Drive all four outputs equally.
        for output in range(4):
            self.init.output.set_output(output, frequency, on_time, True)

    def note_off(self, ch, cmd, note, vel):
        """
        Responds to note off events to disable outputs.

        Parameters:
        ----------
        ch : int
            MIDI channel.
        cmd : int
            MIDI command.
        note : int
            MIDI note number.
        vel : int
            MIDI note velocity.
        """
        # Disable all outputs.
        for output in range(4):
            self.init.output.set_output(output, 0, 0, False)

    def switch_2(self):
        """
        Responds to encoder 2 presses to return to the main menu.
        """
        self.stop_midi_input()
        self.init.output.disable_outputs()
        parent_screen = self.parent
        if parent_screen:
            self.init.menu.set_screen(parent_screen)
            self.init.menu.draw()