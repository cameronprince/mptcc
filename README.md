# MicroPython Tesla Coil Controller (MPTCC)

A MicroPython-based controller for Tesla coils, developed by Cameron Prince. This project provides functionalities for managing interrupter settings, MIDI file playback, MIDI input, battery status, and restoring default settings.

## Table of Contents

- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [File Descriptions](#file-descriptions)
- [License](#license)

## Features

- Configurable interrupter settings
- MIDI file playback and input
- Battery status monitoring
- Restore default settings functionality
- Intuitive menu system

## Installation

1. Clone the repository:

    ```bash
    git clone https://github.com/yourusername/mptcc.git
    ```

2. Copy the project files to your MicroPython-compatible device.

3. Ensure you have the required dependencies installed on your device.

## Usage

Upon powering up the device, navigate through the menu to configure settings, play MIDI files, or monitor battery status. Use the rotary encoders and buttons to interact with the menu.

## File Descriptions

- `config.py`: Provides default configuration values for the project.
- `init.py`: Constants, shared attributes, and initialization code.
- `interrupter.py`: Core functionalities for the interrupter.
- `interrupter_config.py`: Provides the screen for configuring interrupter settings.
- `midi_file.py`: Handles MIDI file playback.
- `midi_input.py`: Provides all the functionality for the MIDI input feature.
- `battery_status.py`: Monitors and displays the battery status.
- `midi_file_config.py`: Provides the screen for configuring MIDI file playback settings.
- `restore_defaults.py`: Provides the screen for restoring default settings.
- `menu.py`: Provides menu functionality.
- `rgb.py`: Functions for controlling RGB LED colors.
- `utils.py`: Shared utility functions.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more details.

---

Developed by Cameron Prince. Visit [teslauniverse.com](https://teslauniverse.com) for more information.