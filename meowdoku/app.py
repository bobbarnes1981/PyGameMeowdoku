"""Solve meowdoku"""

import logging
import time
import pygame
from meowdoku import Solver, colours

CELL_THICKNESS = 3
GRID_THICKNESS = 3
CROSS_THICKNESS = 6
CAT_THICKNESS = 6

CELL_WIDTH = 40
CELL_HEIGHT = 40

COL_WHITE = (255,255,255)

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

class App:
    """Represents the pygame application."""
    def __init__(self, data, delay: float) -> None:
        self._delay: float = delay
        self._solver = Solver(data)
        self._font_s = None
        self._font_l = None
        self._running = True
        self._display_surf = None
        self._time = time.time()
        self._counter = 0
        self._paused = False
        self._complete = False

    def is_complete(self) -> bool:
        """Check if is complete"""
        return self._complete

    def on_init(self) -> bool:
        """Initialise solver."""
        pygame.init()
        pygame.display.set_caption("Meowdoku")
        size = (get_width(self._solver._grid._col_count), get_height(self._solver._grid._row_count))
        self._display_surf = pygame.display.set_mode(size, pygame.HWSURFACE | pygame.DOUBLEBUF)
        font_name = pygame.font.get_default_font()
        logging.info("System font: %s", font_name)
        self._font_s = pygame.font.SysFont(None, 22)
        self._font_l = pygame.font.SysFont(None, 66)
        return True
    def on_event(self, event: pygame.event.Event) -> None:
        """Process the pygame events."""
        if event.type == pygame.QUIT:
            self._running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == 27: # ESC
                self._running = False
            elif event.key == 112: # 'P'
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
                if self._paused is False and self._solver.check_grid():
                    self._complete = True
    def on_render(self) -> None:
        """Render the game."""
        self._display_surf.fill(COL_WHITE)
        self._draw_cells()
        pygame.display.update()
    def _draw_cells(self) -> None:
        """Draw all the cells."""
        for row in range(0, self._solver._grid._row_count):
            for col in range(0, self._solver._grid._col_count):
                self._draw_cell(row, col)
    def _draw_cell(self, row: int, col: int) -> None:
        """Draw a single cell for (row, col)."""
        cell = self._solver._grid._cells[row][col]
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
