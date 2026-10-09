"""Solve meowdoku"""

import logging
import time
import pygame
from meowdoku import Grid, Cell, Position

CELL_THICKNESS = 3
GRID_THICKNESS = 3

CELL_WIDTH = 40
CELL_HEIGHT = 40

COL_WHITE = (255,255,255)

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

def get_width(x: int): # TODO: maybe we should make the width dynamic and scale eveything to fit?
    """get calculated window width"""
    return (CELL_WIDTH*x)+((x-1)*CELL_THICKNESS)+(2*(GRID_THICKNESS-CELL_THICKNESS))

def get_height(y: int): # TODO: maybe we should make the height dynamic and scale eveything to fit?
    """get calculated window height"""
    return (CELL_HEIGHT*y)+((y-1)*CELL_THICKNESS)+(2*(GRID_THICKNESS-CELL_THICKNESS))

def print_colour(colour_id: int, text: str):
    """print the text using rgb colour"""
    r = colours[colour_id][0]
    g = colours[colour_id][1]
    b = colours[colour_id][2]
    print(f'\033[38;2;{r};{g};{b}m{text}\033[0m')

class App:
    """Represents the pygame application."""
    def __init__(self, data, delay: float) -> None:
        self._delay: float = delay
        self._grid: Grid = Grid(data)

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
        self.font_s = None
        self.font_l = None

    def is_complete(self) -> bool:
        """Check if is complete"""
        return self._complete
    def on_init(self) -> bool:
        """Initialise solver."""
        pygame.init()
        pygame.display.set_caption("Meowdoku")
        self._display_surf = pygame.display.set_mode(self._size, pygame.HWSURFACE | pygame.DOUBLEBUF)
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
    def _set_cat(self, _x: int, _y: int) -> bool:
        """Set the cell to contain a cat"""
        steps_taken = False
        if self._grid._cells[_y][_x].is_cat() is False:
            self._grid._cells[_y][_x]._cat = True
            steps_taken = True
        return steps_taken
    def _cross_cells(self, cells: list[Position]) -> None:
        """Cross all cells in provided list"""
        for coord in cells:
            self._grid._cells[coord.y][coord.x]._cross = True
    def _get_cross_row(self, x: int, y: int, colour_id: int) -> list[Position]:
        """Get all the cells in a row that are not a cross or a cat"""
        cells: list[Position] = []
        for _x in range(len(self._grid._cells[0])):
            if _x != x:
                if self._grid._cells[y][_x].is_cross() is False and self._grid._cells[y][_x].is_cat() is False and self._grid._cells[y][_x].num() != colour_id:
                    cells.append(Position(_x, y))
        return cells
    def _cross_row(self, x: int, y: int, colour_id: int) -> bool:
        """Cross all cells in row that are not cross or cat"""
        cells: list[Position] = self._get_cross_row(x, y, colour_id)
        self._cross_cells(cells)
        return len(cells) > 0
    def _get_cross_col(self, x: int, y: int, colour_id: int) -> list[Position]:
        """Get all the cells in a col that are not a cross or a cat"""
        cells: list[Position] = []
        for _y in range(len(self._grid._cells)): # pylint: disable=consider-using-enumerate
            if _y != y:
                if self._grid._cells[_y][x].is_cross() is False and self._grid._cells[_y][x].is_cat() is False and self._grid._cells[_y][x].num() != colour_id:
                    cells.append(Position(x, _y))
        return cells
    def _cross_col(self, x: int ,y: int, colour_id: int) -> bool:
        """Cross all cells in a col that are not a cross or a cat"""
        cells: list[Position] = self._get_cross_col(x, y, colour_id)
        self._cross_cells(cells)
        return len(cells) > 0
    def _get_cross_around(self, x: int, y: int) -> list[Position]:
        """Get all the cells around a cell that are not a cross or a cat"""
        cells: list[Position] = []
        for _y in range(y-1, y+2):
            for _x in range(x-1, x+2):
                if (_x != x or _y != y) and _x >= 0 and _x < self._col_count and _y >=0 and _y < self._row_count:
                    if self._grid._cells[_y][_x].is_cross() is False and self._grid._cells[_y][_x].is_cat() is False:
                        cells.append(Position(_x, _y))
        return cells
    def _cross_around(self, x: int, y: int) -> bool:
        """Cross all cells around the cell that are not cross or cat"""
        cells = self._get_cross_around(x, y)
        self._cross_cells(cells)
        return len(cells) > 0
    def check_grid(self) -> bool:
        """Check the grid"""
        steps_taken = False

        if not steps_taken:
            # check for colours with cats that need crossing
            colour_ids: list[int] = self._grid.get_colour_ids_with_cat()
            colour_coords: dict[int, list[Position]] = self._grid.get_available_coords(colour_ids)
            for colour_id in colour_coords.keys(): # pylint: disable=consider-using-dict-items
                print_colour(colour_id, f"{colour_id} has a cat and needs crossing")
                self._cross_cells(colour_coords[colour_id])
                steps_taken = True

        if not steps_taken:
            # check for colours with only 1 cell available
            colour_coords: dict[int, list[Position]] = self._grid.get_available_coords()
            for colour_id in colour_coords.keys(): # pylint: disable=consider-using-dict-items
                if len(colour_coords[colour_id]) == 1:
                    print_colour(colour_id, f"{colour_id} is single")
                    coord: Position = colour_coords[colour_id][0]
                    if self._set_cat(coord.x, coord.y):
                        steps_taken = True
                    if self._cross_around(coord.x, coord.y):
                        steps_taken = True
                    if self._cross_row(coord.x, coord.y, self._grid._cells[coord.y][coord.x].num()):
                        steps_taken = True
                    if self._cross_col(coord.x, coord.y, self._grid._cells[coord.y][coord.x].num()):
                        steps_taken = True

        if not steps_taken:
            # check for colours with only 1 dimension available (row/col)
            colour_coords: dict[int, list[Position]] = self._grid.get_available_coords()
            for colour_id in colour_coords.keys(): # pylint: disable=consider-using-dict-items
                x_vals = []
                y_vals = []
                for coord in colour_coords[colour_id]:
                    if coord.x not in x_vals:
                        x_vals.append(coord.x)
                    if coord.y not in y_vals:
                        y_vals.append(coord.y)
                if (len(x_vals) == 1) ^ (len(y_vals) == 1): # XOR (only one or other, not both, both would indicate a single cell) Maybe we can combine this check with check for single cell
                    if len(x_vals) == 1:
                        # is a single column
                        print_colour(colour_id, f"{colour_id} is col")
                        if self._cross_col(coord.x, coord.y, colour_id):
                            steps_taken = True
                    if len(y_vals) == 1:
                        # is a single row
                        print_colour(colour_id, f"{colour_id} is row")
                        if self._cross_row(coord.x, coord.y, colour_id):
                            steps_taken = True

        if not steps_taken:
            # check each colour for external cells that are always excluded
            colour_coords: dict[int, list[Position]] = self._grid.get_available_coords()
            for colour_id in colour_coords.keys(): # pylint: disable=consider-using-dict-items
                consistent_cells = None
                for coord in colour_coords[colour_id]:
                    c = set(self._get_cross_around(coord.x, coord.y)).union(set(self._get_cross_row(coord.x, coord.y, colour_id)).union(set(self._get_cross_col(coord.x, coord.y, colour_id))))
                    if consistent_cells is None:
                        consistent_cells = c
                    else:
                        consistent_cells = consistent_cells.intersection(c)
                if len(consistent_cells) > 0:
                    print_colour(colour_id, f"{colour_id} has {len(consistent_cells)} consistent exclusions")
                    self._cross_cells(list(consistent_cells))
                    steps_taken = True


        # check for colours that are the only in a row

        # check for colours that are the only in a col

        return False
    def on_render(self) -> None:
        """Render the game."""
        self._display_surf.fill(COL_WHITE)
        self.draw_cells()
        pygame.display.update()
    def draw_cells(self) -> None:
        """Draw all the cells."""
        for row in range(0, self._row_count):
            for col in range(0, self._col_count):
                self.draw_cell(row, col)
    def draw_cell(self, row: int, col: int) -> None:
        """Draw a single cell for (row, col)."""
        cell = self._grid._cells[row][col]

        left = get_left_for_cell_index(col)
        top = get_top_for_cell_index(row)
        width = CELL_WIDTH
        height = CELL_HEIGHT
        pygame.draw.rect(self._display_surf, colours[cell._num], (left, top, width, height), 0)

        if cell._cross is True:
            pygame.draw.line(self._display_surf, COL_WHITE, (left,top), (left+width,top+height), 3)
            pygame.draw.line(self._display_surf, COL_WHITE, (left,top+height), (left+width,top), 3)

        if cell._cat is True:
            pygame.draw.circle(self._display_surf, COL_WHITE, (left+(width/2), top+(height/2)), CELL_WIDTH/2, 3)

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
