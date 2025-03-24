"""
MicroPython Tesla Coil Controller (MPTCC)
by Cameron Prince
teslauniverse.com

hardware/display/tasks.py
Asyncio tasks for displays.
"""

import uasyncio as asyncio
from ...hardware.init import init

def start_scroll(display, text, y_position, identifier, background_color=1):
    """
    Helper to start scrolling text as an asyncio task.

    Parameters:
    ----------
    display : Display
        The display instance.
    text : str
        The text to scroll.
    y_position : int
        The y-coordinate where the text will be displayed.
    identifier : int
        A unique identifier (e.g., file index) for the scrolling task.
    background_color : int, optional
        The background color for the text (0 for inactive, 1 for active). Defaults to 1 (active).
    """
    stop_scroll(display)

    text_width = len(text) * display.font_width
    if text_width > display.width:
        display.scroll_flag = identifier
        display.scroll_text = text
        display.scroll_y_position = y_position

        display.fill_rect(0, y_position, display.width, display.line_height, background_color)
        v_padding = int((display.line_height - display.font_height) / 2)
        display.text(text, 0, y_position + v_padding, not background_color)
        display.show()

        display.scroll_task = asyncio.create_task(_scroll_task(display, text, y_position, identifier, background_color))

def stop_scroll(display):
    """
    Helper to stop scrolling text and reset the scroll state.

    Parameters:
    ----------
    display : Display
        The display instance.
    """
    if display.scroll_task:
        display.scroll_flag = None
        task_to_cancel = display.scroll_task
        display.scroll_task = None

        try:
            task_to_cancel.cancel()
        except Exception as e:
            if "can't cancel self" not in str(e):
                print(f"[ERROR] Failed to cancel scroll task: {e}")

        if display.scroll_text and display.scroll_y_position is not None:
            display.fill_rect(0, display.scroll_y_position, display.width, display.line_height, 0)
            v_padding = int((display.line_height - display.font_height) / 2)
            display.text(display.scroll_text, 0, display.scroll_y_position + v_padding, 1)
            display.show()
        display.scroll_text = None
        display.scroll_y_position = None

async def _scroll_task(display, text, y_position, identifier, background_color=1):
    """
    The main coroutine for handling text scrolling.

    Parameters:
    ----------
    display : Display
        The display instance.
    text : str
        The text to scroll.
    y_position : int
        The y-coordinate where the text will be displayed.
    identifier : int
        A unique identifier (e.g., file index) for the scrolling task.
    background_color : int, optional
        The background color for the text (0 for inactive, 1 for active). Defaults to 1 (active).
    """
    delay_seconds = 1
    delay_interval = 0.1
    elapsed_time = 0

    while display.scroll_flag == identifier and elapsed_time < delay_seconds:
        await asyncio.sleep(delay_interval)
        elapsed_time += delay_interval

    v_padding = int((display.line_height - display.font_height) / 2)

    while display.scroll_flag == identifier:
        for i in range(len(text) + display.items_per_page):
            if display.scroll_flag != identifier:
                return

            scroll_text = (text + "    ")[i:] + (text + "    ")[:i]
            display.fill_rect(0, y_position, display.width, display.line_height, background_color)
            display.text(scroll_text[:20], 0, y_position + v_padding, not background_color)
            display.show()
            await asyncio.sleep(0.2)

    return
