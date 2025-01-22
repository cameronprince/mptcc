# MicroPython Tesla Coil Controller (MPTCC)

A MicroPython-based controller for Tesla coils, developed by Cameron Prince.

![MicroPython Tesla coil controller build](images/mptcc_build_v1.0.jpg?raw=true "MicroPython Tesla coil controller build")

This project is based on the MIDI Pro Tesla Coil Controller (also MPTCC) by Phillip Slawinski. A best
effort was made to maintain control functionality matching Phillip's controller, along with feature
parity with the initial Interrupter, MIDI File and MIDI Input screens. A few new features were added
as well, and more are planned.

The controller has four outputs which can drive fiber optic transmitters of your choice, or you may
use other connectors, such as BNC, with shielded cables. The controller sends pulsed square waves of
a frequency and duty cycle you control with the rotary encoders while on the Interrupter screen. On the MIDI
input screen, the controller takes the notes it receives from a MIDI instrument and converts them into
pulses matching the frequency and velocity of the received notes and sends them to all outputs.

The MIDI File screen lists MIDI files found on the SD card and allows you to map tracks within a selected
file with each of the four outputs. During playback, the four rotary encoders control the levels of
each output. The RGB LEDs are active any time the outputs are active and their colors match the relative
level of each output with colors ranging from green, to yellow, to red.

This software provides a framework for any number of screens with each screen optionally having any number
of sub-screens. The rotary encoder and pushbutton inputs cascade down to each screen or sub-screen,
ensuring that all code for a particular screen is contained within its class. Adding your own screens
to customize the controller should be pretty straightforward.

Please be aware that this is my first significant work with MicroPython. I am certain this software can
be improved in many ways and I invite anyone to participate.

## Table of Contents

- [Warning](#warning)
- [Features](#features)
- [Hardware](#hardware)
- [Dependencies](#dependencies)
- [Diagram](#diagram)
- [Connections](#connections)
- [Installation](#installation)
- [Usage](#usage)
- [File Descriptions](#file-descriptions)
- [License](#license)
- [Credits](#credits)

## Warning

Tesla coils are dangerous devices which can cause shocks, burns, fires and even death. The author assumes no
responsibility for any devices operated by the controller project described herein, or for any damage or
injury that may be caused by their operation.

This controller is experimental. If not assembled and operated correctly, it can cause damage to driver and
bridge components. It is solely up to the builder to verify the controller output prior to connecting it to
a Tesla coil. The author assumes no responsibility for damage to equipment, components, tools, etc. which can be
caused by the use of this controller. You have been warned.

## Features

- Class-based, modular screen management system
- Interrupt-driven inputs/non-polling design
- Utilizes threads for driving outputs
- Standard interrupter (square wave pulse generator) with variable frequency and on time and user configurable limits (currently drives all four outputs equally)
- MIDI file playback from SD card with elapsed time display and interface for mapping tracks to outputs - rotary encoders allow level control for each output
- Automatic scrolling of long file and track names
- MIDI input (currently drives all four outputs from a single input/channel)
- RGB LEDs display relative output levels as colors ranging from green, to yellow, to red
- Battery status monitoring
- User configuration stored in flash memory with restore defaults feature
- Intuitive menu system and navigation
- Easily expandable to support additional features

## Hardware
1. Raspberry Pi Pico 2 (Qty 1) [Buy](https://amzn.to/4hhQxz3) - or similar MicroPython-compatible microcontroller with at least two cores
2. PCA9685 16-channel 12-bit PWM (Qty 1) [Buy](https://amzn.to/4jf2E1J)
3. SD card reader (Qty 1) [Buy](https://amzn.to/40gHUhw)
4. Rotary encoder w/ switch (Qty 4) [Buy](https://www.amazon.com/dp/B0BGR4JPRK)
5. RGB LED (Qty 4) [Buy](https://amzn.to/3PD5WhP)
6. 2.4" SSD1309 OLED display (Qty 1) [Buy](https://amzn.to/40wQWbs) - or similar I2C-driven display with MicroPython frame buffer driver
7. 5-Pin DIN socket (Qty 1) [Buy](https://amzn.to/40hERpg)
8. 2N4401 NPN transistors (Qty 4) [Buy](https://amzn.to/4aikSeu)
9. 6N138 high-speed optocoupler (Qty 1) [Buy](https://amzn.to/3BXwgA4)
10. Fiber optic transmitters or connectors of your choice for outputs (Qty 4)
11. Various 1/4-watt resistors [Buy](https://amzn.to/3DXIOYx)
12. 1N4148 diode (Qty 1) [Buy](https://amzn.to/4hi579Q)
13. 5VDC power source (Qty 1) [Buy](https://amzn.to/3Wre4pd)
14. Optional breadboard (Qty 1) [Buy](https://amzn.to/4hkUC5s)

Total estimated cost: $160 USD (not including output transmitters or connectors)

## Dependencies
- Display driver ([MicroPython-SSD1306](https://github.com/TimHanewich/MicroPython-SSD1306))
- External PWM driver ([pca9685_for_pico](https://github.com/kevinmcaleer/pca9685_for_pico))
- Rotary encoder driver ([micropython-rotary](https://github.com/miketeachman/micropython-rotary))
- SD card reader driver ([sdcard.py](https://github.com/micropython/micropython-lib/blob/master/micropython/drivers/storage/sdcard/sdcard.py))
- MIDI input decoder ([SimpleMIDIDecoder](https://github.com/diyelectromusic/sdemp/blob/main/src/SDEMP/Micropython/SimpleMIDIDecoder.py))
- MIDI file parser ([umidiparser](https://github.com/bixb922/umidiparser))

## Schematic

![MicroPython Tesla coil controller schematic](images/mptcc_schematic_v1.1.png?raw=true "MicroPython Tesla coil controller schematic")

## Diagram

![MicroPython Tesla coil controller connections](images/mptcc_connections_v1.1.png?raw=true "MicroPython Tesla coil controller connections")

You can download the Fritzing file for this project [here](images/mptcc_v1.1.fzz).

## Installation

1. Clone the repository:

    ```bash
    git clone https://github.com/cameronprince/mptcc.git
    ```

2. Copy the project files to your MicroPython-compatible device. Typically, you place the entire mptcc directory into the root directory of your device.

3. Ensure you have the required dependencies installed on your device. The dependencies listed above should be placed into a lib subdirectory in the root directory of your device.

4. Edit the mptcc/init.py file and update any hardware variables for which your project deviates from the provided schematics and connection diagrams.

5. Run main.py

Custom firmware build instructions coming soon.

## Usage

### General Operation

Rotate encoder 1 to scroll through the main menu options. Press encoder 1 pushbutton to navigate to a sub-menu item
or select a screen. Pressing encoder 2 pushbutton is consistently used as the "back" or "return" button.

### Interrupter

On the interrupter screen, encoder 1 rotation sets output on time. Encoder 2 rotation sets
output frequency. Press encoder 3 pushbutton to enable/disable outputs. Pressing encoder 4
pushbutton triggers 10x mode where the frequency and on time increments by 10 rather than
the default of 1. To return to the main menu, press encoder 2 pushbutton.

### MIDI Input

When MIDI input is selected from the main menu, the controller immediately begins listening
for MIDI events on the MIDI port. This screen only has one input which is encoder 2 pushbutton
to stop listening for MIDI events and return to the main menu.

### MIDI File

The initial MIDI file screen shows a listing of MIDI files available on the SD card. Use encoder 1
rotation to scroll through the list of files. Press encoder 1 pushbutton to select a file. The
display will then show a list of MIDI tracks within the selected file. As with files, use encoder 1
to scroll through the list and press encoder 1 pushbutton to select a track. On the subsequent
assignment screen, rotate encoder 1 to cycle between None, 1, 2, 3 and 4. Pressing encoder 1 pushbutton
saves the assignment. Pressing encoder 2 pushbutton returns to the track listing without saving the assignment.

The number of track assignments for a selected MIDI file is displayed in the header of the track listing screen,
such as 2/4, indicating two of the maximum of four mappings have been made. Selecting an output for a track
which has already been assigned to a different track will result in the original assignment being overwritten.
Only a single track may be mapped to a single output.

Once track assignments are complete, press encoder 2 pushbutton to return to the file listing. You may then
press encoder 3 pushbutton to start playback. During playback, rotation of each encoder controls the level
of its corresponding output. Pressing any encoder pushbutton during playback will result in the player stopping.

### Battery Status

This screen is much like the MIDI input screen in that only encoder 2 pushbutton is active to allow returning
to the main menu. On this screen the current battery voltage is displayed. Depending on your setup and
battery voltage, you may need to adjust the drop factor in init.py and/or R13 and R14 values to obtain accurate values.

### Interrupter Configuration

This screen, and its two sub-screens, allow configuring upper and lower frequency and on time limits, as well
as a max duty cycle percentage. These values are immediately saved to flash memory when adjustments are made.
There is no "save" button in this case. Encoder 2 pushbutton should be used to exit the screen and encoder 3
and 4 pushbuttons cycle through the configuration sub-screens.

### Restore Defaults

This screen allows you to erase user configuration and return to a set of defaults. This configuration is
currently used only by the interrupter screen, but can be easily expanded to support additional screens
and configuration variables.

## File Descriptions

- `mptcc/init.py`: Constants, shared attributes, and hardware initialization code.
- `mptcc/main.py`: Main program file. Creates the menu object and sets up input interrupts.
- `mptcc/lib/config.py`: Provides default user configuration values for the project.
- `mptcc/lib/menu.py`: Provides menu functionality.
- `mptcc/lib/rgb.py`: Functions for controlling RGB LED colors.
- `mptcc/lib/utils.py`: Shared utility functions.
- `mptcc/screens/battery_status.py`: Displays the current battery status.
- `mptcc/screens/interrupter.py`: Provides the interrupter screen.
- `mptcc/screens/interrupter_config.py`: Provides the screen for configuring interrupter settings.
- `mptcc/screens/restore_defaults.py`: Provides the screen for restoring default settings.
- `mptcc/screens/__init__.py`: Imports each screen.
- `mptcc/screens/midi_input.py`: Provides the the MIDI input screen.
- `mptcc/screens/midi_file/midi_file.py`: Sets up sub-screen handlers for MIDI file playback.
- `mptcc/screens/midi_file/assignment.py`: Sub-screen for assigning tracks to outputs.
- `mptcc/screens/midi_file/files.py`: Sub-screen providing MIDI file listing from SD card.
- `mptcc/screens/midi_file/play.py`: Sub-screen providing MIDI file playback.
- `mptcc/screens/midi_file/tracks.py`: Sub-screen providing MIDI track listing.
- `mptcc/screens/midi_file/__init__.py`: Imports each MIDI file sub-screen.
- `mptcc/test_scripts/*`: Various hardware test scripts.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more details.

## Credits

This project would not have been possible without Steve Ward and Phillip Slawinski. I've learned
a lot from these guys over the years and I appreciate the friendship I have with them.

Thanks to Hermann Paul von Borries (bixb922) for the umidiparser library and Kevin (diyelectromusic)
for the SimpleMIDIDecoder library.

Special thanks to Donna Whisnant, Tom Camp, Timur Tabi and Edwin Burwell for their encouragement,
guidance, support and code reviews.

---

Developed by Cameron Prince. Visit [teslauniverse.com](https://teslauniverse.com) for more information.
