"""
MicroPython Tesla Coil Controller (MPTCC)
by Cameron Prince
teslauniverse.com

menu.py
Provides menu functionality.
Based on https://github.com/plugowski/umenu
"""

try:
    from display import CENTER, RIGHT
except ImportError:
    CENTER = 1
    RIGHT = 2

class MenuItem:
    """
    Represents a generic item in the menu.

    Attributes:
    -----------
    name : str
        The name of the menu item.
    decorator : str
        The decorator string for the menu item.
    visible : bool or callable
        Determines if the menu item is visible.
    """

    def __init__(self, name: str, decorator=None, visible=None):
        self.parent = None
        self._visible = True if visible is None else visible
        self.is_active = False
        self.name = name
        self.decorator = '' if decorator is None else decorator

    @property
    def visible(self):
        """Returns the visibility status of the menu item."""
        return self._visible if not self._check_callable(self._visible, False) else self._call_callable(self._visible)

    def click(self):
        """Defines the action to take when the menu item is clicked."""
        raise NotImplementedError()

    def get_decorator(self):
        """Returns the decorator string for the menu item."""
        return self.decorator if not callable(self.decorator) else self.decorator()

    @staticmethod
    def _check_callable(param, raise_error=True):
        """Checks if a parameter is callable."""
        if not (callable(param) or (type(param) is tuple and callable(param[0]))):
            if raise_error:
                raise ValueError('callable param should be callable or tuple with callable on first place!')
            else:
                return False
        return True

    @staticmethod
    def _call_callable(func, *args):
        """Calls a callable parameter."""
        if callable(func):
            return func(*args)
        elif type(func) is tuple and callable(func[0]):
            in_args = func[1] if type(func[1]) is tuple else (func[1],)
            return func[0](*tuple(list(in_args) + list(args)))

class SubMenuItem(MenuItem):
    """
    Represents a submenu item in the menu.

    Attributes:
    -----------
    name : str
        The name of the submenu item.
    decorator : str
        The decorator string for the submenu item.
    visible : bool or callable
        Determines if the submenu item is visible.
    menu : MenuScreen
        The menu screen associated with the submenu item.
    """

    def __init__(self, name, decorator=None, visible=None):
        super().__init__(name, '>' if decorator is None else decorator, visible)
        self.menu = MenuScreen(name, None)

    def click(self):
        """Defines the action to take when the submenu item is clicked."""
        pass

    def add(self, item, parent=None) -> 'SubMenuItem':
        """Adds a menu item to the submenu."""
        self.menu.add(item, parent)
        return self

    def reset(self):
        """Resets the submenu."""
        self.menu.reset()

class CustomItem(MenuItem):
    """
    Represents a custom item in the menu.

    Attributes:
    -----------
    name : str
        The name of the custom item.
    visible : bool or callable
        Determines if the custom item is visible.
    display : object
        The display object associated with the custom item.
    """

    def __init__(self, name, visible=None):
        super().__init__(name, visible=visible)
        self.display = None  # it is set after initialization via Menu._update_display()

    def click(self):
        """Defines the action to take when the custom item is clicked."""
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
    _visible_items : list
        The list of visible menu items in the menu screen.
    """

    def __init__(self, title: str, parent=None):
        self._items = []
        self._visible_items = []
        self.selected = 0
        self.parent = parent
        self.title = title

    def add(self, item, parent=None):
        """Adds a menu item to the menu screen."""
        item.parent = self if parent is None else parent
        if type(item) is SubMenuItem:
            item.menu.parent = self if parent is None else parent
        self._items.append(item)
        return self

    def reset(self):
        """Resets the menu screen."""
        self._items = []

    def count(self) -> int:
        """Returns the count of visible menu items."""
        elements = 0
        self._visible_items = []
        for item in self._items:
            if item.visible:
                elements += 1
                self._visible_items.append(item)
        return elements + (1 if self.parent is not None else 0)

    def up(self) -> None:
        """Moves the selection up."""
        if self.selected > 0:
            self.selected = self.selected - 1

    def down(self) -> None:
        """Moves the selection down."""
        if self.selected + 1 < self.count():
            self.selected = self.selected + 1

    def get(self, position):
        """Gets the menu item at the specified position."""
        if position < 0 or position + 1 > self.count():
            return None

        if position + 1 == self.count() and self.parent is not None:
            item = BackItem(self.parent)
        else:
            item = self._visible_items[position]

        item.is_active = position == self.selected
        return item

    def select(self) -> None:
        """Selects the current menu item."""
        item = self.get(self.selected)
        if type(item) is BackItem:
            self.selected = 0

        if type(item) is SubMenuItem:
            return item.menu
        else:
            # do action and return current menu
            return item.click()

class Menu:
    """
    Represents the main menu.

    Attributes:
    -----------
    display : object
        The display object for rendering the menu.
    per_page : int
        The number of items per page.
    line_height : int
        The height of each line in the menu.
    font_width : int
        The width of the font used in the menu.
    font_height : int
        The height of the font used in the menu.
    main_screen : MenuScreen
        The main screen of the menu.
    current_screen : MenuScreen or CustomItem
        The current screen being displayed.
    """

    current_screen = None  # type: MenuScreen | CustomItem

    def __init__(self, display, per_page: int = 4, line_height: int = 14, font_width: int = 8, font_height: int = 8):
        # todo: replace display and specific driver to framebuf
        self.display = display
        self.per_page = per_page
        self.line_height = line_height
        self.font_height = font_height
        self.font_width = font_width
        self.main_screen = None

    def set_screen(self, screen: MenuScreen):
        """Sets the current screen."""
        self.current_screen = screen
        if self.main_screen is None:
            self.main_screen = screen
            self._update_display(screen._items)

    def move(self, direction: int = 1):
        """Moves the selection in the specified direction."""
        self.current_screen.up() if direction < 0 else self.current_screen.down()
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
        if isinstance(self.current_screen, CustomItem):
            self.current_screen.draw()
            return

        self.display.fill(0)

        self._menu_header(self.current_screen.title)

        elements = self.current_screen.count()
        start = self.current_screen.selected - self.per_page + 1 if self.current_screen.selected + 1 > self.per_page else 0
        end = start + self.per_page

        menu_pos = 0
        for i in range(start, min(end, elements)):
            self._item_line(self.current_screen.get(i), menu_pos)
            menu_pos += 1

        self.display.show()

    def _item_line(self, item: MenuItem, pos):
        """Draws a single menu item line on the display."""
        menu_y_end = 12
        y = menu_y_end + (pos * self.line_height)
        v_padding = int((self.line_height - self.font_height) / 2)
        background = int(item.is_active)

        self.display.fill_rect(0, y, self.display.width, self.line_height, background)

        if hasattr(self.display, 'rich_text'):
            self.display.rich_text(str.upper(item.name), 2, y + v_padding, int(not background))
            self.display.rich_text(str.upper(item.get_decorator()), None, y + v_padding, int(not background), align=RIGHT)
        else:
            self.display.text(item.name, 0, y + v_padding, int(not background))
            x_pos = self.display.width - (len(item.get_decorator()) * self.font_width) - 1
            self.display.text(item.get_decorator(), x_pos, y + v_padding, int(not background))

    def _menu_header(self, text):
        """Draws the menu header on the display."""
        x = int((self.display.width / 2) - (len(text) * self.font_width / 2))
        self.display.text(str.upper(self.current_screen.title), x, 0, 1)
        self.display.hline(0, self.font_height + 2, self.display.width, 1)

    def _update_display(self, menu_items):
        """
        Adds the display object to all CustomItems, as it can be useful there to draw custom screens.
        """
        for obj in menu_items:
            if isinstance(obj, CustomItem):
                obj.display = self.display
            if isinstance(obj, SubMenuItem):
                self._update_display(obj.menu._items)

    def get_current_screen(self):
        """Returns the current screen."""
        return self.current_screen