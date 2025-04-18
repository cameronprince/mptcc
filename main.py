"""
MicroPython Tesla Coil Controller (MPTCC)
by Cameron Prince
teslauniverse.com

main.py
Initializes a hardware profile and starts the program.
"""

# Prepare the init object to store configuration and initialized hardware.
# There is a single, global instance of init which is shared throughout
# the project.
from mptcc.hardware.init import init

# DEBUGGING
#
# Mutex debugging causes print statements to be issued each time a mutex is
# acquired or released. This is very useful in following the flow of I2C
# communications.
# init.DEBUG_MUTEX = True

# When memory debugging is enabled, drivers print memory usage after they are
# initialized.
init.DEBUG_MEMORY = True

# HARDWARE PROFILES
#
# The MPTCC configuration is stored in files in the hardware/profiles directory.
# You can edit the default profile, or copy it to a new file in the profiles
# directory and reference it here instead of default.
PROFILE_NAME = "mptcc_5"
profile = __import__(f"mptcc.hardware.profiles.{PROFILE_NAME}", None, None, (None,))
profile.Profile(PROFILE_NAME, init)

# MENU DEFINITION
from mptcc.lib.menu import Menu, MenuScreen, SubMenuItem, Screen
import mptcc.screens as screens

init.menu = Menu(init.display)
init.menu.set_screen(MenuScreen("MicroPython TCC")
    .add(screens.Interrupter("Interrupter"))
    .add(screens.MIDIFile("MIDI File"))
    .add(screens.MIDIInput("MIDI Input"))
    .add(screens.ARSG("ARSG Emulator"))
    .add(screens.BatteryStatus("Battery Status"))
    .add(SubMenuItem("Configure")
        .add(screens.InterrupterConfig("Interrupter Config"))
        .add(screens.MIDIFileConfig("MIDI File Config"))
        .add(screens.ARSGConfig("ARSG Config"))
        .add(screens.RestoreDefaults("Restore Defaults"))
    )
)
init.menu.draw()

# Start the asyncio loop for handling asynchronous tasks. 
init.asyncio.start_loop()

# END