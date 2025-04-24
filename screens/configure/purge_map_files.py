"""
MicroPython Tesla Coil Controller (MPTCC)
by Cameron Prince
teslauniverse.com

screens/configure/purge_map_files.py
Provides the screen for purging map files.
"""

import uos
from ...hardware.init import init
from ...lib.menu import Screen


class PurgeMapFiles(Screen):
    """
    A class to represent and handle the screen for purging map files
    in the MicroPython Tesla Coil Controller (MPTCC).
    """

    def __init__(self, name):
        """
        Constructs all the necessary attributes for the PurgeMapFiles object.

        Parameters:
        ----------
        name : str
            The name of the purge map files screen.
        """
        super().__init__(name)
        self.name = name
        self.init = init
        self.selection = "No"
        self.font_width = 8
        self.font_height = 8

    def draw(self):
        """
        Displays the purge map files screen with options.
        """
        self.init.display.clear()
        self.init.display.header(self.name)

        # Calculate positions for centering text.
        screen_width = self.init.display.width
        padding = 2
        vertical_spacing = 10

        purge_map_files_text = "Purge now?"
        purge_map_files_x = (screen_width - len(purge_map_files_text) * self.font_width) // 2

        yes_text = "Yes"
        no_text = "No"
        yes_no_text = f"{yes_text}       {no_text}"
        yes_no_x = (screen_width - len(yes_no_text) * self.font_width) // 2

        # Display the centered options.
        self.init.display.text(purge_map_files_text, purge_map_files_x, 20, 1)

        # Highlight the current selection.
        yes_background = int(self.selection == "Yes")
        no_background = int(self.selection == "No")

        yes_x = yes_no_x
        no_x = yes_no_x + len(yes_text) * self.font_width + 7 * self.font_width
        box_height = self.font_height + 2 * padding
        yes_y = 30 + vertical_spacing
        no_y = yes_y

        # Draw the background rectangles with padding.
        self.init.display.fill_rect(yes_x - padding, yes_y - padding, len(yes_text) * self.font_width + 2 * padding, box_height, yes_background)
        self.init.display.text(yes_text, yes_x, yes_y, int(not yes_background))

        self.init.display.fill_rect(no_x - padding, no_y - padding, len(no_text) * self.font_width + 2 * padding, box_height, no_background)
        self.init.display.text(no_text, no_x, no_y, int(not no_background))

        self.init.display.show()

    def purge_map_files(self):
        """
        Deletes all .map files in the SD card mount point.
        """
        mount_point = self.init.sd_card_reader.mount_point
        deleted_count = 0

        try:
            # Initialize SD card.
            self.init.sd_card_reader.init_sd()

            # List all files in the mount point and filter for .map files.
            for file_info in uos.listdir(mount_point):
                file_name = file_info[0] if isinstance(file_info, tuple) else file_info
                if file_name.lower().endswith('.map') and not file_name.startswith('._'):
                    try:
                        file_path = f"{mount_point}/{file_name}"
                        uos.remove(file_path)
                        deleted_count += 1
                    except OSError as e:
                        print(f"Error deleting {file_path}: {e}")

            # Display success or no-files message.
            if deleted_count > 0:
                self.init.display.alert_screen(f"Purged {deleted_count} map files")
            else:
                self.init.display.alert_screen("No map files found")

        except OSError as e:
            print(f"Error accessing SD card: {e}")
            self.init.display.alert_screen("SD card error")
        except Exception as e:
            print(f"Unexpected error during purge: {e}")
            self.init.display.alert_screen("Purge failed")
        finally:
            # Clean up SD card.
            self.init.sd_card_reader.deinit_sd()

        # Return to the main menu after a brief delay.
        import time
        time.sleep(2)  # Display message for 2 seconds.
        self.init.menu.reset()
        self.init.menu.draw()

    def rotary_1(self, direction):
        """
        Responds to encoder 1 rotation to select between "Yes" and "No".

        Parameters:
        ----------
        direction : int
            The direction of rotation (1 for clockwise, -1 for counterclockwise).
        """
        self.selection = "Yes" if self.selection == "No" else "No"
        self.draw()

    def switch_1(self):
        """
        Responds to switch 1 presses to perform the purge action if "Yes" is selected,
        or return to the configuration menu if "No" is selected.
        """
        if self.selection == "Yes":
            self.purge_map_files()
        else:
            self.switch_2()

    def switch_2(self):
        """
        Responds to encoder 2 presses to return to the configuration menu.
        """
        parent_screen = self.parent
        if parent_screen:
            self.init.menu.set_screen(parent_screen)
            self.init.menu.draw()
