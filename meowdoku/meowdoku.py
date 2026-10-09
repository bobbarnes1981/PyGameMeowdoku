"""Represents a meowdoku grid"""

class Position:
    """Represents a cell location"""
    def __init__(self, x: int, y: int) -> None:
        self.x: int = x
        self.y: int = y
    def __eq__(self, other):
        if not isinstance(other, Position):
            return False
        return self.x == other.x and self.y == other.y
    def __hash__(self):
        return hash(f"{self.x}, {self.y}")

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
                colour_id = data[row][col]
                cat = False
                if colour_id > 100:
                    colour_id -= 100
                    cat = True
                self._cells[row].append(Cell(colour_id, cat))
    def get_colour_ids_with_cat(self) -> list[int]:
        """Get list of colour ids that have a cat"""
        colour_ids: list[int] = []
        for y in range(len(self._cells)): # pylint: disable=consider-using-enumerate
            for x in range(len(self._cells[y])):
                cell = self._cells[y][x]
                if cell.num() not in colour_ids and cell.is_cat():
                    colour_ids.append(cell.num())
        return colour_ids
    def get_all_coords(self) -> dict[int, list[Position]]:
        """Get dictionary of coords indexed by colour_id"""
        coords: dict[int, list[Position]] = {}
        for y in range(len(self._cells)): # pylint: disable=consider-using-enumerate
            for x in range(len(self._cells[y])):
                cell = self._cells[y][x]
                if cell.num() not in coords:
                    coords[cell.num()] = []
                coords[cell.num()].append(Position(x, y))
        return coords
    def get_available_coords(self, colours_ids: list[int] = None) -> dict[int, list[Position]]:
        """Get dictionary of coords that are not cat or cross, optionally filtered by colour_ids"""
        coords: dict[int, list[Position]] = {}
        for y in range(len(self._cells)): # pylint: disable=consider-using-enumerate
            for x in range(len(self._cells[y])):
                cell = self._cells[y][x]
                if colours_ids is None or cell.num() in colours_ids:
                    if cell.is_cross() is False and cell.is_cat() is False:
                        if cell.num() not in coords:
                            coords[cell.num()] = []
                        coords[cell.num()].append(Position(x, y))
        return coords

class Cell:
    """Represents the meowdoku cell"""
    def __init__(self, num: int, cat: bool) -> None:
        self._num = num
        self._cat = cat
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
