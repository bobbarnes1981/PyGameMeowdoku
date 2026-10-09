"""Solve meowdoku"""

import logging
import time
import pygame
from meowdoku import Grid, Cell, Position

CELL_THICKNESS = 3
GRID_THICKNESS = 3
CROSS_THICKNESS = 6
CAT_THICKNESS = 6

CELL_WIDTH = 40
CELL_HEIGHT = 40

COL_WHITE = (255,255,255)

colours = {
    1:  (76,182,176),
    2:  (174,217,148),
    3:  (255,170,109),
    4:  (237,141,182),
    5:  (153,121,214),
    6:  (250,181,208),
    7:  (167,191,215),
    8:  (107,188,231),
    9:  (228,187,73),
    10: (89,73,28)
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
        self._paused = False
        self._render_check = True
        self._render_selected = True
        self._font_s = None
        self._font_l = None
        self._complete = False
        self.font_s = None
        self.font_l = None
    def valid_coord(self, x, y) -> bool:
        """Check if coordinates are valid"""
        return x >= 0 and x < self._col_count and y >=0 and y < self._row_count
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
            elif event.key == 112:
                self._paused = not self._paused
        else:
            logging.debug(event)
    def on_loop(self, elapsed: float) -> None:
        """When counter elapses check."""
        self._counter+=elapsed
        if self._counter > self._delay:
            #logging.info("tick")
            self._counter = 0
            if not self._complete:
                if self._paused is False and self.check_grid():
                    self._complete = True
    def _set_cat(self, _x: int, _y: int) -> bool:
        """Set the cell to contain a cat"""
        steps_taken = False
        if self._grid._cells[_y][_x].is_cross() is True:
            raise Exception("Cannot set cat on crossed cell")
        if self._grid._cells[_y][_x].is_cat() is False:
            colour_id = self._grid._cells[_y][_x].num()
            print_colour(colour_id, f"setting cat for {colour_id} ({_x},{_y})")
            self._grid._cells[_y][_x]._cat = True
            steps_taken = True
        return steps_taken
    def _cross_cells(self, cells: list[Position]) -> None:
        """Cross all cells in provided list"""
        for coord in cells:
            if self._grid._cells[coord.y][coord.x].is_cross():
                raise Exception("Cell is already crossed")
            if self._grid._cells[coord.y][coord.x].is_cat():
                raise Exception("Cannot set cross on cat cell")
            self._grid._cells[coord.y][coord.x]._cross = True
    def _get_cross_row(self, x: int, y: int, colour_ids: list[int]) -> list[Position]:
        """Get all the cells in a row that are not a cross or a cat"""
        cells: list[Position] = []
        for _x in range(len(self._grid._cells[0])):
            #if _x != x: # TODO: can we get rid of this? Already excluded?
            if self._grid._cells[y][_x].is_cross() is False and self._grid._cells[y][_x].is_cat() is False and self._grid._cells[y][_x].num() not in colour_ids:
                cells.append(Position(_x, y))
        return cells
    def _cross_row(self, x: int, y: int, colour_ids: list[int]) -> bool:
        """Cross all cells in row that are not cross or cat"""
        cells: list[Position] = self._get_cross_row(x, y, colour_ids)
        self._cross_cells(cells)
        return len(cells) > 0
    def _get_cross_col(self, x: int, y: int, colour_ids: list[int]) -> list[Position]:
        """Get all the cells in a col that are not a cross or a cat"""
        cells: list[Position] = []
        for _y in range(len(self._grid._cells)):
            #if _y != y:  # TODO: can we get rid of this? Already exlcuded?
            if self._grid._cells[_y][x].is_cross() is False and self._grid._cells[_y][x].is_cat() is False and self._grid._cells[_y][x].num() not in colour_ids:
                cells.append(Position(x, _y))
        return cells
    def _cross_col(self, x: int ,y: int, colour_ids: list[int]) -> bool:
        """Cross all cells in a col that are not a cross or a cat"""
        cells: list[Position] = self._get_cross_col(x, y, colour_ids)
        self._cross_cells(cells)
        return len(cells) > 0
    def _get_cross_around(self, x: int, y: int) -> list[Position]:
        """Get all the cells around a cell that are not a cross or a cat"""
        cells: list[Position] = []
        for _y in range(y-1, y+2):
            for _x in range(x-1, x+2):
                if (_x != x or _y != y) and self.valid_coord(_x, _y):
                    if self._grid._cells[_y][_x].is_cross() is False and self._grid._cells[_y][_x].is_cat() is False:
                        cells.append(Position(_x, _y))
        return cells
    def _cross_around(self, x: int, y: int) -> bool:
        """Cross all cells around the cell that are not cross or cat"""
        cells = self._get_cross_around(x, y)
        self._cross_cells(cells)
        return len(cells) > 0
    def _get_cross_colour(self, x: int, y: int) -> list[Position]:
        """Get all the cells of the colour in the identified cell"""
        cells: list[Position] = []
        for _y in range(self._row_count):
            for _x in range(self._col_count):
                if self._grid._cells[y][x].num() == self._grid._cells[_y][_x].num():
                    if self._grid._cells[_y][_x].is_cross() is False and self._grid._cells[_y][_x].is_cat() is False:
                        cells.append(Position(_x, _y))
        return cells
    def _cross_colour(self, x: int, y: int) -> bool:
        """Cross all the cells of the colour in the identified cell"""
        cells = self._get_cross_colour(x, y)
        self._cross_cells(cells)
        return len(cells) > 0
    def _check_for_cats(self) -> bool:
        """check for colours with cats that need crossing"""
        steps_taken = False
        locations: dict[int, Position] = self._grid.get_cat_locations()
        for colour_id in locations.keys(): # pylint: disable=consider-using-dict-items
            colour_steps = False
            coord: Position = locations[colour_id]
            if self._cross_colour(coord.x, coord.y):
                colour_steps = True
            if self._cross_around(coord.x, coord.y):
                colour_steps = True
            if self._cross_row(coord.x, coord.y, [self._grid._cells[coord.y][coord.x].num()]):
                colour_steps = True
            if self._cross_col(coord.x, coord.y, [self._grid._cells[coord.y][coord.x].num()]):
                colour_steps = True
            if colour_steps:
                steps_taken = True
                print_colour(colour_id, f"{colour_id} has a cat")
        return steps_taken
    def _check_for_single_cell_colours(self) -> bool:
        """check for colours with only 1 cell available"""
        steps_taken = False
        colour_coords: dict[int, list[Position]] = self._grid.get_available_coords([])
        for colour_id in colour_coords.keys(): # pylint: disable=consider-using-dict-items
            if len(colour_coords[colour_id]) == 1:
                print_colour(colour_id, f"{colour_id} is single")
                coord: Position = colour_coords[colour_id][0]
                if self._set_cat(coord.x, coord.y):
                    steps_taken = True
                if self._cross_around(coord.x, coord.y):
                    steps_taken = True
                if self._cross_row(coord.x, coord.y, [self._grid._cells[coord.y][coord.x].num()]):
                    steps_taken = True
                if self._cross_col(coord.x, coord.y, [self._grid._cells[coord.y][coord.x].num()]):
                    steps_taken = True
        return steps_taken
    def _check_for_colours_1_wide(self):
        """check for 1 colours with only 1 wide"""
        steps_taken = False
        colour_coords: dict[int, list[Position]] = self._grid.get_available_coords([])
        col_colours: dict[int, Position] = {}
        row_colours: dict[int, Position] = {}
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
                    print_colour(colour_id, f"{colour_id} is col ({x_vals[0]})")
                    col_colours[colour_id] = Position(x_vals[0], 0)
                if len(y_vals) == 1:
                    # is a single row
                    print_colour(colour_id, f"{colour_id} is row ({y_vals[0]})")
                    row_colours[colour_id] = Position(0, y_vals[0])
        for colour_id in col_colours.keys(): # pylint: disable=consider-using-dict-items
            # is a single column
            coord = col_colours[colour_id]
            if self._cross_col(coord.x, coord.y, [colour_id]):
                steps_taken = True
        for colour_id in row_colours.keys(): # pylint: disable=consider-using-dict-items
            # is a single row
            coord = row_colours[colour_id]
            if self._cross_row(coord.x, coord.y, [colour_id]):
                steps_taken = True
        return steps_taken
    def _check_for_2_colours_2_wide(self) -> bool:
        """check for 2 colours with 2 wide"""
        steps_taken = False
        colour_coords: dict[int, list[Position]] = self._grid.get_available_coords([])
        col_colours: dict[int, tuple[int, int]] = {}
        row_colours: dict[int, tuple[int, int]] = {}
        for colour_id in colour_coords.keys(): # pylint: disable=consider-using-dict-items
            x_vals = []
            y_vals = []
            for coord in colour_coords[colour_id]:
                if coord.x not in x_vals:
                    x_vals.append(coord.x)
                if coord.y not in y_vals:
                    y_vals.append(coord.y)
            if (len(x_vals) == 2) or (len(y_vals) == 2):
                if len(x_vals) == 2:
                    # two vals in x direction, 'col-like' structure
                    print_colour(colour_id, f"{colour_id} has col-like structure {x_vals[0]} {x_vals[1]}")
                    col_colours[colour_id] = (x_vals[0], x_vals[1])
                if len(y_vals) == 2:
                    # two vals in y direction, 'row-like' structure
                    print_colour(colour_id, f"{colour_id} has row-like structure {y_vals[0]} {y_vals[1]}")
                    row_colours[colour_id] = (y_vals[0], y_vals[1])
        # find sets of two with matching x_vals
        sets: list[tuple[tuple[int, int], tuple[int, int]]] = []
        for colour_id1 in col_colours.keys(): # pylint: disable=consider-using-dict-items
            for colour_id2 in col_colours.keys(): # pylint: disable=consider-using-dict-items
                if colour_id1 != colour_id2:
                    x_vals1 = col_colours[colour_id1]
                    x_vals2 = col_colours[colour_id2]
                    if x_vals1[0] == x_vals2[0] and x_vals1[1] == x_vals2[1]: # TODO: this might not work if the numbers are not in the same order
                        sets.append(((colour_id1, colour_id2), (x_vals1[0], x_vals1[1])))
        for exclusion in sets:
            colour_id1 = exclusion[0][0]
            colour_id2 = exclusion[0][1]
            x1 = exclusion[1][0]
            x2 = exclusion[1][1]
            print_colour(colour_id1, f"{colour_id1} excludes {x1} {x2}")
            print_colour(colour_id2, f"{colour_id2} excludes {x1} {x2}")
            if self._cross_col(x1, 0, [colour_id1, colour_id2]):
                steps_taken = True
            if self._cross_col(x2, 0, [colour_id1, colour_id2]):
                steps_taken = True
        # find sets of two with matching y_vals
        sets: list[tuple[tuple[int, int], tuple[int, int]]] = []
        for colour_id1 in row_colours.keys(): # pylint: disable=consider-using-dict-items
            for colour_id2 in row_colours.keys(): # pylint: disable=consider-using-dict-items
                if colour_id1 != colour_id2:
                    y_vals1 = row_colours[colour_id1]
                    y_vals2 = row_colours[colour_id2]
                    if y_vals1[0] == y_vals2[0] and y_vals1[1] == y_vals2[1]: # TODO: this might not work if the numbers are not in the same order
                        sets.append(((colour_id1, colour_id2), (y_vals1[0], y_vals1[1])))
        for exclusion in sets:
            colour_id1 = exclusion[0][0]
            colour_id2 = exclusion[0][1]
            y1 = exclusion[1][0]
            y2 = exclusion[1][1]
            print_colour(colour_id1, f"{colour_id1} excludes {y1} {y2}")
            print_colour(colour_id2, f"{colour_id2} excludes {y1} {y2}")
            if self._cross_row(0, y1, [colour_id1, colour_id2]):
                steps_taken = True
            if self._cross_row(0, y2, [colour_id1, colour_id2]):
                steps_taken = True
        return steps_taken
    def _check_for_consistent_exclusions(self) -> bool:
        """check each colour for external cells that are always excluded"""
        steps_taken = False
        colour_coords: dict[int, list[Position]] = self._grid.get_available_coords([])
        for colour_id in colour_coords.keys(): # pylint: disable=consider-using-dict-items
            all_cells: list[Position] = []
            for _y in range(self._row_count):
                for _x in range(self._col_count):
                    all_cells.append(Position(_x, _y))
            consistent_cells:set = set(all_cells)
            for coord in colour_coords[colour_id]:
                c = set(self._get_cross_around(coord.x, coord.y)).union(set(self._get_cross_row(coord.x, coord.y, [colour_id])).union(set(self._get_cross_col(coord.x, coord.y, [colour_id]))))
                consistent_cells = consistent_cells.intersection(c)
            if len(consistent_cells) > 0:
                c_str = ",".join([f"({c.x},{c.y})" for c in consistent_cells])
                print_colour(colour_id, f"{colour_id} has {len(consistent_cells)} consistent exclusions: {c_str}")
                self._cross_cells(list(consistent_cells))
                steps_taken = True
        return steps_taken
    def _check_impossible_rows_2(self) -> bool:
        """find rows with two free spaces and exclude placements that make the row impossible"""
        steps_taken = False
        coord_list: list[list[Position]] = self._grid.get_coords_for_rows_with_only_n_space(2)
        for coords in coord_list:
            x_str = ",".join([str(c.x) for c in coords])
            print(f"row {coords[0].y} has spaces at {x_str}")
            cells:list[Position] = []
            # check coords[0].y-1 at coords[0].x
            x = coords[0].x
            y = coords[0].y-1
            if self.valid_coord(x, y):
                cell = self._grid._cells[y][x]
                if cell.is_cat() is False and cell.is_cross() is False:
                    cells.append(Position(x, y))
            # check coords[1].y-1 at coords[1].x
            x = coords[1].x
            y = coords[1].y-1
            if self.valid_coord(x, y):
                cell = self._grid._cells[y][x]
                if cell.is_cat() is False and cell.is_cross() is False:
                    cells.append(Position(x, y))
            # check coords[0].y+1 at coords[0].x
            x = coords[0].x
            y = coords[0].y+1
            if self.valid_coord(x, y):
                cell = self._grid._cells[y][x]
                if cell.is_cat() is False and cell.is_cross() is False:
                    cells.append(Position(x, y))
            # check coords[1].y+1 at coords[1].x
            x = coords[1].x
            y = coords[1].y+1
            if self.valid_coord(x, y):
                cell = self._grid._cells[y][x]
                if cell.is_cat() is False and cell.is_cross() is False:
                    cells.append(Position(x, y))
            for cell in cells:
                print(f"excluding cell {cell.x},{cell.y}")
                self._cross_cells([cell])
                steps_taken = True
        return steps_taken
    def _check_impossible_cols_2(self) -> bool:
        """find cols with two free spaces and exclude placements that make the col impossible"""
        steps_taken = False
        coord_list: list[list[Position]] = self._grid.get_coords_for_cols_with_only_n_space(2)
        for coords in coord_list:
            y_str = ",".join([str(c.y) for c in coords])
            print(f"col {coords[0].x} has spaces at {y_str}")
            cells:list[Position] = []
            # check coords[0].x-1 at coords[0].y
            x = coords[0].x-1
            y = coords[0].y
            if self.valid_coord(x, y):
                cell = self._grid._cells[y][x]
                if cell.is_cat() is False and cell.is_cross() is False:
                    cells.append(Position(x, y))
            # check coords[1].x-1 at coords[1].y
            x = coords[1].x-1
            y = coords[1].y
            if self.valid_coord(x, y):
                cell = self._grid._cells[y][x]
                if cell.is_cat() is False and cell.is_cross() is False:
                    cells.append(Position(x, y))
            # check coords[0].x+1 at coords[0].y
            x = coords[0].x+1
            y = coords[0].y
            if self.valid_coord(x, y):
                cell = self._grid._cells[y][x]
                if cell.is_cat() is False and cell.is_cross() is False:
                    cells.append(Position(x, y))
            # check coords[1].x+1 at coords[1].y
            x = coords[1].x+1
            y = coords[1].y
            if self.valid_coord(x, y):
                cell = self._grid._cells[y][x]
                if cell.is_cat() is False and cell.is_cross() is False:
                    cells.append(Position(x, y))
            for cell in cells:
                print(f"excluding cell {cell.x},{cell.y}")
                self._cross_cells([cell])
                steps_taken = True
        return steps_taken
    def _check_impossible_rows_3(self) -> bool:
        """find rows with three free spaces and exclude placements that make the row impossible"""
        steps_taken = False
        coord_list: list[list[Position]] = self._grid.get_coords_for_rows_with_only_n_space(3)
        for coords in coord_list:
            x_str = ",".join([str(c.x) for c in coords])
            print(f"row {coords[0].y} has spaces at {x_str}")
            cells:list[Position] = []
            # check coords[1].y-1 at coords[1].x
            x = coords[1].x
            y = coords[1].y-1
            if self.valid_coord(x, y):
                cell = self._grid._cells[y][x]
                if cell.is_cat() is False and cell.is_cross() is False:
                    cells.append(Position(x, y))
            # check coords[1].y+1 at coords[1].x
            x = coords[1].x
            y = coords[1].y+1
            if self.valid_coord(x, y):
                cell = self._grid._cells[y][x]
                if cell.is_cat() is False and cell.is_cross() is False:
                    cells.append(Position(x, y))
            for cell in cells:
                print(f"excluding cell {cell.x},{cell.y}")
                self._cross_cells([cell])
                steps_taken = True
        return steps_taken
    def _check_impossible_cols_3(self) -> bool:
        """find cols with three free spaces and exclude placements that make the col impossible"""
        steps_taken = False
        coord_list: list[list[Position]] = self._grid.get_coords_for_cols_with_only_n_space(3)
        for coords in coord_list:
            y_str = ",".join([str(c.y) for c in coords])
            print(f"col {coords[0].x} has spaces at {y_str}")
            cells:list[Position] = []
            # check coords[0].x-1 at coords[1].y
            x = coords[1].x-1
            y = coords[1].y
            if self.valid_coord(x, y):
                cell = self._grid._cells[y][x]
                if cell.is_cat() is False and cell.is_cross() is False:
                    cells.append(Position(x, y))
            # check coords[0].x+1 at coords[1].y
            x = coords[1].x+1
            y = coords[1].y
            if self.valid_coord(x, y):
                cell = self._grid._cells[y][x]
                if cell.is_cat() is False and cell.is_cross() is False:
                    cells.append(Position(x, y))
            for cell in cells:
                print(f"excluding cell {cell.x},{cell.y}")
                self._cross_cells([cell])
                steps_taken = True
        return steps_taken
    def _check_single_cell_rows(self) -> bool:
        """check for rows with single cell left"""
        steps_taken = False
        coord_list: list[list[Position]] = self._grid.get_coords_for_rows_with_only_n_space(1)
        for coords in coord_list:
            x_str = ",".join([str(c.x) for c in coords])
            coord = coords[0]
            colour_id = self._grid._cells[coord.y][coord.x].num()
            print_colour(colour_id, f"row {coord.y} has space at {x_str}")
            self._set_cat(coord.x, coord.y)
            if self._cross_colour(coord.x, coord.y):
                steps_taken = True
            if self._cross_around(coord.x, coord.y):
                steps_taken = True
            if self._cross_row(coord.x, coord.y, [self._grid._cells[coord.y][coord.x].num()]):
                steps_taken = True
            if self._cross_col(coord.x, coord.y, [self._grid._cells[coord.y][coord.x].num()]):
                steps_taken = True
        return steps_taken
    def _check_single_cell_cols(self) -> bool:
        """check for cols with single cell left"""
        steps_taken = False
        coord_list: list[list[Position]] = self._grid.get_coords_for_cols_with_only_n_space(1)
        for coords in coord_list:
            y_str = ",".join([str(c.y) for c in coords])
            coord = coords[0]
            colour_id = self._grid._cells[coord.y][coord.x].num()
            print_colour(colour_id, f"col {coord.x} has space at {y_str}")
            self._set_cat(coord.x, coord.y)
            if self._cross_colour(coord.x, coord.y):
                steps_taken = True
            if self._cross_around(coord.x, coord.y):
                steps_taken = True
            if self._cross_row(coord.x, coord.y, [self._grid._cells[coord.y][coord.x].num()]):
                steps_taken = True
            if self._cross_col(coord.x, coord.y, [self._grid._cells[coord.y][coord.x].num()]):
                steps_taken = True
        return steps_taken
    def check_grid(self) -> bool:
        """Check the grid"""
        steps_taken = False

        if not steps_taken and self._check_for_cats():
            steps_taken = True
        if not steps_taken and self._check_for_single_cell_colours():
            steps_taken = True
        if not steps_taken and self._check_for_colours_1_wide():
            steps_taken = True
        if not steps_taken and self._check_for_2_colours_2_wide():
            steps_taken = True
        if not steps_taken and self._check_for_consistent_exclusions():
            steps_taken = True
        if not steps_taken and self._check_impossible_rows_3():
            steps_taken = True
        if not steps_taken and self._check_impossible_cols_3():
            steps_taken = True
        if not steps_taken and self._check_impossible_rows_2():
            steps_taken = True
        if not steps_taken and self._check_impossible_cols_2():
            steps_taken = True
        if not steps_taken and self._check_single_cell_rows():
            steps_taken = True
        if not steps_taken and self._check_single_cell_cols():
            steps_taken = True
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
            pygame.draw.line(self._display_surf, COL_WHITE, (left,top), (left+width,top+height), CROSS_THICKNESS)
            pygame.draw.line(self._display_surf, COL_WHITE, (left,top+height), (left+width,top), CROSS_THICKNESS)

        if cell._cat is True:
            pygame.draw.circle(self._display_surf, COL_WHITE, (left+(width/2), top+(height/2)), CELL_WIDTH/2, CAT_THICKNESS)

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
