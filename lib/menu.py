"""
MicroPython Tesla Coil Controller (MPTCC)
by Cameron Prince
teslauniverse.com

menu.py
Provides menu functionality.
Based on https://github.com/plugowski/umenu
"""

from ..hardware.display.display import Display


class MenuItem:
    """
    Represents a generic item in the menu.

    Attributes:
    -----------
    name : str
        The name of the menu item.
    decorator : str or callable
        The decorator string for the menu item.
    """

    def __init__(self, name: str, decorator=None):
        self.parent = None
        self.is_active = False
        self.name = name
        self.decorator = decorator if decorator is not None else ''

    def click(self):
        """Defines the action to take when the menu item is clicked."""
        raise NotImplementedError()

    def get_decorator(self):
        """Returns the decorator string for the menu item."""
        return self.decorator() if callable(self.decorator) else self.decorator


class SubMenuItem(MenuItem):
    """
    Represents a submenu item in the menu.

    Attributes:
    -----------
    name : str
        The name of the submenu item.
    decorator : str or callable
        The decorator string for the submenu item.
    menu : MenuScreen
        The menu screen associated with the submenu item.
    """

    def __init__(self, name, decorator=None):
        super().__init__(name, '>' if decorator is None else decorator)
        self.menu = MenuScreen(name, None)

    def click(self):
        """Defines the action to take when the submenu item is clicked."""
        return self.menu

    def add(self, item, parent=None) -> 'SubMenuItem':
        """Adds a menu item to the submenu."""
        self.menu.add(item, parent)
        return self

    def reset(self):
        """Resets the submenu."""
        self.menu.reset()


class Screen(MenuItem):
    """
    Represents a screen linked in the menu.

    Attributes:
    -----------
    name : str
        The name of the screen.
    display : object
        The display object associated with the screen.
    """

    def __init__(self, name):
        super().__init__(name)
        self.display = None

    def click(self):
        """Defines the action to take when the screen menu item is clicked."""
        return self

    def up(self):
        """Called when menu.move(-1) is called."""
        pass

    def down(self):
        """Called when menu.move(1) is called."""
        pass

    def select(self):
        """
        Called when menu.click() is called (on button press).
        Should return instance of MenuItem (usually self.parent to go level up or self to stay in current context).
        """
        raise NotImplementedError()

    def draw(self):
        """Called when someone clicks on the menu item."""
        raise NotImplementedError()


class BackItem(MenuItem):
    """
    Represents a back item in the menu.

    Attributes:
    -----------
    parent : MenuScreen
        The parent menu screen of the back item.
    label : str
        The label of the back item.
    """

    def __init__(self, parent, label='< BACK'):
        super().__init__(label)
        self.parent = parent

    def click(self):
        """Defines the action to take when the back item is clicked."""
        return self.parent


class MenuScreen:
    """
    Represents a screen in the menu.

    Attributes:
    -----------
    title : str
        The title of the menu screen.
    parent : MenuScreen
        The parent menu screen.
    selected : int
        The index of the selected menu item.
    _items : list
        The list of menu items in the menu screen.
    """

    def __init__(self, title: str, parent=None):
        self._items = []
        self.selected = 0
        self.parent = parent
        self.title = title

    def add(self, item, parent=None):
        """Adds a menu item to the menu screen."""
        item.parent = self if parent is None else parent
        if isinstance(item, SubMenuItem):
            item.menu.parent = self if parent is None else parent
        self._items.append(item)
        return self

    def reset(self):
        """Resets the menu screen."""
        self._items = []

    def count(self) -> int:
        """Returns the count of menu items."""
        return len(self._items) + (1 if self.parent is not None else 0)

    def up(self) -> None:
        """Moves the selection up."""
        if self.selected > 0:
            self.selected -= 1

    def down(self) -> None:
        """Moves the selection down."""
        if self.selected + 1 < self.count():
            self.selected += 1

    def get(self, position):
        """Gets the menu item at the specified position."""
        if position < 0 or position + 1 > self.count():
            return None

        if position + 1 == self.count() and self.parent is not None:
            item = BackItem(self.parent)
        else:
            item = self._items[position]

        item.is_active = position == self.selected
        return item

    def select(self):
        """Selects the current menu item."""
        item = self.get(self.selected)
        if isinstance(item, BackItem):
            self.selected = 0
            return item.click()
        elif isinstance(item, SubMenuItem):
            return item.click()
        else:
            return item.click()

    def draw(self, menu):
        """Draws the menu screen on the display."""
        menu._menu_header(self.title)

        elements = self.count()
        start = self.selected - menu.per_page + 1 if self.selected + 1 > menu.per_page else 0
        end = start + menu.per_page

        menu_pos = 0
        for i in range(start, min(end, elements)):
            menu._item_line(self.get(i), menu_pos)
            menu_pos += 1

        menu.display.show()


class Menu:
    """
    Represents the main menu.

    Attributes:
    -----------
    init : Init
        The global init object containing hardware instances.
    """

    def __init__(self, display):
        self.display = display
        self.display_width = self.display.width
        self.per_page = self.display.items_per_page
        self.line_height = self.display.line_height
        self.font_height = self.display.font_height
        self.font_width = self.display.font_width
        self.main_screen = None
        self.current_screen = None

    def set_screen(self, screen):
        """Sets the current screen."""
        self.current_screen = screen
        if self.main_screen is None:
            self.main_screen = screen
            self._update_display(screen._items)

    def move(self, direction: int = 1):
        """Moves the selection in the specified direction."""
        if direction < 0:
            self.current_screen.up()
        else:
            self.current_screen.down()
        self.draw()

    def click(self):
        """Clicks the current menu item."""
        self.current_screen = self.current_screen.select()
        if self.current_screen is not None:
            self.draw()

    def reset(self):
        """Resets the menu to the main screen."""
        self.current_screen = self.main_screen
        self.current_screen.selected = 0
        self.draw()

    def draw(self):
        """Draws the menu on the display."""
        if isinstance(self.current_screen, MenuScreen):
            # Call MenuScreen's draw method with the menu argument.
            self.current_screen.draw(self)
        elif isinstance(self.current_screen, Screen):
            # Call screen's draw method without the menu argument.
            self.current_screen.draw()
        else:
            raise TypeError("Unsupported screen type")

    def _item_line(self, item: MenuItem, pos):
        """Draws a single menu item line on the display."""
        menu_y_end = 12
        y = menu_y_end + (pos * self.line_height)
        v_padding = int((self.line_height - self.font_height) / 2)
        background = int(item.is_active)

        self.display.fill_rect(0, y, self.display_width, self.line_height, background)

        self.display.text(item.name, 0, y + v_padding, int(not background))
        decorator_text = item.get_decorator()
        if decorator_text:
            x_pos = min(self.display_width - (len(decorator_text) * self.font_width) - 1, 255)
            self.display.text(decorator_text, x_pos, y + v_padding, int(not background))

    def _menu_header(self, text):
        """Draws the menu header on the display."""
        x = int((self.display_width / 2) - (len(text) * self.font_width / 2))
        self.display.text(str.upper(self.current_screen.title), x, 0, 1)
        self.display.hline(0, self.font_height + 2, self.display_width, 1)

    def _update_display(self, menu_items):
        """
        Adds the display object to all screens.
        """
        for obj in menu_items:
            if isinstance(obj, Screen):
                obj.display = self.display
            if isinstance(obj, SubMenuItem):
                self._update_display(obj.menu._items)

    def get_current_screen(self):
        """Returns the current screen."""
        return self.current_screen
