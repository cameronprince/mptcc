# MicroPython Tesla Coil Controller (MPTCC)

A MicroPython-based controller for Tesla coils, developed by Cameron Prince. 

This project is based on the MIDI Pro Tesla Coil Controller (also MPTCC) by Phillip Slawinski. A best
effort was made to maintain control functionality matching Phillip's controller, along with feature
parity with the initial Interrupter, MIDI File and MIDI Input screens. A few new features were added
as well, and more are planned.

The controller has four outputs which can drive fiber optic transmitters of your choice, or you may
use other connectors, such as BNC, with shielded cables. The controller sends pulsed square waves of
a frequency and duty cycle you control with the rotary encoders on the Interrupter screen. On the MIDI
input screen, the controller takes the notes it receives from a MIDI instrument and converts them into
pulses matching the frequency and velocity of the received notes and sends them to all outputs.

The MIDI File screen lists MIDI files found on the SD card and allows you map tracks within a selected
file with each of the four outputs. During playback, the four rotary encoders control the levels of
each output. The RGB LEDs are active any time the outputs are active and their colors match the relative
level of each output with colors ranging from green to yellow and yellow to red.

This software provides a framework for any number of screens with each screen optionally having any number
of sub-screens. The rotary encoder and push-button inputs cascade down to each screen, or sub-screen,
so that all code for a particular screen is contained solely within its class. Adding your own screens
to customize the controller should be pretty straightforward.

Please be aware that this is my first significant work with MicroPython. I am certain this software can
be improved in many ways and I invite anyone to participate.

## Table of Contents

- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [File Descriptions](#file-descriptions)
- [License](#license)

## Features

- Class-based, modular screen management system
- Interrupt-driven inputs
- Utilizes threads for driving outputs
- Standard interrupter (square wave pulse generator) with variable frequency and on time with configurable limits (currently drives all four outpus equally)
- MIDI file playback from SD card with interface for mapping tracks to outputs - rotary encoders allow level control for each output
- MIDI input (currently drives all four outputs from a single input/channel)
- RGB LEDs display relative output levels as colors ranging from green, to yellow, to red
- Battery status monitoring
- Configuration stored in flash memory with restore defaults feature
- Intuitive menu system
- Easily expandable to support additional features

## Hardware
1. Raspberry Pi Pico 2 (Qty 1) [Buy](https://amzn.to/4hhQxz3) - or similar MicroPython-compatible microcontroller with at least two cores
2. PCA9685 16-channel 12-bit PWM (Qty 1) [Buy](https://amzn.to/4jf2E1J)
3. SD card reader (Qty 1) [Buy](https://amzn.to/40gHUhw)
4. Rotary encoder w/ switch (Qty 4) [Buy](https://www.amazon.com/dp/B0BGR4JPRK)
5. RGB LED (Qty 4) [Buy](https://amzn.to/4jlGqvc)
6. 2.4" SSD1309 OLED display (Qty 1) [Buy](https://amzn.to/40wQWbs) - or similar I2C-driven display with MicroPython frame buffer driver
7. 5-Pin DIN socket (Qty 1) [Buy](https://amzn.to/40hERpg)
8. 2N4401 NPN transistors (Qty 4) [Buy](https://amzn.to/4aikSeu)
9. 6N138 high-speed optocoupler (Qty 1) [Buy](https://amzn.to/3BXwgA4)
10. Fiber optic transmitters or connectors of your choice for outputs (Qty 4)
11. Various 1/8-watt resistors
12. 1N4148 diode (Qty 1)
11. 5VDC power source

## Dependencies
- Display driver ([MicroPython-SSD1306](https://github.com/TimHanewich/MicroPython-SSD1306))
- External PWM driver ([pca9685_for_pico](https://github.com/kevinmcaleer/pca9685_for_pico))
- Rotary encoder driver ([micropython-rotary](https://github.com/miketeachman/micropython-rotary))
- SD card reader driver ([sdcard.py](https://github.com/micropython/micropython-lib/blob/master/micropython/drivers/storage/sdcard/sdcard.py))
- MIDI input decoder ([SimpleMIDIDecoder](https://github.com/diyelectromusic/sdemp/blob/main/src/SDEMP/Micropython/SimpleMIDIDecoder.py))
- MIDI file parser ([umidiparser](https://github.com/bixb922/umidiparser))

## Schematics

Coming soon.

## Connections

Coming soon.

## Installation

1. Clone the repository:

    ```bash
    git clone https://github.com/yourusername/mptcc.git
    ```

2. Copy the project files to your MicroPython-compatible device. Typically, you place the entire mptcc directory into the root directory of your device.

3. Ensure you have the required dependencies installed on your device. The dependencies listed above should be placed into a lib subdirectory in the root directory of your device.

4. Edit the mptcc/init.py file and update any hardware variables for which your project deviates from the provided schematics and connection diagrams.

5. Run main.py

6. Custom firmware instructions coming soon.

## Usage

Upon powering up the device, navigate through the menu to configure settings, play MIDI files, or monitor battery status. Use the rotary encoders and buttons to interact with the menu.

## File Descriptions

- `mptcc/init.py`: Constants, shared attributes, and initialization code.
- `mptcc/main.py`: Main program file. Creates the menu object and sets up input interrupts.
- `mptcc/lib/config.py`: Provides default user configuration values for the project.
- `mptcc/lib/menu.py`: Provides menu functionality.
- `mptcc/lib/rgb.py`: Functions for controlling RGB LED colors.
- `mptcc/lib/utils.py`: Shared utility functions.
- `mptcc/screens/battery_status.py`: Displays the current battery status.
- `mptcc/screens/interrupter.py`: Core functionalities for the interrupter feature.
- `mptcc/screens/interrupter_config.py`: Provides the screen for configuring interrupter settings.
- `mptcc/screens/restore_defaults.py`: Provides the screen for restoring default settings.
- `mptcc/screens/__init__.py`: Imports each MIDI file screen.
- `mptcc/screens/midi_input.py`: Provides the functionality for the MIDI input feature.
- `mptcc/screens/midi_file/midi_file.py`: Sets up sub-screen handlers for MIDI file playback.
- `mptcc/screens/midi_file/assignment.py`: Sub-screen for assigning tracks to outputs.
- `mptcc/screens/midi_file/files.py`: Sub-screen providing MIDI file listing from SD card.
- `mptcc/screens/midi_file/play.py`: Sub-screen providing MIDI file playback.
- `mptcc/screens/midi_file/tracks.py`: Sub-screen providing MIDI track listing.
- `mptcc/screens/midi_file/__init__.py`: Imports each MIDI file sub-screen.
- `mptcc/test_scripts/*`: Various hardware test scripts.






## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more details.

---

Developed by Cameron Prince. Visit [teslauniverse.com](https://teslauniverse.com) for more information.