"""Solve meowdoku"""

import logging
import time
import pygame
import meowdoku

SOLARIZED_BASE03 = (0,43,54)
SOLARIZED_BASE02 = (7,54,66)
SOLARIZED_BASE01 = (88,110,117)
SOLARIZED_BASE00 = (101,123,131)
SOLARIZED_BASE0 = (131,148,150)
SOLARIZED_BASE1 = (147,161,161)
SOLARIZED_BASE2 = (238,232,213)
SOLARIZED_BASE3 = (253,246,227)
SOLARIZED_YELLOW = (181,137,0)
SOLARIZED_ORANGE = (203,75,22)
SOLARIZED_RED = (220,50,47)
SOLARIZED_MAGENTA = (211,54,130)
SOLARIZED_VIOLET = (108,113,196)
SOLARIZED_BLUE = (38,139,210)
SOLARIZED_CYAN = (42,161,152)
SOLARIZED_GREEN = (133,153,0)

CELL_THICKNESS = 3
GRID_THICKNESS = 3
AREA_THICKNESS = 3
SELECTED_THICKNESS = 3

CELL_WIDTH = 20
CELL_HEIGHT = 20
SUB_WIDTH = (CELL_WIDTH*3*3)+(CELL_THICKNESS*2)
SUB_HEIGHT = (CELL_HEIGHT*3*3)+(CELL_THICKNESS*2)

COL_WHITE = (255,255,255)
COL_LINE = SOLARIZED_BASE01
COL_BACK = SOLARIZED_BASE03
COL_BACK2 = SOLARIZED_BASE03
COL_TEXT0 = SOLARIZED_BASE2
COL_TEXT1 = SOLARIZED_BASE1
COL_TEXT2 = SOLARIZED_BLUE
COL_TEXT3 = SOLARIZED_GREEN
COL_CHECK = SOLARIZED_BASE02
COL_CHECKING = SOLARIZED_MAGENTA
COL_AREA = SOLARIZED_YELLOW

if CELL_THICKNESS%2 == 0:
    raise Exception("CELL_THICKNESS must be odd")
if GRID_THICKNESS%2 == 0:
    raise Exception("GRID_THICKNESS must be odd")

def get_left_for_cell_index(cell_x_index: int):
    """Calculate the left pixel for the cell x index."""
    return ((CELL_WIDTH*cell_x_index)+
            (cell_x_index*CELL_THICKNESS)+
            ((cell_x_index)*(GRID_THICKNESS-CELL_THICKNESS)))

def get_top_for_cell_index(cell_y_index: int):
    """Calculate the top pixel for the cell y index."""
    return ((CELL_HEIGHT*cell_y_index)+
            (cell_y_index*CELL_THICKNESS)+
            ((cell_y_index)*(GRID_THICKNESS-CELL_THICKNESS)))

def get_width(x: int):
    return (CELL_WIDTH*x)+((x-1)*CELL_THICKNESS)+(2*(GRID_THICKNESS-CELL_THICKNESS))

def get_height(y: int):
    return (CELL_HEIGHT*y)+((y-1)*CELL_THICKNESS)+(2*(GRID_THICKNESS-CELL_THICKNESS))

class App:
    """Represents the pygame application."""
    def __init__(self, data, delay: float) -> None:
        self._delay = delay
        self._grid = meowdoku.Grid(data)

        self._row_count = len(self._grid._cells)
        self._col_count = len(self._grid._cells[0])

        self._running = True
        self._display_surf = None
        self._size = (get_width(self._col_count), get_height(self._row_count))
        self._time = time.time()
        self._counter = 0
        self._checking = 0
        self._render_check = True
        self._render_selected = True
        self._font_s = None
        self._font_l = None
        self._complete = False

    def is_complete(self) -> bool:
        """Check if is complete"""
        return self._complete
    def on_init(self) -> bool:
        """Initialise solver."""
        pygame.init()
        pygame.display.set_caption("Meowdoku")
        self._display_surf = pygame.display.set_mode(self._size,
                                                     pygame.HWSURFACE | pygame.DOUBLEBUF)
        self._running = True
        font_name = pygame.font.get_default_font()
        logging.info("System font: %s", font_name)
        self.font_s = pygame.font.SysFont(None, 22)
        self.font_l = pygame.font.SysFont(None, 66)
        return True
    def on_event(self, event: pygame.event.Event) -> None:
        """Process the pygame events."""
        if event.type == pygame.QUIT:
            self._running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == 27:
                self._running = False
        else:
            logging.debug(event)
    def on_loop(self, elapsed: float) -> None:
        """When counter elapses check."""
        self._counter+=elapsed
        if self._counter > self._delay:
            logging.info("tick")
            self._counter = 0
            if not self._complete:
                if self.check_grid():
                    self._complete = True
                    if self._exit_on_complete:
                        self._running = False
    def check_grid(self) -> bool:
        """Check the grid"""
        return False
    def on_render(self) -> None:
        """Render the game."""
        self._display_surf.fill(COL_WHITE)
        self.draw_cells()
        # self.draw_lines()
        # self.draw_checking()
        # self.draw_numbers()
        # self.draw_checking_area()
        # self.draw_selected_cell()
        pygame.display.update()
    def draw_cells(self) -> None:
        """Draw all the cells."""
        for row in range(0, self._row_count):
            for col in range(0, self._col_count):
                self.draw_cell(row, col)
    def draw_cell(self, row: int, col: int) -> None:
        """Draw a single cell for (row, col)."""
        cell = self._grid._cells[row][col]

        colours = {
            1: (76,182,176),
            2: (174,217,148),
            3: (255,170,109),
            4: (237,141,182),
            5: (153,121,214),
            6: (250,181,208),
            7: (167,191,215),
            8: (107,188,231),
            9: (228,187,73),
        }

        left = get_left_for_cell_index(col)
        top = get_top_for_cell_index(row)
        width = CELL_WIDTH
        height = CELL_HEIGHT
        pygame.draw.rect(self._display_surf, colours[cell._num], (left, top, width, height), 0)
    def on_cleanup(self) -> None:
        """Cleanup."""
        pygame.quit()
    def on_execute(self) -> None:
        """Execute application."""
        if not self.on_init():
            self._running = False
        while self._running:
            current = time.time()
            elapsed = current - self._time
            self._time = current
            for event in pygame.event.get():
                self.on_event(event)
            self.on_loop(elapsed)
            self.on_render()
        self.on_cleanup()