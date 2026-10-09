"""Represents a meowdoku grid"""

class Grid:
    """Represents the meowdoku grid"""
    def __init__(self, data) -> None:
        self._cells = []
        for row in range(len(data)): # pylint: disable=consider-using-enumerate
            if len(data) != len(data[row]):
                raise Exception(f"{len(data)} rows but row {row} has {len(data[row])} columns")
        for row in range(len(data)): # pylint: disable=consider-using-enumerate
            self._cells.append([])
            for col in range(len(data[row])):
                self._cells[row].append(Cell(data[row][col]))
    def get_all_colours(self) -> dict:
        """Get a dictionary of the colours with the coordinates"""
        colours = {}
        for y in range(len(self._cells)): # pylint: disable=consider-using-enumerate
            for x in range(len(self._cells[y])):
                cell = self._cells[y][x]
                if cell.num() not in colours:
                    colours[cell.num()] = []
                colours[cell.num()].append((y, x))
        return colours
    def get_available_colours(self) -> dict:
        """Get a dictionary of the available colours with the coordinates"""
        filtered = {}
        for y in range(len(self._cells)): # pylint: disable=consider-using-enumerate
            for x in range(len(self._cells[y])):
                cell = self._cells[y][x]
                if cell.is_cross() is False and cell.is_cat() is False:
                    if cell.num() not in filtered:
                        filtered[cell.num()] = []
                    filtered[cell.num()].append((y, x))
        return filtered

class Cell:
    """Represents the meowdoku cell"""
    def __init__(self, num: int) -> None:
        self._num = num
        self._cat = False
        self._cross = False
    def is_cross(self) -> bool:
        """Gets a value indicating if the cell is crossed out"""
        return self._cross
    def is_cat(self) -> bool:
        """Gets a value indicating if the cell is a cat"""
        return self._cat
    def num(self) -> int:
        """Gets the cell number"""
        return self._num