"""Represents a meowdoku grid"""

class Grid:
    """Represents the meowdoku grid"""
    def __init__(self, data) -> None:
        self._cells = []
        for row in range(len(data)):
            if len(data) != len(data[row]):
                raise Exception(f"{len(data)} rows but row {row} has {len(data[row])} columns")
        for row in range(len(data)):
            self._cells.append([])
            for col in range(len(data[row])):
                self._cells[row].append(Cell(data[row][col]))

class Cell:
    """Represents the meowdoku cell"""
    def __init__(self, num: int) -> None:
        self._num = num
        self._cat = False
        self._cross = False