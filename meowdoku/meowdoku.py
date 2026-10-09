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
    def get_cat_locations(self) -> dict[int, Position]:
        """Get a dictionary of the locations with a cat indexed by colour_id"""
        locations: dict[int, Position] = {}
        for y in range(len(self._cells)): # pylint: disable=consider-using-enumerate
            for x in range(len(self._cells[y])):
                cell = self._cells[y][x]
                if cell.is_cat():
                    locations[cell.num()] = Position(x, y)
        return locations
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
    def get_coords_for_rows_with_only_n_space(self, n: int) -> list[list[Position]]:
        """Get a list of coords for each row that has only n contiguous spaces left"""
        coord_list: list[list[Position]] = []
        for y in range(len(self._cells)): # pylint: disable=consider-using-enumerate
            spaces: list[list[int]] = []
            restart = True
            for x in range(len(self._cells[y])):
                cell = self._cells[y][x]
                if cell.is_cat() is False and cell.is_cross() is False:
                    if restart is True:
                        spaces.append([])
                        restart = False
                    spaces[-1].append(x)
                else:
                    restart = True
            if len(spaces) == 1 and len(spaces[0]) == n:
                coords = []
                for space in spaces[0]:
                    coords.append(Position(space, y))
                coord_list.append(coords)
        return coord_list
    def get_coords_for_cols_with_only_n_space(self, n: int) -> list[list[Position]]:
        """Get a list of coords for each col that has only n contiguous spaces left"""
        coord_list: list[list[Position]] = []
        for x in range(len(self._cells[0])):
            spaces: list[list[int]] = []
            restart = True
            for y in range(len(self._cells)): # pylint: disable=consider-using-enumerate
                cell = self._cells[y][x]
                if cell.is_cat() is False and cell.is_cross() is False:
                    if restart is True:
                        spaces.append([])
                        restart = False
                    spaces[-1].append(y)
                else:
                    restart = True
            if len(spaces) == 1 and len(spaces[0]) == n:
                coords = []
                for space in spaces[0]:
                    coords.append(Position(x, space))
                coord_list.append(coords)
        return coord_list

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
